from json import loads

from agno.tools.mcp import MultiMCPTools
from agno.utils.log import log_info, log_warning

from chattr.app.settings import MCPSettings


def setup_mcp_tools(mcp: MCPSettings) -> MultiMCPTools | None:
    """Return and setup MCP tools connection."""
    if not mcp.path.exists():
        log_warning("MCP config file not found.")
        return None
    mcp_servers: list[dict] = loads(mcp.path.read_text()).get("mcp_servers", [])
    url_servers: list[dict] = [
        m for m in mcp_servers if m.get("transport") in ("sse", "streamable-http")
    ]
    if not url_servers:
        log_info("No Remote MCP servers found.")
        return None
    mcp_tools = MultiMCPTools(
        urls=[m["url"] for m in url_servers],
        urls_transports=[m["transport"] for m in url_servers],
        refresh_connection=True,
    )
    log_info(f"MCP servers: {len(mcp_tools.tools)}")
    return mcp_tools
