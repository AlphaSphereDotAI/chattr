import json
from typing import Any

import gradio

from .agents.llm import get_response
from .settings import Settings, load_settings

global settings
settings: Settings = load_settings()

gradio.ChatInterface(
    fn=get_response,
    inputs=[
        gradio.Textbox(label="Query"),
        gradio.Dropdown(
            choices=["Alice", "Bob", "Charlie"],
            label="Character",
        ),
    ],
    outputs=[
        gradio.Textbox(label="Response"),
        gradio.Textbox(label="Time"),
    ],
    title="Character Chat",
    description="Chat with a character",
    theme="default",
    height=600,
    width=800,
)

gradio.launch()


# app = FastAPI(debug=True)


# @app.get(path="/")
# async def is_alive() -> dict[str, str]:
#     return {"message": "Chatacter is alive!", "status": "ok"}


# @app.get(path="/get_settings")
# def get_settings() -> Any:
#     return json.loads(s=settings.model_dump_json(indent=4))


# @app.get(path="/get_text")
# def get_text(query: str, character: str) -> JSONResponse:
#     res, time = get_response(query=query, character=character)
#     return JSONResponse(
#         content=res,
#         headers={"time": time},
#     )


# @app.get(path="/get_audio")
# def get_audio(text: str) -> FileResponse:
#     response_audio: Response = get(
#         url=f"{settings.host.voice_generator}get_audio?text={text}"
#     )
#     with open(file=settings.assets.audio, mode="wb") as f:
#         f.write(response_audio.content)
#     return FileResponse(
#         path=settings.assets.audio,
#         media_type="audio/wav",
#         filename="AUDIO.wav",
#     )


# @app.get(path="/get_video")
# def get_video(character: str) -> FileResponse:
#     send_audio: Response = post(
#         url=f"{settings.host.video_generator}set_audio",
#         files={"file": open(file=settings.assets.audio, mode="rb")},
#     )
#     print("Send Audio: ", send_audio.status_code == 200)
#     response_video: Response = get(
#         url=f"{settings.host.video_generator}get_video?character={character}"
#     )
#     with open(file=settings.assets.video, mode="wb") as f:
#         f.write(response_video.content)
#     return FileResponse(
#         path=settings.assets.video,
#         media_type="video/mp4",
#         filename="VIDEO.mp4",
#     )
