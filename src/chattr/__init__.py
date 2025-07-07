from datetime import datetime
from os import getenv
from pathlib import Path
from loguru import logger

from chattr.graph import Graph

DEBUG: bool = getenv(key="DEBUG", default="True").lower() == "true"
SERVER_NAME: str = getenv(key="GRADIO_SERVER_NAME", default="localhost")
SERVER_PORT: int = int(getenv(key="GRADIO_SERVER_PORT", default="8080"))
CURRENT_DATE: str = datetime.now().strftime(format="%Y-%m-%d_%H-%M-%S")

BASE_DIR: Path = Path.cwd()
RESULTS_DIR: Path = BASE_DIR / "results"
LOG_DIR: Path = BASE_DIR / "logs"
AUDIO_FILE_PATH: Path = RESULTS_DIR / f"{CURRENT_DATE}.wav"
LOG_FILE_PATH: Path = LOG_DIR / f"{CURRENT_DATE}.log"

RESULTS_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

GRAPH = Graph()

logger.info(f"Current date: {CURRENT_DATE}")
logger.info(f"Base directory: {BASE_DIR}")
logger.info(f"Results directory: {RESULTS_DIR}")
logger.info(f"Log directory: {LOG_DIR}")
logger.info(f"Audio file path: {AUDIO_FILE_PATH}")
logger.info(f"Log file path: {LOG_FILE_PATH}")
logger.info(f"Graph: {GRAPH}")
