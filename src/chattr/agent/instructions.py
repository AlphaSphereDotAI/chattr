from agno.tools.mcp import MultiMCPTools
from agno.utils.log import log_error


def setup_instructions(character: str | None, tools: list[MultiMCPTools | None]) -> list[str]:
    if not character:
        _msg = "Character name is required."
        log_error(_msg)
        raise ValueError(_msg)
    """Return a list of instructions to mimic a given character."""
    instructions: list[str] = [
        "Understand the user's question and context.",
        "Gather relevant information and resources.",
        f"Formulate a clear and concise response in {character}'s voice.",
    ]
    for tool in tools:
        if isinstance(tool, MultiMCPTools):
            for key in tool.functions:
                if tool.functions[key].name == "generate_audio_for_text":
                    instructions.append(
                        "Generate audio from the formulated response using the appropriate Tool.",
                    )
                if tool.functions[key].name == "generate_video_mcp":
                    instructions.append(
                        "Generate video from the resulted audio using the appropriate Tool.",
                    )
    return instructions
