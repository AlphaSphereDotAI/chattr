"""Entry point for initializing the application with settings."""
from chattr.app.builder import App
from chattr.app.settings import Settings

settings: Settings = Settings()
app: App = App(settings)
