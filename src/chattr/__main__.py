from logging import Logger

from agno.os import AgentOS
from agno.utils.log import configure_agno_logging
from fastapi import FastAPI
from gradio import Blocks, mount_gradio_app

from chattr.app.app import setup_app
from chattr.app.logger import setup_logger
from chattr.app.settings import Settings
from chattr.app.ui import setup_ui


def main() -> None:
    """Launch the app."""
    settings: Settings = Settings()
    logger: Logger = setup_logger(settings.log)
    configure_agno_logging(custom_default_logger=logger)

    agent_os: AgentOS = setup_app(settings)
    app: FastAPI = agent_os.get_app()

    gradio_application: Blocks = setup_ui()
    app: FastAPI = mount_gradio_app(app, gradio_application, path="/gradio")

    # Remove TrailingSlashMiddleware to fix infinite redirect loop with Gradio mount
    app.user_middleware = [
        m for m in app.user_middleware if m.cls.__name__ != "TrailingSlashMiddleware"
    ]

    agent_os.serve(app=app, access_log=True)


if __name__ == "__main__":
    main()
