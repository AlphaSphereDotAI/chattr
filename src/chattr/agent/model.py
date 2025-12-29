from agno.models.openai.like import OpenAILike

from chattr.app.logger import logger
from chattr.app.settings import Settings
from chattr.app.utils import is_url


def setup_model(settings: Settings) -> OpenAILike:
    """
    Initialize the ChatOpenAI language model using the provided settings.

    This method creates and returns a ChatOpenAI instance configured with
    the model's URL, name, API key, and temperature.

    Returns:
        ChatOpenAI: The initialized ChatOpenAI language model instance.
    """
    if not settings.model.url:
        _msg = "Model URL is missing. Set it with `MODEL__URL`"
        logger.error(_msg)
        raise ValueError(_msg)
    if not is_url(str(settings.model.url)):
        _msg = "Model URL is invalid. Set it with `MODEL__URL`"
        logger.error(_msg)
        raise ValueError(_msg)
    if not settings.model.name:
        _msg = "Model name is missing. Set it with `MODEL__NAME`"
        logger.error(_msg)
        raise ValueError(_msg)
    if not settings.model.api_key:
        _msg = "API key is missing. Set it with `MODEL__API_KEY`"
        logger.error(_msg)
        raise ValueError(_msg)
    return OpenAILike(
        base_url=str(settings.model.url),
        id=settings.model.name,
        api_key=settings.model.api_key.get_secret_value(),
        temperature=settings.model.temperature,
        cache_response=True,
    )
