from commands.audit_now import run as audit_now
from commands.audit_between_commits import run as audit_between_commits
from commands.commit_message import run as commit_message
from lib.cli import cli

cli.add_command(cmd=audit_now, name='audit_now')
cli.add_command(cmd=commit_message, name='commit_message')
cli.add_command(cmd=audit_between_commits, name='audit_between_commits')

if __name__ == "__main__":
    cli()
