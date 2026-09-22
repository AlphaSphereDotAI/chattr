from logging import Logger

from agno.os import AgentOS
from agno.utils.log import configure_agno_logging
from fastapi import FastAPI

from chattr.core import setup_logger
from chattr.service import setup_service
from chattr.settings import Settings


def main() -> None:
    """Launch the app."""
    settings: Settings = Settings()
    logger: Logger = setup_logger(settings.log)
    configure_agno_logging(custom_default_logger=logger)
    agent_os: AgentOS = setup_service(settings)
    app: FastAPI = agent_os.get_app()
    agent_os.serve(app=app, access_log=True)


if __name__ == "__main__":
    main()
