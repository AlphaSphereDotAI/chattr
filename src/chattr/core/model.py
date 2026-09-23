from agno.models.openai.like import OpenAILike
from agno.utils.log import log_info
from pydantic import HttpUrl, ValidationError

from chattr.settings import ModelSettings


def setup_model(model: ModelSettings) -> OpenAILike:
    """
    Initialize the OpenAILike language model using the provided settings.

    This method creates and returns an OpenAILike instance configured with
    the model's URL, name, API key, and temperature.

    Returns:
        OpenAILike: The initialized OpenAILike language model instance.
    """
    if not model.url:
        _msg = "Model URL is missing. Set it with `MODEL__URL`"
        raise ValueError(_msg)
    try:
        _ = HttpUrl(model.url.encoded_string())
    except ValidationError:
        _msg = "Model URL is invalid. Set it with `MODEL__URL`"
        raise ValueError(_msg)
    if not model.name:
        _msg = "Model name is missing. Set it with `MODEL__NAME`"
        raise ValueError(_msg)
    if not model.api_key:
        _msg = "API key is missing. Set it with `MODEL__API_KEY`"
        raise ValueError(_msg)
    log_info("Initializing OpenAILike language model")
    return OpenAILike(
        base_url=model.url.encoded_string(),
        id=model.name,
        api_key=model.api_key.get_secret_value(),
        temperature=model.temperature,
        cache_response=model.cache_response,
    )
