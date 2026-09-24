from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, FilePath, PositiveInt
from pydantic_extra_types.timezone_name import TimeZoneName


class AgentSettings(BaseModel):
    markdown: bool = Field(default=True)
    add_datetime_to_context: bool = Field(default=True)
    timezone_identifier: TimeZoneName | None = Field(default="Africa/Cairo")
    debug_mode: bool = Field(default=False)
    debug_level: Literal[1, 2] = Field(default=1)
    save_response_to_file: FilePath = Field(default_factory=lambda: Path.cwd() / "agno" / "response.txt")
    add_history_to_context: bool = Field(default=True)
    enable_agentic_state: bool = Field(default=True)
    cache_session: bool = Field(default=True)
    checkpoint: Literal["runs", "tool-batch", "tools"] | None = Field(default=None)
    enable_agentic_memory: bool = Field(default=True)
    update_memory_on_run: bool = Field(default=True)
    add_memories_to_context: bool | None = Field(default=None)
    enable_session_summaries: bool = Field(default=True)
    add_session_summary_to_context: bool | None = Field(default=None)
    compress_tool_results: bool = Field(default=True)
    num_history_runs: PositiveInt | None = Field(default=None)
    num_history_messages: PositiveInt | None = Field(default=None)
    enable_agentic_knowledge_filters: bool | None = Field(default=None)
    add_knowledge_to_context: bool = Field(default=True)
    tool_call_limit: PositiveInt | None = Field(default=None)
    max_tool_calls_from_history: PositiveInt | None = Field(default=None)
    read_chat_history: bool = Field(default=True)
    search_knowledge: bool = Field(default=True)
    add_search_knowledge_instructions: bool = Field(default=True)
    update_knowledge: bool = Field(default=True)
    read_tool_call_history: bool = Field(default=True)
    send_media_to_model: bool = Field(default=False)
    store_media: bool = Field(default=True)
    store_tool_messages: bool = Field(default=True)
    store_history_messages: bool = Field(default=True)
    retries: PositiveInt = Field(default=0)
    delay_between_retries: PositiveInt = Field(default=1)
    structured_outputs: bool | None = Field(default=None)
    use_json_mode: bool = Field(default=False)
    cache_callables: bool = Field(default=True)
