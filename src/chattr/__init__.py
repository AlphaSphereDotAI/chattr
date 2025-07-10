from datetime import datetime
from os import getenv
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

SERVER_URL: str = getenv(key="SERVER_URL", default="127.0.0.1")
SERVER_PORT: int = getenv(key="SERVER_PORT", default=7860)
CURRENT_DATE: str = datetime.now().strftime(format="%Y-%m-%d_%H-%M-%S")
MCP_VOICE_GENERATOR: str = getenv(
    key="MCP_VOICE_GENERATOR", default="http://localhost:8001/"
)
MCP_VIDEO_GENERATOR: str = getenv(
    key="MCP_VIDEO_GENERATOR", default="http://localhost:8002/"
)
VECTOR_DATABASE_NAME: str = getenv(key="VECTOR_DATABASE_NAME", default="chattr")
GROQ_MODEL_NAME: str = getenv(key="GROQ_MODEL_NAME", default="llama-3.1-8b-instant")
GROQ_MODEL_TEMPERATURE: float = getenv(key="GROQ_MODEL_TEMPERATURE", default=0.0)

BASE_DIR: Path = Path.cwd()
ASSETS_DIR: Path = BASE_DIR / "assets"
LOG_DIR: Path = BASE_DIR / "logs"
IMAGE_DIR: Path = ASSETS_DIR / "image"
AUDIO_DIR: Path = ASSETS_DIR / "audio"
VIDEO_DIR: Path = ASSETS_DIR / "video"

LOG_FILE_PATH: Path = LOG_DIR / f"{CURRENT_DATE}.log"
AUDIO_FILE_PATH: Path = AUDIO_DIR / f"{CURRENT_DATE}.wav"
VIDEO_FILE_PATH: Path = VIDEO_DIR / f"{CURRENT_DATE}.mp4"

ASSETS_DIR.mkdir(exist_ok=True)
IMAGE_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)
VIDEO_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

logger.add(
    sink=LOG_FILE_PATH,
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    colorize=True,
)

logger.info(f"Current date: {CURRENT_DATE}")
logger.info(f"Base directory: {BASE_DIR}")
logger.info(f"Assets directory: {ASSETS_DIR}")
logger.info(f"Log directory: {LOG_DIR}")
logger.info(f"Audio file path: {AUDIO_FILE_PATH}")
logger.info(f"Log file path: {LOG_FILE_PATH}")
