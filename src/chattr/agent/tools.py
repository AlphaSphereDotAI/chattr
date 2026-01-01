from json import loads

from agno.tools.mcp import MultiMCPTools
from rich.pretty import pprint

from chattr.app.logger import logger
from chattr.app.settings import MCPSettings


async def setup_mcp_tools(mcp: MCPSettings) -> MultiMCPTools | None:
    """Return and setup MCP tools connection."""
    if not mcp.path.exists():
        logger.warning("MCP config file not found.")
        return None
    mcp_servers: list[dict] = loads(settings.mcp.path.read_text()).get("mcp_servers", [])
    url_servers: list[dict] = [m for m in mcp_servers if m.get("type") == "url"]
    pprint(url_servers)
    if not url_servers:
        logger.info("No Remote MCP servers found.")
        return None
    mcp_tools = MultiMCPTools(
        urls=[m["url"] for m in url_servers],
        urls_transports=[m["transport"] for m in url_servers],
        allow_partial_failure=True,
    )
    logger.info(f"MCP servers: {len(mcp_tools.tools)}")
    if not mcp_tools.tools or len(mcp_tools.tools) == 0:
        logger.info("No MCP servers available.")
        return None
    await mcp_tools.connect()
    return mcp_tools


async def close_mcp_tools(mcp_tools: MultiMCPTools | None) -> None:
    """Close the MCP tools connection."""
    logger.info("Closing MCP tools...")
    if not mcp_tools:
        return
    await mcp_tools.close()
