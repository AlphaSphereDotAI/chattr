from pydantic.dataclasses import Field, dataclass

from chattr.character.base import Character


@dataclass(frozen=True)
class DocQA(Character):
    name: str = Field("DocQA", description="The name of the character")
    description: str = Field(
        "DocQA is a helpful assistant that can answer questions about the documents.",
        description="The description of the character",
    )
    instructions: list[str] = Field(
        [
            "You are DocQA, a helpful assistant that can answer questions about given documents.",
            "You can use the tools provided to you to answer questions.",
        ],
        description="The instructions for the character",
    )
