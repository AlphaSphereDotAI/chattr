from textwrap import dedent


def setup_description(character: str | None) -> str:
    if not character:
        raise ParameterMissingError("Character name", "CHARACTER__NAME")
    return dedent(
        f"""
        You are a helpful assistant
        who can act and mimic {character}'s character
        and answer questions about the era.
        """,
    )
