class ChattrError(Exception):
    """Base exception for the Chattr application."""


class ConfigurationError(ChattrError):
    """Raised when there is an issue with the application settings."""


class ModelConfigurationError(ConfigurationError):
    """Raised when model-specific settings are missing or invalid."""


class ParameterMissingError(ChattrError):
    """Exception raised for missing parameters."""


class CharacterNameMissingError(ParameterMissingError):
    """Exception raised when the character name is missing."""

    def __init__(self) -> None:
        super().__init__("Character name is missing. Set it with `CHARACTER__NAME`")
