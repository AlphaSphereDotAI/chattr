from json import loads

from agno.tools.mcp import MultiMCPTools
from rich.pretty import pprint

from chattr.app.logger import logger
from chattr.app.settings import Settings


async def setup_mcp_tools(settings: Settings) -> MultiMCPTools | None:
    """Return and setup MCP tools connection."""
    if not settings.mcp.path.exists():
        return None
    mcp_servers: list[dict] = loads(settings.mcp.path.read_text()).get("mcp_servers", [])
    url_servers: list[dict] = [m for m in mcp_servers if m.get("type") == "url"]
    pprint(url_servers)
    if not url_servers:
        return None
    mcp_tools = MultiMCPTools(
        urls=[m["url"] for m in url_servers],
        urls_transports=[m["transport"] for m in url_servers],
        allow_partial_failure=True,
    )
    logger.info(f"MCP servers: {len(mcp_tools.tools)}")
    await mcp_tools.connect()
    return mcp_tools


async def close_mcp_tools(mcp_tools: MultiMCPTools | None) -> None:
    """Close the MCP tools connection."""
    logger.info("Closing MCP tools...")
    if not mcp_tools:
        return
    await mcp_tools.close()
