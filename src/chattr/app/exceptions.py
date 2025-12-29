class ParameterMissingError(ValueError):
    """Exception raised for missing parameters."""

    def __init__(self, parameter: str, environment_variable: str) -> None:
        super().__init__(f"{parameter} is missing. Set it with `{environment_variable}`")


class ChattrError(Exception):
    """Base exception for the Chattr application."""


class ConfigurationError(ChattrError):
    """Raised when there is an issue with the application settings."""


class ModelConfigurationError(ConfigurationError):
    """Raised when model-specific settings are missing or invalid."""
