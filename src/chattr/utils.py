from pathlib import Path
from typing import Optional

from pydantic import HttpUrl, ValidationError


def is_url(value: Optional[str]) -> bool:
    """
    Check if a string is a valid URL.
    
    Args:
        value: The string to check. Can be None.
        
    Returns:
        bool: True if the string is a valid URL, False otherwise or if None.
    """
    if value is None:
        return False
    
    try:
        HttpUrl(value)
        return True
    except ValidationError:
        return False


def download(url: HttpUrl, path: Path) -> None:
    """
    Download a file from a URL and save it to a local path.

    Args:
        url: The URL to download the file from.
        path: The local file path where the downloaded file will be saved.

    Returns:
        None
    """
    import requests
    response = requests.get(url, stream=True)
    with open(path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
