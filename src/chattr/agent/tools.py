from agno.tools.mcp import MCPTools
from agno.utils.log import log_info

from chattr.settings.mcp import (
    ExtraMCPServer,
    VideoGeneratorMCPServer,
    VoiceGeneratorMCPServer,
)


def setup_mcp_tools(
    mcps: list[VoiceGeneratorMCPServer | VideoGeneratorMCPServer | ExtraMCPServer],
) -> list[MCPTools] | None:
    """Return and setup MCP tools connection."""
    if not mcps:
        log_info("No Remote MCP servers found.")
        return None
    return [
        MCPTools(
            server_params=mcp,
            transport="streamable-http",
            refresh_connection=True,
        )
        for mcp in mcps
    ]
