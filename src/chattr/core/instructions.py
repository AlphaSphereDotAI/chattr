from agno.tools.mcp import MCPTools


def setup_instructions(tools: list[MCPTools] | None) -> list[str]:
    """Return a list of instructions to use the tools."""
    instructions: list[str] = [
        "Understand the user's question and context.",
        "Gather relevant information and resources.",
        "Formulate a clear and concise response.",
    ]
    if tools:
        for tool in tools:
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
