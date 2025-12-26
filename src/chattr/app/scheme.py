"""Module defining MCP connection scheme configurations."""
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    ValidationError,
)

from chattr.app.logger import logger


class CommandConnection(BaseModel):
    """MCP connection variant using a shell command."""

    model_config = ConfigDict(extra="forbid")
    name: str = Field(..., description="Name of the MCP server instance")
    type: Literal["command"]
    command: str = Field(..., description="Executable command to start MCP server")
    args: list[str] | None = Field(default=None)
    transport: Literal["stdio"] = Field("stdio")


class URLConnection(BaseModel):
    """MCP connection variant using a URL endpoint."""

    model_config = ConfigDict(extra="forbid")
    name: str = Field(..., description="Name of the MCP server instance")
    type: Literal["url"]
    url: HttpUrl = Field(..., description="URL of the MCP server endpoint")
    transport: Literal["sse", "streamable-http"] = Field(...)


class MCPScheme(BaseModel):
    """Model representing the MCP scheme configuration."""

    model_config = ConfigDict(extra="forbid")
    mcp_servers: list[
        Annotated[CommandConnection | URLConnection, Field(discriminator="type")]
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
        logger.error("Validation error: %s", e)

    # Additional validation examples can be added here if needed.
