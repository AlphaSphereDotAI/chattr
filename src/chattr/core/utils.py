from pathlib import Path

from agno.utils.log import log_info
from httpx import URL, Client, HTTPStatusError, RequestError, Response
from pydantic import HttpUrl, ValidationError

VALID_STATUS_CODE = 200


def is_url(value: str | None) -> bool:
    """
    Check if a string is a valid URL.

    Args:
        value: The string to check. Can be None.

    Returns:
        bool: True if the string is a valid URL, False otherwise.
    """
    if value is None:
        return False

    try:
        _ = HttpUrl(value)
    except ValidationError:
        return False
    return True


def is_alive(url: HttpUrl) -> bool:
    """
    Check if a given URL is accessible and returns its availability status.

    Args:
        url (HttpUrl): The URL to check for accessibility.

    Returns:
        bool: True if the URL is accessible with a valid status code, otherwise False.
    """
    try:
        with Client() as client:
            response: Response = client.get(str(url))
            return response.status_code == VALID_STATUS_CODE
    except (RequestError, HTTPStatusError):
        return False


def download_file(url: URL, path: Path, timeout: float = 30.0) -> None:
    """
    Download a file from a URL and save it to a local path using streaming.

    Args:
        url (URL): The URL to download the file from.
        path (Path): The local file path where the downloaded file will be saved.
        timeout (float): Request timeout in seconds. Defaults to 30.0.

    Returns:
        None
    """
    log_info(f"Downloading {url} to {path}")
    with Client(timeout=timeout) as client:
        with client.stream("GET", url) as response:
            response.raise_for_status()
            with path.open("wb") as f:
                f.writelines(response.iter_bytes())
    log_info(f"Downloaded {url} to {path}")
