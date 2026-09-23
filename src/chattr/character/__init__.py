from pydantic.dataclasses import Field, dataclass

from chattr.character.napoleon_bonaparte import NapoleonBonaparte

__all__ = ["NapoleonBonaparte"]


@dataclass(frozen=True)
class Character:
    name: str = Field(description="The name of the character")
    description: str = Field(description="The description of the character")
    instructions: list[str] = Field(description="The instructions for the character")
