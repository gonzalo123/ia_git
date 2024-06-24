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
