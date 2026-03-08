# Getting Started with Chattr

This guide will help you get Chattr up and running quickly.

## Prerequisites

- Python 3.13
- Docker and Docker Compose (optional, for containerized deployment)
- Redis server (for memory management)
- API key for OpenAI-compatible model endpoint (e.g., Groq)

## Installation

### Option 1: Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/AlphaSphereDotAI/chattr.git
cd chattr

# Install dependencies
uv sync

# Run the application
uv run chattr
```

### Option 2: Using Docker

```bash
# Clone the repository
git clone https://github.com/AlphaSphereDotAI/chattr.git
cd chattr

# Build and run with docker-compose
docker-compose up
```

The application will be available at http://localhost:7860

## Configuration

Before running Chattr, you need to configure environment variables. Create a `.env` file in the project root:

```bash
# Required: API Key for your model provider
MODEL__API_KEY=your_api_key_here

# Optional: Model configuration
MODEL__URL=https://api.groq.com/openai/v1
MODEL__NAME=llama3-70b-8192
MODEL__TEMPERATURE=0.0

# Optional: Memory and database
SHORT_TERM_MEMORY__URL=redis://localhost:6379
VECTOR_DATABASE__NAME=chattr

# Optional: MCP services for audio/video
VOICE_GENERATOR_MCP__URL=http://localhost:8001/gradio_api/mcp/sse
VIDEO_GENERATOR_MCP__URL=http://localhost:8002/gradio_api/mcp/sse

# Optional: Asset directories
DIRECTORY__ASSETS=./assets
DIRECTORY__LOG=./logs
```

See [Configuration Guide](configuration.md) for detailed information about all environment variables.

## Quick Start

### 1. Start Required Services

If you're running locally without Docker, make sure Redis is running:

```bash
# On macOS with Homebrew
brew services start redis

# On Linux
sudo systemctl start redis

# Or using Docker
docker run -d -p 6379:6379 redis:latest
```

### 2. Run Chattr

```bash
# Using uv
uv run chattr

# Or if installed in your environment
chattr
```

### 3. Access the Web Interface

Open your browser and navigate to:
```
http://localhost:7860
```

You should see the Gradio chat interface where you can start interacting with the character agent.

## First Conversation

Once the interface loads:

1. Type a message in the chat input
2. Press Enter or click Send
3. The agent will process your message and respond in character
4. If configured, audio and video responses will be generated

Example conversation:
```
User: Tell me about your greatest military campaigns.
Agent: [Responds in Napoleon's character with text, audio, and video]
```

## Basic Usage

### Chatting with the Agent

The agent is configured by default to mimic Napoleon's character. You can:

- Ask historical questions
- Request opinions on various topics
- Have casual conversations
- All responses will be in Napoleon's voice and style

### Understanding Responses

Each response may include:

1. **Text**: The primary response from the agent
2. **Audio**: Generated speech of the response
3. **Video**: Animated video with the audio

### Memory and Context

The agent maintains:

- **Conversation history**: Recent messages in the current session
- **Long-term memory**: Important facts stored in the vector database
- **Context awareness**: Understanding of the conversation flow

## Next Steps

- [Architecture](architecture.md): Learn about Chattr's system design
- [Configuration](configuration.md): Detailed configuration options
- [API Reference](api.md): Agent and tool API documentation
- [Development](development.md): Set up a development environment

## Troubleshooting

### Application won't start

- Check that all required environment variables are set
- Verify Redis is running and accessible
- Ensure Python 3.13 is installed

### No audio/video generation

- Verify MCP service URLs are correct and services are running
- Check that the MCP servers are accessible
- Review logs for connection errors

### Memory issues

- Verify Redis connection string
- Check Redis server is running
- Review memory configuration settings

For more detailed troubleshooting, see the [Troubleshooting Guide](troubleshooting.md).
