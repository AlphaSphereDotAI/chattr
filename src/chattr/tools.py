from typing import Literal

from langchain_core.tools import tool


@tool
def get_weather(city: Literal["nyc", "sf"]) -> str:
    """
    Returns a weather description for the specified city.

    Parameters:
        city (Literal["nyc", "sf"]): The city for which to retrieve weather information.

    Returns:
        str: A message describing the weather in the specified city.

    Raises:
        AssertionError: If the city is not "nyc" or "sf".
    """
    if city == "nyc":
        return "It might be cloudy in nyc"
    elif city == "sf":
        return "It's always sunny in sf"
    else:
        raise AssertionError("Unknown city")
