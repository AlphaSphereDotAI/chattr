from datetime import datetime
from os import getenv
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from requests import get, RequestException, Response

load_dotenv()

SERVER_URL: str = getenv(key="SERVER_URL", default="127.0.0.1")
SERVER_PORT: int = int(getenv(key="SERVER_PORT", default="7860"))
CURRENT_DATE: str = datetime.now().strftime(format="%Y-%m-%d_%H-%M-%S")
MCP_VOICE_GENERATOR: str = getenv(
    key="MCP_VOICE_GENERATOR", default="http://localhost:8001/"
)
MCP_VIDEO_GENERATOR: str = getenv(
    key="MCP_VIDEO_GENERATOR", default="http://localhost:8002/"
)
VECTOR_DATABASE_NAME: str = getenv(
    key="VECTOR_DATABASE_NAME", default="chattr"
)
DOCKER_MODEL_RUNNER_URL: str = getenv(
    key="DOCKER_MODEL_RUNNER_URL", default="http://127.0.0.1:12434/engines/v1"
)
DOCKER_MODEL_RUNNER_MODEL_NAME: str = getenv(
    key="DOCKER_MODEL_RUNNER_MODEL_NAME",
    default="ai/qwen3:0.6B-Q4_0",
)
GROQ_URL: str = getenv(
    key="MODEL_URL", default="https://api.groq.com/openai/v1"
)
GROQ_MODEL_NAME: str = getenv(key="GROQ_MODEL_NAME", default="llama3-70b-8192")

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


try:
    response: Response = get(DOCKER_MODEL_RUNNER_URL, timeout=10)
    response.raise_for_status()
    MODEL_URL: str = DOCKER_MODEL_RUNNER_URL
except RequestException as e:
    logger.warning(
        f"Failed to connect to Docker Model URL, using GROQ API fallback: {e!r}"
    )
    MODEL_URL: str = GROQ_URL

MODEL_NAME: str = (
    DOCKER_MODEL_RUNNER_MODEL_NAME
    if MODEL_URL == DOCKER_MODEL_RUNNER_URL
    else GROQ_MODEL_NAME
)
MODEL_API_KEY: str = (
    "not-needed"
    if MODEL_URL == DOCKER_MODEL_RUNNER_URL
    else getenv("GROQ_API_KEY")
)
MODEL_TEMPERATURE: float = float(getenv(key="MODEL_TEMPERATURE", default=0.0))

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
logger.info(f"Model URL is going to be used is {MODEL_URL}")
logger.info(f"Model name is going to be used is {MODEL_NAME}")
logger.info(f"Model temperature is going to be used is {MODEL_TEMPERATURE}")
