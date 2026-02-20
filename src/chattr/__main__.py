from chattr.app.app import App
from chattr.app.settings import Settings


def main() -> None:
    """Launch the app."""
    settings = Settings()
    application = App(settings)
    gradio_application = application.gradio_app()
    gradio_application.queue(api_open=True)
    gradio_application.launch(
        debug=True, enable_monitoring=True, show_error=True, pwa=True
    )


if __name__ == "__main__":
    main()
