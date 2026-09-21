from pathlib import Path
from typing import Self

from pydantic import BaseModel, Field, FilePath, model_validator

from chattr.app.scheme import MCPScheme


class MCPSettings(BaseModel):
    """Settings for MCP configuration."""

    path: FilePath = Field(default_factory=lambda: Path.cwd() / "mcp.json")

    @model_validator(mode="after")
    def is_valid(self) -> Self:
        """Validate that the MCP config file is a valid JSON file."""
        if self.path:
            if self.path.suffix != ".json":
                msg = "MCP config file must be a JSON file"
                raise ValueError(msg)
            if self.path.stem != "mcp":
                msg = "MCP config file must be named 'mcp.json'"
                raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def is_valid_scheme(self) -> Self:
        """Validate that the MCP config file has a valid scheme."""
        if self.path and self.path.exists():
            _ = MCPScheme.model_validate_json(self.path.read_text())
        return self
