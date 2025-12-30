from textwrap import dedent

from chattr.app.logger import logger


def setup_description(character: str | None) -> str:
    if not character:
        _msg = "Character name is required."
        logger.error(_msg)
        raise ValueError(_msg)
    return dedent(
        f"""
        You are a helpful assistant
        who can act and mimic {character}'s character
        and answer questions about the era.
        """,
    )
