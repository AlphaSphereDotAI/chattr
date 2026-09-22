from agno.os import QueueConfig
from pydantic import BaseModel


class QueueSettings(BaseModel, QueueConfig):
    pass
