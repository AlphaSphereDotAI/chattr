"""Base persona model for Chattr characters."""

from pydantic.dataclasses import Field, dataclass


@dataclass(frozen=True)
class Character:
    """A persona the agent can adopt."""

    name: str = Field(description="The name of the character")
    description: str = Field(description="The description of the character")
    instructions: list[str] = Field(description="The instructions for the character")
