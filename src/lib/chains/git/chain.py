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
