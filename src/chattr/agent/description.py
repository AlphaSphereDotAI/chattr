from textwrap import dedent

from agno.utils.log import log_error


def setup_description(character: str | None) -> str:
    if not character:
        _msg = "Character name is required."
        log_error(_msg)
        raise ValueError(_msg)
    return dedent(
        f"""
        You are a helpful assistant
        who can act and mimic {character}'s character
        and answer questions about the era.
        """,
    )
