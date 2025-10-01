from asyncio import run

from chattr.app.builder import App
from chattr.app.settings import Settings

settings: Settings = Settings()
app: App = run(App.create(settings))
