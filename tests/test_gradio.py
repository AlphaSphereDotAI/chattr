from gradio_client import Client


def test_gradio():
    client = Client("http://localhost:7860")
    result = client.predict(
        message="Generate an audio from text of 'hello world'",
        history=[],
        api_name="/generate_response",
    )
    print(result)
    assert result is not None
