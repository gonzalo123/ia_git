import click
from rich.console import Console
from rich.markdown import Markdown

from lib.chains.git import get_chain
from lib.chains.git.chain import Score
from lib.git_utils import get_diff
from lib.llm.azure import llm


@click.command()
@click.option('--path', required=False, help='git dir path')
@click.option('--commit1', required=False, help='commit from')
@click.option('--commit2', required=False, help='commit to')
def run(path: str, commit1: str, commit2: str):
    current_diff = get_diff(path, commit1, commit2)
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

    # click.echo(ia_response)
    console = Console()
    md = Markdown(ia_response)
    console.print(md)

    click.echo('')
    if status == Score.CRITICAL:
        click.echo('[WARNING] Critical issues found.')
    else:
        click.echo('No critical issues found.')
