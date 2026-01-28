# API Reference

This document provides detailed API documentation for Chattr.

## Table of Contents

- [Python API](#python-api)
- [REST API](#rest-api)
- [Configuration API](#configuration-api)
- [MCP Protocol](#mcp-protocol)

## Python API

### App Class

The main application class for Chattr.

```python
from chattr.app.builder import App
from chattr.app.settings import Settings

settings = Settings()
app = App(settings)
```

#### Methods

##### `gui() -> Blocks`

Create and return the Gradio Blocks interface.

**Returns:**
- `Blocks`: Gradio interface for the chat application

**Example:**
```python
app = App(settings)
interface = app.gui()
interface.launch()
```

##### `async generate_response(message: str, history: list[ChatMessage]) -> AsyncGenerator`

Generate a response to a user message.

**Parameters:**
- `message` (str): User input message
- `history` (list[ChatMessage]): Conversation history

**Yields:**
- tuple: (empty_string, updated_history, audio_path, video_path)

**Example:**
```python
async for response in app.generate_response("Hello!", []):
    print(response)
```

### Settings Class

Configuration management using Pydantic.

```python
from chattr.app.settings import Settings

settings = Settings()
print(settings.model.name)
print(settings.vector_database.url)
```

#### Sections

##### ModelSettings

Configuration for AI model.

```python
class ModelSettings(BaseModel):
    url: HttpUrl | None
    name: str | None
    api_key: SecretStr | None
    temperature: float = 0.0
```

**Fields:**
- `url`: OpenAI-compatible API endpoint
- `name`: Model identifier
- `api_key`: API authentication key
- `temperature`: Sampling temperature (0.0-1.0)

##### VectorDatabaseSettings

Configuration for Qdrant vector database.

```python
class VectorDatabaseSettings(BaseModel):
    name: str = "chattr"
    url: HttpUrl = "http://localhost:6333"
```

**Fields:**
- `name`: Collection name in Qdrant
- `url`: Qdrant server URL

##### DirectorySettings

File system paths configuration.

```python
class DirectorySettings(BaseModel):
    base: DirectoryPath
    
    @property
    def assets(self) -> DirectoryPath
    
    @property
    def audio(self) -> DirectoryPath
    
    @property
    def video(self) -> DirectoryPath
    
    @property
    def prompts(self) -> DirectoryPath
```

**Properties:**
- `base`: Base directory
- `assets`: Assets directory path
- `audio`: Audio files directory
- `video`: Video files directory
- `prompts`: Character prompts directory

##### MemorySettings

Memory and context configuration.

```python
class MemorySettings(BaseModel):
    collection_name: str = "memories"
    embedding_dims: int = 384
```

**Fields:**
- `collection_name`: Memory collection identifier
- `embedding_dims`: Embedding vector dimensions

## REST API

Gradio automatically generates REST API endpoints.

### Base URL

```
http://localhost:7860
```

### Endpoints

#### POST `/api/predict`

Send a message and receive a response.

**Request:**
```json
{
  "data": [
    "Hello Napoleon!",
    []
  ]
}
```

**Response:**
```json
{
  "data": [
    [
      {
        "role": "user",
        "content": "Hello Napoleon!"
      },
      {
        "role": "assistant",
        "content": "Bonjour! I am Napoleon Bonaparte..."
      }
    ]
  ],
  "duration": 2.5
}
```

#### GET `/api/`

Get API information.

**Response:**
```json
{
  "named_endpoints": {
    "/chat": {
      "parameters": [
        {
          "label": "message",
          "type": "string"
        },
        {
          "label": "history",
          "type": "array"
        }
      ]
    }
  }
}
```

### Using the API

#### Python Client

```python
from gradio_client import Client

client = Client("http://localhost:7860")

# Send a message
result = client.predict(
    message="Tell me about the Battle of Waterloo",
    history=[],
    api_name="/chat"
)

print(result)
```

#### cURL

```bash
curl -X POST http://localhost:7860/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      "Tell me about the Battle of Waterloo",
      []
    ]
  }'
```

#### JavaScript/TypeScript

```javascript
const response = await fetch('http://localhost:7860/api/predict', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    data: [
      'Tell me about the Battle of Waterloo',
      []
    ]
  })
});

const result = await response.json();
console.log(result);
```

## Configuration API

### Environment Variables

Configuration is done through environment variables with nested structure using double underscores.

#### Setting Values

```bash
# Direct export
export MODEL__API_KEY="your-key"
export MODEL__NAME="llama3-70b-8192"

# Using .env file
echo "MODEL__API_KEY=your-key" >> .env
echo "MODEL__NAME=llama3-70b-8192" >> .env
```

#### Programmatic Configuration

```python
import os
from chattr.app.settings import Settings

# Set environment variables
os.environ["MODEL__API_KEY"] = "your-key"
os.environ["MODEL__NAME"] = "llama3-70b-8192"

# Load settings
settings = Settings()

# Access configuration
print(settings.model.name)
print(settings.model.api_key.get_secret_value())
```

### MCP Configuration

The `mcp.json` file configures Model Context Protocol services.

#### Structure

```json
{
  "mcp_servers": [
    {
      "name": "service_name",
      "type": "url",
      "url": "http://localhost:8001/gradio_api/mcp/sse",
      "transport": "sse"
    }
  ]
}
```

#### Fields

- `name`: Service identifier
- `type`: Connection type ("url" or "stdio")
- `url`: Service endpoint URL
- `transport`: Transport protocol ("sse" or "http")

#### Example Configuration

```json
{
  "mcp_servers": [
    {
      "name": "voice_generator",
      "type": "url",
      "url": "http://voice-service:8001/gradio_api/mcp/sse",
      "transport": "sse"
    },
    {
      "name": "video_generator",
      "type": "url",
      "url": "http://video-service:8002/gradio_api/mcp/sse",
      "transport": "sse"
    }
  ]
}
```

## MCP Protocol

### Overview

Chattr uses the Model Context Protocol (MCP) to communicate with auxiliary services for audio and video generation.

### Message Format

#### Tool Call Request

```json
{
  "tool_name": "generate_audio_for_text",
  "tool_args": {
    "text": "Hello, I am Napoleon Bonaparte.",
    "voice": "napoleon"
  }
}
```

#### Tool Call Response

```json
{
  "result": "/path/to/audio.wav",
  "status": "success",
  "duration": 1.23
}
```

### Available Tools

#### generate_audio_for_text

Generate audio from text using TTS.

**Parameters:**
- `text` (str): Text to convert to speech
- `voice` (str, optional): Voice model to use

**Returns:**
- `str`: Path to generated audio file

#### generate_video_mcp

Generate video from audio and image.

**Parameters:**
- `audio_path` (str): Path to audio file
- `image_path` (str): Path to character image

**Returns:**
- `str`: Path to generated video file

### Custom Tool Integration

To add custom MCP tools:

1. **Implement MCP server**:
   ```python
   from gradio_mcp import MCPServer
   
   server = MCPServer()
   
   @server.tool()
   def my_custom_tool(param: str) -> str:
       return f"Processed: {param}"
   ```

2. **Add to mcp.json**:
   ```json
   {
     "name": "my_custom_service",
     "type": "url",
     "url": "http://localhost:8003/gradio_api/mcp/sse",
     "transport": "sse"
   }
   ```

3. **Use in agent**:
   The tool will be automatically available to the agent.

## Error Handling

### Common Errors

#### `ValidationError`

Raised when configuration is invalid.

```python
from pydantic import ValidationError

try:
    settings = Settings()
except ValidationError as e:
    print(e.errors())
```

#### `Error` (Gradio)

Raised for user-facing errors.

```python
from gradio import Error

raise Error("Model API key is required")
```

### Error Response Format

```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "status": "error"
}
```

## Rate Limiting

No built-in rate limiting. For production deployments, use a reverse proxy like Nginx with rate limiting configured.

## Authentication

No built-in authentication. For production deployments:

1. Use Gradio's built-in auth:
   ```python
   interface.launch(auth=("username", "password"))
   ```

2. Deploy behind an authentication proxy

3. Implement custom middleware

## Monitoring

### Health Check

```bash
curl http://localhost:7860/
```

### Metrics

Gradio provides basic metrics at `/metrics` (if enabled):

```python
interface.launch(enable_monitoring=True)
```

## Examples

### Complete Usage Example

```python
import asyncio
from chattr.app.builder import App
from chattr.app.settings import Settings
from agno.models.message import Message

async def main():
    # Initialize
    settings = Settings()
    app = App(settings)
    
    # Setup agent
    agent = await app._setup_agent()
    
    # Generate response
    async for event in agent.arun(
        Message(content="Hello Napoleon!", role="user"),
        stream=True
    ):
        print(event)
    
    # Cleanup
    await app._close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Custom Character Example

```python
# Create custom prompt in assets/prompts/custom.poml
# Then update builder.py to load it

from pathlib import Path
from poml import poml

prompt = poml(
    Path("assets/prompts/custom.poml"),
    {"character": "Einstein"},
    chat=False,
    format="dict"
)
```

## Further Resources

- [Gradio Documentation](https://gradio.app/docs)
- [Agno Framework](https://github.com/agno-dev/agno)
- [Pydantic Documentation](https://docs.pydantic.dev)
- [MCP Specification](https://github.com/gradio-app/gradio-mcp)
