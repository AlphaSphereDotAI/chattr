from pathlib import Path
from typing import Self

from agno.utils.log import log_error, log_info
from pydantic import BaseModel, DirectoryPath, Field, computed_field, model_validator


class DirectorySettings(BaseModel):
    """Settings for application directories."""

    base: DirectoryPath = Field(default_factory=Path.cwd, frozen=True)

    @computed_field
    @property
    def assets(self) -> DirectoryPath:
        """Path to the assets directory."""
        return self.base / "assets"

    @computed_field
    @property
    def audio(self) -> DirectoryPath:
        """Path to the audio directory."""
        return self.assets / "audio"

    @computed_field
    @property
    def video(self) -> DirectoryPath:
        """Path to the video directory."""
        return self.assets / "video"

    @computed_field
    @property
    def prompts(self) -> DirectoryPath:
        """Path to the prompts directory."""
        return self.assets / "prompts"

    @model_validator(mode="after")
    def create_missing_dirs(self) -> Self:
        """
        Ensure that all specified directories exist, creating them if necessary.

        Checks and creates any missing directories defined in the `DirectorySettings`.

        Returns:
            Self: The validated DirectorySettings instance.
        """
        for directory in [self.base, self.assets, self.audio, self.video, self.prompts]:
            if not directory.exists():
                try:
                    directory.mkdir(parents=True, exist_ok=True)
                    log_info(f"Created directory {directory}.")
                except OSError as e:
                    log_error(f"Error creating directory {directory}: {e}")
                    raise
        return self
