from pathlib import Path

from httpx import URL, Client, HTTPStatusError, RequestError
from pydantic import HttpUrl, ValidationError

from chattr.app.logger import logger

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
            response = client.get(str(url))
            return response.status_code == VALID_STATUS_CODE
    except (RequestError, HTTPStatusError):
        return False


def download_file(url: URL, path: Path) -> None:
    """
    Download a file from a URL and save it to a local path.

    Args:
        url: The URL to download the file from.
        path: The local file path where the downloaded file will be saved.

    Returns:
        None
    """
    logger.info(f"Downloading {url} to {path}")
    with Client() as client:
        response = client.get(url)
        response.raise_for_status()
        path.write_bytes(response.content)
    logger.info(f"Downloaded {url} to {path}")


# def _download_audio(url: URL) -> Path:
#     """
#     Download an audio file from a given URL and save it as a temporary WAV file.
#
#     Args:
#         url (URL): The URL to download the audio from.
#
#     Returns:
#         Path: The path to the downloaded temporary audio file.
#
#     Raises:
#         Error: If the download fails due to network or file errors.
#     """
#     try:
#         with Client() as client:
#             response = client.get(url)
#             response.raise_for_status()
#             with NamedTemporaryFile(delete=False, suffix=".wav") as f:
#                 f.write(response.content)
#                 audio_path = Path(f.name)
#             logger.info(f"Downloaded audio to {audio_path}")
#     except (RequestError, HTTPStatusError, OSError) as e:
#         msg = f"Failed to download audio from {url}: {e}"
#         logger.error(msg)
#         raise Error(msg) from e
#     return audio_path
