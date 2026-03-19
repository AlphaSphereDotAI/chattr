# Configuration Guide

This guide provides detailed information about configuring Chattr through environment variables and configuration files.

## Environment Variables

All configuration is done through environment variables. You can set them in your shell, in a `.env` file, or in your container orchestration system.

### Model Configuration

#### `MODEL__URL`
- **Description**: OpenAI-compatible API endpoint
- **Required**: No
- **Default**: `https://api.groq.com/openai/v1`
- **Example**: `https://api.openai.com/v1`

The base URL for the LLM API. Chattr supports any OpenAI-compatible endpoint.

#### `MODEL__NAME`
- **Description**: Model name/identifier to use
- **Required**: No
- **Default**: `llama3-70b-8192`
- **Example**: `gpt-4`, `llama3-70b-8192`, `mixtral-8x7b-32768`

The specific model to use for generating responses.

#### `MODEL__API_KEY`
- **Description**: API key for model endpoint authentication
- **Required**: **Yes**
- **Default**: None
- **Example**: `sk-proj-...` or `gsk_...`

**Security Note**: Never commit API keys to version control. Use environment variables or secrets management.

#### `MODEL__TEMPERATURE`
- **Description**: Model temperature for response randomness
- **Required**: No
- **Default**: `0.0`
- **Range**: `0.0` to `1.0`

Controls the creativity/randomness of responses:
- `0.0`: Deterministic, focused responses
- `0.7`: Balanced creativity
- `1.0`: Maximum creativity/randomness

### Memory Configuration

#### `SHORT_TERM_MEMORY__URL`
- **Description**: Redis connection URL for session memory
- **Required**: No
- **Default**: `redis://localhost:6379`
- **Format**: `redis://[password@]host[:port][/database]`

Examples:
```bash
# Local Redis
SHORT_TERM_MEMORY__URL=redis://localhost:6379

# Redis with password
SHORT_TERM_MEMORY__URL=redis://password@redis-server:6379

# Redis with database selection
SHORT_TERM_MEMORY__URL=redis://localhost:6379/0
```

### Vector Database Configuration

#### `VECTOR_DATABASE__NAME`
- **Description**: Collection name in Qdrant vector database
- **Required**: No
- **Default**: `chattr`

The collection name used to store and retrieve embeddings.

**Note**: Qdrant connection is configured via Agno framework settings. The default connects to a local Qdrant instance.

### MCP Service Configuration

MCP (Multi-agent Coordination Protocol) services provide additional capabilities like audio and video generation.

#### `VOICE_GENERATOR_MCP__URL`
- **Description**: MCP service endpoint for text-to-speech
- **Required**: No
- **Default**: `http://localhost:8001/gradio_api/mcp/sse`
- **Format**: `http://host:port/gradio_api/mcp/sse`

The MCP service that converts text responses to speech audio.

#### `VIDEO_GENERATOR_MCP__URL`
- **Description**: MCP service endpoint for audio-to-video
- **Required**: No
- **Default**: `http://localhost:8002/gradio_api/mcp/sse`
- **Format**: `http://host:port/gradio_api/mcp/sse`

The MCP service that generates animated videos from audio.

### Directory Configuration

All directory paths can be absolute or relative to the project root.

#### `DIRECTORY__ASSETS`
- **Description**: Base directory for all asset files
- **Required**: No
- **Default**: `./assets`

#### `DIRECTORY__LOG`
- **Description**: Directory for log files
- **Required**: No
- **Default**: `./logs`

#### `DIRECTORY__IMAGE`
- **Description**: Directory for image assets
- **Required**: No
- **Default**: `./assets/image`

#### `DIRECTORY__AUDIO`
- **Description**: Directory for generated audio files
- **Required**: No
- **Default**: `./assets/audio`

#### `DIRECTORY__VIDEO`
- **Description**: Directory for generated video files
- **Required**: No
- **Default**: `./assets/video`

## Configuration File Formats

### .env File

Create a `.env` file in the project root:

```bash
# Model Configuration
MODEL__URL=https://api.groq.com/openai/v1
MODEL__NAME=llama3-70b-8192
MODEL__API_KEY=your_api_key_here
MODEL__TEMPERATURE=0.0

# Memory Configuration
SHORT_TERM_MEMORY__URL=redis://localhost:6379

# Vector Database
VECTOR_DATABASE__NAME=chattr

# MCP Services
VOICE_GENERATOR_MCP__URL=http://localhost:8001/gradio_api/mcp/sse
VIDEO_GENERATOR_MCP__URL=http://localhost:8002/gradio_api/mcp/sse

# Directories
DIRECTORY__ASSETS=./assets
DIRECTORY__LOG=./logs
DIRECTORY__IMAGE=./assets/image
DIRECTORY__AUDIO=./assets/audio
DIRECTORY__VIDEO=./assets/video
```

### MCP Configuration (mcp.json)

The `mcp.json` file configures MCP server connections:

```json
{
  "mcp_servers": [
    {
      "name": "voice-generator",
      "type": "url",
      "url": "http://localhost:8001/gradio_api/mcp/sse",
      "description": "Text-to-speech service"
    },
    {
      "name": "video-generator",
      "type": "url",
      "url": "http://localhost:8002/gradio_api/mcp/sse",
      "description": "Audio-to-video animation service"
    }
  ]
}
```

## Docker Configuration

### docker-compose.yaml

The docker-compose configuration supports environment variable substitution:

```yaml
version: '3.8'

services:
  chattr:
    build: .
    ports:
      - "7860:7860"
    environment:
      - MODEL__API_KEY=${MODEL__API_KEY}
      - MODEL__URL=${MODEL__URL:-https://api.groq.com/openai/v1}
      - MODEL__NAME=${MODEL__NAME:-llama3-70b-8192}
      - SHORT_TERM_MEMORY__URL=redis://redis:6379
    volumes:
      - ./assets:/app/assets
      - ./logs:/app/logs
    depends_on:
      - redis
      - qdrant

  redis:
    image: redis:latest
    ports:
      - "6379:6379"

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_storage:/qdrant/storage
```

### Environment Variables in Docker

Create a `.env` file for Docker Compose:

```bash
MODEL__API_KEY=your_api_key_here
MODEL__URL=https://api.groq.com/openai/v1
MODEL__NAME=llama3-70b-8192
```

Docker Compose will automatically load these variables.

## Configuration Validation

Chattr uses Pydantic for configuration validation. Invalid configurations will raise errors at startup:

```python
# Invalid configuration example
MODEL__TEMPERATURE=2.0  # Error: Must be between 0.0 and 1.0
MODEL__URL=not-a-url    # Error: Must be a valid URL
```

## Advanced Configuration

### Custom Agent Configuration

To customize the agent behavior, modify `src/chattr/app/builder.py`:

```python
async def _setup_agent(self) -> Agent:
    return Agent(
        model=self._setup_model(),
        tools=await self._setup_tools(),
        description="Custom character description",
        instructions=[
            "Custom instruction 1",
            "Custom instruction 2",
        ],
        temperature=0.7,  # Override temperature
        # ... other settings
    )
```

### Multiple Characters

To support multiple characters, you can:

1. Create different agent configurations
2. Select agent based on user input
3. Maintain separate memory spaces per character

### Custom Tools

Add custom tools by extending the MCP configuration or implementing local tools:

```python
from agno.tools import Toolkit

class CustomToolkit(Toolkit):
    def __init__(self):
        super().__init__(name="custom_toolkit")
        self.register(self.custom_function)
    
    def custom_function(self, param: str) -> str:
        """Custom tool implementation."""
        return f"Processed: {param}"
```

## Production Recommendations

### Security

- **Never commit secrets**: Use environment variables or secrets managers
- **Use HTTPS**: Always use secure connections for API endpoints
- **Rotate API keys**: Regularly rotate your API keys
- **Limit access**: Use network policies to restrict service access

### Performance

- **Redis persistence**: Configure Redis for data persistence in production
- **Qdrant optimization**: Tune Qdrant for your workload
- **Resource limits**: Set appropriate CPU/memory limits
- **Connection pooling**: Configure connection pool sizes

### Monitoring

- **Enable logging**: Set appropriate log levels
- **Track metrics**: Monitor API usage and response times
- **Error tracking**: Implement error reporting
- **Health checks**: Add health check endpoints

### Example Production Configuration

```bash
# Production .env
MODEL__API_KEY=prod_api_key_from_secrets_manager
MODEL__URL=https://api.production-endpoint.com/v1
MODEL__NAME=gpt-4
MODEL__TEMPERATURE=0.0

# Production Redis with persistence
SHORT_TERM_MEMORY__URL=redis://redis-cluster.prod.internal:6379/0

# Production Qdrant
VECTOR_DATABASE__NAME=chattr_production

# Production directories with persistent volumes
DIRECTORY__ASSETS=/data/assets
DIRECTORY__LOG=/data/logs
```

## Troubleshooting Configuration

### Common Issues

1. **Invalid API Key**
   - Check the format of your API key
   - Verify the key is active and has proper permissions

2. **Redis Connection Failed**
   - Verify Redis is running: `redis-cli ping`
   - Check the connection URL format
   - Verify network connectivity

3. **MCP Service Unreachable**
   - Verify MCP services are running
   - Check URLs and ports
   - Review network policies

### Configuration Debugging

Enable debug logging to see configuration values:

```python
# In settings.py
logger.setLevel("DEBUG")
```

View loaded configuration:
```bash
uv run python -c "from chattr.app.settings import Settings; print(Settings())"
```
