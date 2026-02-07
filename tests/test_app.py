"""Tests for the application's HTTP endpoints."""

from os import getenv

from requests import Response, head

HTTP_SUCCESS_CODE = 200


def test_app() -> None:
    """
    Test the reachability of Chattr.

    Returns:
        None
    """
    response: Response = head(
        getenv("CHATTR_URL", "http://localhost:7860/"), timeout=30
    )
    assert response.status_code == HTTP_SUCCESS_CODE
