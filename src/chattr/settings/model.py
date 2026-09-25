from typing import Self

from pydantic import BaseModel, Field, HttpUrl, SecretStr, model_validator


class ModelSettings(BaseModel):
    """Settings related to model execution."""

    url: HttpUrl | None = Field(default=None)
    name: str | None = Field(default=None)
    api_key: SecretStr | None = Field(default=None)
    temperature: float = Field(default=0.0, ge=0.0, le=1.0)
    cache_response: bool = Field(default=True)
    search: bool = Field(default=True)
    url_context: bool = Field(default=True)
    response_modalities: list[str] = Field(default=["TEXT", "AUDIO"])
    thinking_level: Literal["low", "high"] | None = Field(default=None)

    @model_validator(mode="after")
    def check_param_exist(self) -> Self:
        """Validate the existence of required credentials for the model provider."""
        if self.url:
            if not self.api_key or not self.api_key.get_secret_value():
                _msg: str = "You need to provide API Key for the Model provider: Set via `MODEL__API_KEY`"
                raise ValueError(_msg)
            if not self.name:
                _msg: str = "You need to provide Model name for the Model provider: Set via `MODEL__NAME`"
                raise ValueError(_msg)
        return self
