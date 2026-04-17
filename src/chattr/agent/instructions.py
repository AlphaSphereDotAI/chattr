from sys import exit as sys_exit

from agno.tools.mcp import MultiMCPTools
from agno.utils.log import log_error


def setup_instructions(character: str | None, tools: list[MultiMCPTools | None]) -> list[str]:
    """Return a list of instructions to mimic a given character."""
    if not character:
        log_error("`character` must be provided.")
        sys_exit(1)
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
                        "Generate video from the resulting audio using the appropriate Tool.",
                    )
    return instructions
