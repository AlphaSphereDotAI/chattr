from anyio import run

from chattr.agent import Agent
from chattr.app.app import App
from chattr.app.settings import Settings


async def main() -> None:
    """Launch the app."""
    settings = Settings()
    chattr_agent = Agent(settings)
    agent = await chattr_agent.setup_agent()
    application = App(agent, settings)
    gradio_application = application.gradio_app()
    gradio_application.queue(api_open=True)
    gradio_application.launch(debug=True, enable_monitoring=True, show_error=True, pwa=True)


if __name__ == "__main__":
    run(main)
