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
