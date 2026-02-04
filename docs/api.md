# API Reference

This document provides detailed API reference for Chattr's core components and interfaces.

## Application API

### App Class

**Location**: `src/chattr/app/builder.py`

The main application class that orchestrates all components.

```python
from chattr.app.builder import App
from chattr.app.settings import Settings

settings = Settings()
app = App(settings)
```

#### Methods

##### `gui() -> Blocks`

Creates and returns the Gradio Blocks interface.

**Returns**: `gradio.Blocks` - The configured Gradio interface

**Example**:
```python
application = app.gui()
application.launch()
```

##### `async _setup_agent() -> Agent`

Internal method that creates and configures the agent.

**Returns**: `agno.Agent` - Configured agent instance

##### `async _setup_tools() -> list[Toolkit]`

Internal method that sets up and returns MCP tools.

**Returns**: `list[Toolkit]` - List of configured toolkits

##### `_setup_model() -> OpenAILike`

Internal method that configures the LLM model.

**Returns**: `agno.models.OpenAILike` - Configured model instance

##### `_setup_database() -> BaseDb`

Internal method that sets up the session database.

**Returns**: `agno.db.BaseDb` - Database instance (JsonDb)

##### `_setup_vector_database() -> Qdrant`

Internal method that configures the vector database.

**Returns**: `agno.vectordb.Qdrant` - Vector database instance

##### `_setup_knowledge(vector_db, db) -> Knowledge`

Internal method that creates the knowledge base.

**Parameters**:
- `vector_db`: Vector database instance
- `db`: Session database instance

**Returns**: `agno.knowledge.Knowledge` - Knowledge base instance

##### `async respond(message, history) -> AsyncGenerator`

Main response handler that processes user messages.

**Parameters**:
- `message: dict` - User message with content and files
- `history: list` - Conversation history

**Yields**: `ChatMessage` - Streaming response messages

**Example**:
```python
async for response in app.respond(message, history):
    print(response.content)
```

## Settings API

**Location**: `src/chattr/app/settings.py`

Pydantic-based settings management with environment variable support.

### Settings Class

```python
from chattr.app.settings import Settings

settings = Settings()
```

#### Attributes

##### `model: ModelSettings`

Model configuration settings.

**Fields**:
- `url: str` - API endpoint URL
- `name: str` - Model name
- `api_key: str` - API authentication key
- `temperature: float` - Model temperature (0.0-1.0)

##### `short_term_memory: MemorySettings`

Redis memory configuration.

**Fields**:
- `url: str` - Redis connection URL

##### `vector_database: VectorDBSettings`

Vector database configuration.

**Fields**:
- `name: str` - Collection name

##### `mcp: MCPSettings`

MCP service configuration.

**Fields**:
- `path: Path` - Path to mcp.json configuration file

##### `directory: DirectorySettings`

Asset directory configuration.

**Fields**:
- `assets: Path` - Base assets directory
- `log: Path` - Log files directory
- `image: Path` - Image directory
- `audio: Path` - Audio directory
- `video: Path` - Video directory

### Environment Variable Mapping

```python
# Format: SECTION__FIELD
MODEL__URL=https://api.groq.com/openai/v1
MODEL__NAME=llama3-70b-8192
MODEL__API_KEY=your_key
MODEL__TEMPERATURE=0.0

SHORT_TERM_MEMORY__URL=redis://localhost:6379

VECTOR_DATABASE__NAME=chattr

DIRECTORY__ASSETS=./assets
DIRECTORY__LOG=./logs
```

## Agent API

The agent is configured using the Agno framework. Key configuration:

```python
from agno.agent import Agent
from agno.models.openai.like import OpenAILike

agent = Agent(
    model=OpenAILike(
        id="llama3-70b-8192",
        base_url="https://api.groq.com/openai/v1",
        api_key="your_key",
    ),
    tools=[...],  # List of toolkits
    description="Character description",
    instructions=["List", "of", "instructions"],
    db=database,
    knowledge=knowledge_base,
    markdown=True,
    add_datetime_to_context=True,
    pre_hooks=[...],  # Guardrails
    debug_mode=True,
)
```

### Agent Methods

#### `async run(message: str) -> AsyncGenerator`

Process a message and generate responses.

**Parameters**:
- `message: str` - User message to process

**Yields**: Various event types:
- `RunContentEvent` - Text content from agent
- `ToolCallStartedEvent` - Tool execution started
- `ToolCallCompletedEvent` - Tool execution completed

**Example**:
```python
async for event in agent.run("Hello!"):
    if isinstance(event, RunContentEvent):
        print(event.content)
```

## Tools API

### MCP Tools

MCP tools are automatically discovered from configured MCP servers.

#### Configuration (mcp.json)

```json
{
  "mcp_servers": [
    {
      "name": "tool-name",
      "type": "url",
      "url": "http://localhost:8001/gradio_api/mcp/sse",
      "description": "Tool description"
    }
  ]
}
```

#### Using MCP Tools

Tools are automatically available to the agent based on the MCP server capabilities.

Example tool invocation by agent:
```python
# Agent automatically calls tools based on instructions
# Example: Generate audio
audio_result = await voice_generator_tool(
    text="Response text to convert to speech"
)
```

## Gradio Interface API

### ChatInterface

The Gradio ChatInterface is configured with:

```python
from gradio import ChatInterface

interface = ChatInterface(
    fn=app.respond,  # Response function
    type="messages",
    multimodal=True,  # Support text, images, audio, video
)
```

### Message Format

#### Input Message

```python
{
    "text": "User message text",
    "files": [
        {
            "path": "/path/to/file",
            "mime_type": "image/jpeg",
            "size": 12345
        }
    ]
}
```

#### Output Message (ChatMessage)

```python
from gradio import ChatMessage

ChatMessage(
    role="assistant",  # or "user"
    content="Response text",
    metadata={
        "title": "Tool Name",
        "status": "running",
    }
)
```

#### Multimodal Content

```python
from gradio import Audio, Video

# Text with audio
ChatMessage(
    role="assistant",
    content={"text": "Here's the audio", "audio": Audio(...)}
)

# Text with video
ChatMessage(
    role="assistant",
    content={"text": "Here's the video", "video": Video(...)}
)
```

## Events API

### Event Types

Events are emitted during agent processing:

#### `RunContentEvent`

Text content generated by the agent.

```python
@dataclass
class RunContentEvent:
    content: str  # Generated text
```

#### `ToolCallStartedEvent`

Indicates a tool execution has started.

```python
@dataclass
class ToolCallStartedEvent:
    tool_name: str
    parameters: dict
```

#### `ToolCallCompletedEvent`

Indicates a tool execution has completed.

```python
@dataclass
class ToolCallCompletedEvent:
    tool_name: str
    result: any
```

## Memory API

### Short-term Memory (Redis)

Managed automatically by the Agno agent framework.

**Connection**:
```python
# Configured via environment variable
SHORT_TERM_MEMORY__URL=redis://localhost:6379
```

**Storage**:
- Session-based conversation history
- Automatic expiration
- Key-value storage

### Long-term Memory (Qdrant)

Vector database for semantic search and knowledge storage.

**Connection**:
```python
from agno.vectordb.qdrant import Qdrant

vector_db = Qdrant(
    collection=settings.vector_database.name,
    embedder=FastEmbed(model="BAAI/bge-small-en-v1.5"),
)
```

**Operations**:
- Automatic embedding generation
- Semantic similarity search
- Document storage and retrieval

## Knowledge API

### Knowledge Base

```python
from agno.knowledge import Knowledge

knowledge = Knowledge(
    sources=["path/to/documents"],
    vector_db=vector_db,
)
```

### Adding Documents

Documents can be added to the knowledge base:

```python
# Documents are automatically processed and embedded
# Retrieved during agent processing based on relevance
```

## Guardrails API

### PII Detection

```python
from agno.guardrails import PIIDetectionGuardrail

pii_guard = PIIDetectionGuardrail()
```

Detects and filters:
- Email addresses
- Phone numbers
- Social security numbers
- Credit card numbers
- Other personal identifiers

### Prompt Injection Detection

```python
from agno.guardrails import PromptInjectionGuardrail

injection_guard = PromptInjectionGuardrail()
```

Detects attempts to:
- Override system instructions
- Inject malicious prompts
- Manipulate agent behavior

## Logging API

### Logger Configuration

**Location**: `src/chattr/app/logger.py`

```python
from chattr.app.settings import logger

logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message")
logger.debug("Debug message")
```

### Log Levels

- `DEBUG`: Detailed debugging information
- `INFO`: General information messages
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

## Error Handling

### Gradio Errors

```python
from gradio import Error

raise Error("User-friendly error message")
```

### Custom Exceptions

Handle exceptions appropriately:

```python
try:
    result = await agent.run(message)
except ValidationError as e:
    logger.error(f"Validation error: {e}")
    raise Error("Invalid input provided")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise Error("An unexpected error occurred")
```

## Type Hints

Chattr uses Python type hints extensively:

```python
from typing import TYPE_CHECKING, AsyncGenerator
from collections.abc import Sequence

if TYPE_CHECKING:
    from agno.agent import Agent
    from gradio import Blocks

async def respond(
    message: dict,
    history: Sequence[dict],
) -> AsyncGenerator[ChatMessage, None]:
    ...
```

## Example: Custom Application

```python
from chattr.app.builder import App
from chattr.app.settings import Settings
from gradio import Blocks

# Initialize with custom settings
settings = Settings(
    model__url="https://api.openai.com/v1",
    model__name="gpt-4",
    model__api_key="your_key",
)

# Create app
app = App(settings)

# Get Gradio interface
interface: Blocks = app.gui()

# Configure and launch
interface.queue(api_open=True)
interface.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=False,
)
```

## Example: Direct Agent Usage

```python
from agno.agent import Agent, RunContentEvent
from chattr.app.settings import Settings

settings = Settings()
app = App(settings)
agent = await app._setup_agent()

# Process message
async for event in agent.run("Tell me about your campaigns"):
    if isinstance(event, RunContentEvent):
        print(f"Agent: {event.content}")
```
