# Leveraging AI to perform Code Audits based on Git Commit Diff with Python and LangChain

A few days ago, I came across a project on GitHub by my friend Jordi called [Commitia](https://github.com/heedrox/commitia). Commitia is a simple command line tool that helps you write commit messages. It works by passing a git diff to an LLM model, which then suggests a commit message based on the diff. I liked the idea of using LLM models to assist in the development process by interacting with git diffs. So, I decided to create a similar tool using Python and LangChain, just for practice. I'll use Click to create the command line interface and LangChain to interact with the LLM model. I'll use Azure LLM, but any LLM model that supports custom functions, like Groq LLM or OpenAI, can be used.

```python
import click

from lib.chains.git import get_chain
from lib.git_utils import get_current_diff
from lib.llm.azure import llm
from settings import BASE_DIR


@click.command()
def run():
    current_diff = get_current_diff(BASE_DIR / '..')
    chain = get_chain(llm)
    ia_response = chain.get_commit_message(current_diff)
    click.echo(ia_response)
```

That's the chain

```python
import logging

from langchain_core.messages import SystemMessage, HumanMessage

from lib.models import DiffData
from .prompts import PROMPT_COMMIT_MESSAGE

logger = logging.getLogger(__name__)


class GitChain:

    def __init__(self, llm):
        self.llm = llm
        self.prompt_commit_message = SystemMessage(content=PROMPT_COMMIT_MESSAGE)

    @staticmethod
    def _get_diff_content(diff: DiffData):
        return "\n".join((d.diff for d in diff.diffs))

    def get_commit_message(self, diff: DiffData):
        try:
            user_message = HumanMessage(content=self._get_diff_content(diff))
            messages = [self.prompt_commit_message, user_message]
            ai_msg = self.llm.invoke(messages)
            return ai_msg if isinstance(ai_msg, str) else ai_msg.content
        except Exception as e:
            logger.error(f"Error during question processing: {e}")
```
I'm going to use the same prompt that Jordi uses in Commitia.

```python
PROMPT_COMMIT_MESSAGE = """
You are an assistant to write the commit message.
The user will send you the content of the commit diff, and you will reply with the commit message.
It must be a commit message of one single line. Be concise, just write the message, do not give any explanation.
"""
```
To obtain the git diff I'm going to use gitpython library.

```python
from git.repo import Repo

from .models import Diff, DiffData, Status

def _get_file_mode(diff):
    if diff.new_file:
        return Status.CREATED
    elif diff.deleted_file:
        return Status.DELETED
    elif diff.copied_file:
        return Status.COPIED
    else:
        return Status.MODIFIED


    
def _build_diff_data(commit, diffs) -> DiffData:
    return DiffData(
        user=str(commit.author),
        date=commit.committed_datetime,
        diffs=[Diff(
            diff=str(diff),
            path=diff.b_path if diff.new_file else diff.a_path,
            status=_get_file_mode(diff)
        ) for diff in diffs]
    )

def get_current_diff(repo_path) -> DiffData:
    repo = Repo(repo_path)
    commit = repo.head.commit
    diffs = commit.diff(None, create_patch=True)

    return _build_diff_data(commit, diffs)
```

I'm using the following models to represent the data.


```python
from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel


class Status(str, Enum):
    CREATED = 'C'
    MODIFIED = 'M'
    DELETED = 'D'
    COPIED = 'C'


class Diff(BaseModel):
    diff: str
    path: str
    status: Status


class DiffData(BaseModel):
    user: str
    date: datetime
    diffs: List[Diff]
```

After this experiment cloning Commitia I'm going to do another experiment. Now the idea is create a code review of based on the git diff. I'm going to use the same structure of the previous experiment. I can only need to change the prompt.

```python
PROMPT_CODE_AUDIT = """
You are experience developer and need to perform a code review of a git diff.
You should identify potential errors, provide suggestions for improvement,
and highlight best practices in the provided code.

You should provide a global score of the code quality if you detect any issue based on the following criteria:
- NONE: 0.0
- LOW: Between 0.1 and 3.9
- MEDIUM: Between 4.0 and 6.9
- HIGH: Between 7.0 and 8.9
- CRITICAL Between 9.0 and 10.0

Your output should use the following template:
### Score
Global score of risks: [NONE, LOW, MEDIUM, HIGH, CRITICAL]

### Diff Explanation
First you must provide a brief explanation of the diff in a single line. Be concise and do not give any explanation.
Then you should provide a detailed explanation of the changes made in the diff.

### Audit summary
Detailed explanation of the identified gaps and their potential impact, if there are any significant findings.
"""
```

As you can see, I'm using a prompt to analyze the code and provide a score for its quality. I also want to perform actions based on the score, such as taking specific measures if the score is critical. To achieve this, we need to use a custom function. Therefore, we need an LLM model that supports calling custom functions. I added the audit_diff method to the chain to handle this.

```python
import logging
from enum import Enum

from langchain_core.messages import SystemMessage, HumanMessage

from lib.models import DiffData
from .prompts import PROMPT_CODE_AUDIT, PROMPT_COMMIT_MESSAGE

logger = logging.getLogger(__name__)


class Score(int, Enum):
    NONE = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


class GitChain:

    def __init__(self, llm, tools):
        self.llm = llm
        if hasattr(llm, 'bind_tools'):
            self.llm_with_tools = llm.bind_tools(list(tools.values()))
        else:
            logger.info("LLM does not support bind_tools method")
            self.llm_with_tools = llm
        self.prompt_code_audit = SystemMessage(content=PROMPT_CODE_AUDIT)
        self.prompt_commit_message = SystemMessage(content=PROMPT_COMMIT_MESSAGE)
        self.tools = tools

    @staticmethod
    def _get_diff_content(diff: DiffData):
        return "\n".join((d.diff for d in diff.diffs))

    def _get_status_from_message(self, message) -> Score | None:
        ai_msg = self.llm_with_tools.invoke([HumanMessage(content=message)])
        return self._get_tool_output(ai_msg)

    def get_commit_message(self, diff: DiffData):
        try:
            user_message = HumanMessage(content=self._get_diff_content(diff))
            messages = [self.prompt_commit_message, user_message]
            ai_msg = self.llm.invoke(messages)
            return ai_msg if isinstance(ai_msg, str) else ai_msg.content
        except Exception as e:
            logger.error(f"Error during question processing: {e}")

    def audit_diff(self, diff: DiffData):
        user_message = HumanMessage(content=self._get_diff_content(diff))
        try:
            ai_msg = self.llm.invoke([self.prompt_code_audit, user_message])
            output_message = ai_msg.content if not isinstance(ai_msg, str) else ai_msg

            return self._get_status_from_message(output_message), output_message
        except Exception as e:
            logger.error(f"Error during question processing: {e}")

    def _get_tool_output(self, ai_msg):
        status = None
        for tool_call in ai_msg.tool_calls:
            tool_output = self.tools[tool_call["name"]].invoke(tool_call["args"])
            logger.info(f"Tool: '{tool_call['name']}'")
            status = tool_output
        return status
```

The audit_diff method takes a DiffData object as an argument, which represents the differences in the code that need to be audited. The first line inside the method creates a HumanMessage object from the content of the DiffData object by calling the _get_diff_content method, which combines all the diffs into a single string. Next, the method invokes the LLM with a system message prompt for code auditing and the human message. The LLM's response is stored in ai_msg. If ai_msg is a string, it is used as is; otherwise, the content of ai_msg is used. The method then calls _get_status_from_message with output_message as the argument. This method invokes the LLM with tools using the output_message as input and gets the tool output. The method returns the tool output status and the output_message. In summary, the audit_diff method audits code differences using a Language Learning Model and a set of tools, and returns the audit status and the AI message content.

Now I can invoke the chain to audit the code and print the results. Also, I can use the score to perform an action.

```python
import click
from rich.console import Console
from rich.markdown import Markdown

from lib.chains.git import get_chain
from lib.chains.git.chain import Score
from lib.git_utils import get_current_diff
from lib.llm.azure import llm
from settings import BASE_DIR


@click.command()
def run():
    current_diff = get_current_diff(BASE_DIR / '..')
    chain = get_chain(llm)
    status, ia_response = chain.audit_diff(current_diff)

    click.echo('Audit results:')
    click.echo('--------------')
    click.echo(f"{current_diff.user} at {current_diff.date} made the following changes at:")
    click.echo('')
    click.echo('Affected files:')
    for diff in current_diff.diffs:
        print(f"[{diff.status.value}] {diff.path}")
    click.echo('')

    console = Console()
    console.print(Markdown(ia_response))

    click.echo('')
    if status == Score.CRITICAL:
        click.echo('[WARNING] Critical issues found.')
    else:
        click.echo('No critical issues found.')
```

In conclusion, integrating AI into the development workflow can significantly enhance productivity and code quality. 
By using tools like LangChain and LLM models, we can automate the generation of commit messages and perform detailed 
code audits based on git diffs. This not only saves time but also ensures consistency and accuracy in commit 
messages and code reviews. As we continue to explore and implement these AI-driven solutions, we open up new 
possibilities for more efficient and effective software development practices. It is not magic, it is just code.
