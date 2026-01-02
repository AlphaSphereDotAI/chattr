"""Module defining MCP connection scheme configurations."""

from typing import Annotated, Literal

from agno.tools.mcp import SSEClientParams, StreamableHTTPClientParams
from agno.utils.log import log_error
from mcp import StdioServerParameters
from pydantic import BaseModel, ConfigDict, Field, ValidationError


class CommandConnection(StdioServerParameters):
    """MCP connection variant using a shell command."""

    name: str = Field(..., description="Name of the MCP server instance")
    transport: Literal["stdio"] = Field("stdio")


class SSEConnection(BaseModel, SSEClientParams):
    """SSE connection variant using a URL endpoint."""

    name: str = Field(..., description="Name of the MCP server instance")
    transport: Literal["sse"] = Field("sse")


class StreamableHTTPConnection(BaseModel, StreamableHTTPClientParams):
    """MCP connection variant using a URL endpoint."""

    name: str = Field(..., description="Name of the MCP server instance")
    transport: Literal["streamable-http"] = Field("streamable-http")


class MCPScheme(BaseModel):
    """Model representing the MCP scheme configuration."""

    model_config = ConfigDict(extra="forbid")
    mcp_servers: list[
        Annotated[
            CommandConnection | SSEConnection | StreamableHTTPConnection,
            Field(discriminator="transport"),
        ]
    ] = Field(default_factory=list)


if __name__ == "__main__":
    from rich.pretty import pprint

    pprint(MCPScheme.model_json_schema())
    # Example instances
    ok1 = MCPScheme.model_validate(
        {
            "mcp_servers": [
                {
                    "name": "example_command_server",
                    "type": "command",
                    "command": "mcp-server",
                    "args": ["--port", "8080"],
                    "transport": "stdio",
                },
                {
                    "name": "example_url_server",
                    "type": "url",
                    "url": "https://example.com/mcp",
                    "transport": "sse",
                },
            ],
        },
    )
    pprint(ok1)

    # This will fail: missing the required key for the selected type
    try:
        MCPScheme.model_validate(
            {"mcp_servers": [{"type": "url", "command": "ls"}]},
        )
    except ValidationError as e:
        log_error(f"Validation error: {e}")

    # Additional validation examples can be added here if needed.
