from pydantic import BaseModel, Field


class CharacterSettings(BaseModel):
    """Settings related to character configuration."""

    name: str | None = Field(default=None)
