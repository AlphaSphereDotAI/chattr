from textwrap import dedent

from chattr.app.exceptions import CharacterNameMissingError


def setup_description(character: str | None) -> str:
    """Set up the description for the agent."""
    if not character:
        raise CharacterNameMissingError
    return dedent(
        f"""
        You are a helpful assistant
        who can act and mimic {character}'s character
        and answer questions about the era.
        """,
    )
