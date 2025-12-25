from typing import TYPE_CHECKING

from chattr.app.runner import app

if TYPE_CHECKING:
    from gradio import Blocks


def main() -> None:
    """Launch the Gradio Multi-agent system app."""
    application: Blocks = app.gui()
    application.queue(api_open=True)
    application.launch(
        debug=True,
        enable_monitoring=True,
        show_error=True,
        pwa=True,
    )


if __name__ == "__main__":
    main()
