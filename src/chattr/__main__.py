from gradio import Blocks

from chattr import SERVER_PORT, SERVER_URL
from chattr.gui import app_block


def main() -> None:
    app: Blocks = app_block()
    app.queue(api_open=True).launch(
        server_name=SERVER_URL,
        server_port=SERVER_PORT,
        debug=True,
        show_api=True,
        enable_monitoring=True,
        show_error=True,
        pwa=True,
    )


if __name__ == "__main__":
    main()
