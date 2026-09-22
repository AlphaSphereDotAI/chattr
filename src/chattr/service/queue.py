from agno.os import QueueConfig

from chattr.settings.queue import QueueSettings


def setup_queue(queue: QueueSettings) -> QueueConfig:
    return QueueConfig(**queue.model_dump())
