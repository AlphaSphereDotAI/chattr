from asyncio import CancelledError, run, wait_for

from agno.tools.mcp import MCPTools
from agno.utils.log import log_info, log_warning
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from chattr.settings import (
    ExtraMCPServerSettings,
    VideoGeneratorMCPServerSettings,
    VoiceGeneratorMCPServerSettings,
)

_INITIALIZE_TIMEOUT_SECONDS = 5.0

type MCPServerSettings = VoiceGeneratorMCPServerSettings | VideoGeneratorMCPServerSettings | ExtraMCPServerSettings


async def _is_server_reachable(server: MCPServerSettings) -> bool:
    """Return whether the MCP server completes the official handshake.

    Args:
        server: Remote MCP server to probe.

    Returns:
        True when the official MCP client can finish the handshake.
    """
    try:
        async with (
            streamable_http_client(str(server.url)) as (read, write, _),
            ClientSession(read, write) as session,
        ):
            await wait_for(
                session.initialize(),
                timeout=_INITIALIZE_TIMEOUT_SECONDS,
            )
        return True
    except KeyboardInterrupt, SystemExit:
        raise
    except Exception, CancelledError:  # noqa: BLE001
        return False


def setup_mcp_tools(mcps: list[MCPServerSettings]) -> list[MCPTools] | None:
    """Return MCP tools for servers that accept a connection.

    Servers that are not listening are skipped so application startup can
    continue without them. Restart the app after a skipped server comes up
    to attach its tools.

    Args:
        mcps: Configured remote MCP servers.

    Returns:
        One toolkit per reachable server, or None when none are reachable.
    """
    if not mcps:
        log_info("No Remote MCP servers found.")
        return None

    reachable: list[MCPServerSettings] = [mcp for mcp in mcps if run(_is_server_reachable(mcp))]
    not_reachable: list[MCPServerSettings] = [mcp for mcp in mcps if mcp not in reachable]
    
    if not_reachable:
        log_warning(f"MCP servers {not_reachable} are unreachable. Skipping.")
    if not reachable:
        log_info("No reachable Remote MCP servers found.")
        return None

    return [
        MCPTools(
            server_params=mcp,
            transport="streamable-http",
            refresh_connection=True,
        )
        for mcp in reachable
    ]
