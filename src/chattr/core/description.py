from sys import exit as sys_exit
from textwrap import dedent

from agno.utils.log import log_error


def setup_description(character: str | None) -> str:
    """Set up the description for the agent."""
    if not character:
        log_error("`character` must be provided.")
        sys_exit(1)
    return dedent(
        f"""
        You are a helpful assistant
        who can act and mimic {character}'s character
        and answer questions about the era.
        """,
    )
