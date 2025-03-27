from functools import lru_cache

from pydantic import BaseModel


class AssetsSettings(BaseModel):
    audio: str = "./assets/audio/AUDIO.wav"
    image: str = "./assets/image/"
    video: str = "./assets/video/VIDEO.mp4"


class HostSettings(BaseModel):
    voice_generator: str = "http://localhost:8001/"
    video_generator: str = "http://localhost:8002/"


class Settings(BaseModel):
    app_name: str = "Chatacter"
    assets: AssetsSettings = AssetsSettings()
    character: str = str()
    host: HostSettings = HostSettings()
    vector_database_name: str = "chatacter"


@lru_cache
def load_settings() -> Settings:
    return Settings()


if __name__ == "__main__":
    settings: Settings = load_settings()
    print(settings.model_dump_json(indent=4))
