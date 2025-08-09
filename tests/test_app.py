from requests import Response, head


def test_app() -> None:
    response: Response = head("http://localhost:7860/", timeout=30)
    assert response.status_code == 200
