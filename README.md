---
title: Chattr
emoji: 💬
colorFrom: gray
colorTo: blue
sdk: gradio
python_version: 3.13
app_file: src/chattr/__main__.py
short_description: Chat with Characters
---

<div align="center">

# 💬 Chattr

**Multi-modal AI Character Chat Application**

[![Build](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/build.yaml/badge.svg)](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/build.yaml)
[![CI Tools](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/ci_tools.yaml/badge.svg)](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/ci_tools.yaml)
[![CodeQL](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/github-code-scanning/codeql)
[![Test](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/test.yaml/badge.svg)](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/test.yaml)
[![Release](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/release.yaml/badge.svg)](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/release.yaml)

[Features](#-features) •
[Quick Start](#-quick-start) •
[Documentation](#-documentation) •
[API Reference](docs/API.md) •
[Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Development](#-development)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)
- [Support](#-support)

## 🌟 Overview

**Chattr** is an advanced multi-modal AI-powered chat application that enables users to interact with historical characters through text, audio, and video. Built with cutting-edge AI technologies, Chattr provides an immersive conversational experience where characters respond not just with text, but with authentic voice and video representations.

### Key Highlights

- 🎭 **Character Personas**: Chat with historically accurate AI representations of famous figures
- 🎙️ **Voice Generation**: Responses are converted to audio with character-appropriate voices
- 🎬 **Video Synthesis**: Visual responses with animated character representations
- 🧠 **Memory & Context**: Long-term memory and contextual understanding
- 🔒 **Security-First**: Built-in PII detection and prompt injection protection
- 🐳 **Docker-Ready**: Easy deployment with Docker Compose

## ✨ Features

### Core Capabilities

- **Multi-Modal Conversations**: Engage with characters through text, voice, and video
- **AI-Powered Agents**: Built on Agno framework with OpenAI-compatible models
- **Vector Knowledge Base**: Qdrant-powered semantic search for contextual responses
- **Memory Management**: Persistent conversation history and long-term memory with Mem0
- **MCP Integration**: Model Context Protocol for audio and video generation services
- **Guardrails**: PII detection and prompt injection prevention

### Technical Features

- **Gradio Web Interface**: Modern, responsive chat interface
- **Streaming Responses**: Real-time message streaming for better UX
- **Tool Integration**: Extensible architecture for adding new capabilities
- **Docker Deployment**: Production-ready containerized deployment
- **Monitoring**: Built-in health checks and logging
- **Type Safety**: Full Python type hints and Pydantic validation

## 🏗️ Architecture

Chattr follows a modular microservices architecture:

```
┌─────────────────┐
│   Gradio UI     │
│  (Chat Interface)│
└────────┬────────┘
         │
┌────────▼─────────┐      ┌──────────────┐
│   Chattr Core    │◄─────┤  Qdrant DB   │
│  (Agno Agent)    │      │  (Vectors)   │
└────────┬─────────┘      └──────────────┘
         │
         ├──────────────┐
         │              │
┌────────▼────────┐ ┌──▼─────────────┐
│ Voice Generator │ │Video Generator │
│     (MCP)       │ │     (MCP)      │
└─────────────────┘ └────────────────┘
```

### Components

1. **Chattr Core**: Main application built with Agno framework
2. **Gradio Interface**: Web-based chat UI with multi-modal support
3. **Qdrant**: Vector database for knowledge and memory storage
4. **Voice Generator**: MCP service for text-to-speech conversion
5. **Video Generator**: MCP service for video synthesis

## 🚀 Quick Start

Get Chattr up and running in minutes! For a detailed walkthrough, see the [Quick Start Guide](docs/QUICKSTART.md).

### Prerequisites

- Docker & Docker Compose (recommended)
- **OR** Python 3.13+ with `uv` package manager
- API key for an OpenAI-compatible model (e.g., Groq, Google Gemini)

### Docker Deployment (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AlphaSphereDotAI/chattr.git
   cd chattr
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your MODEL__API_KEY
   ```

3. **Launch with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

4. **Access the application**:
   Open your browser to `http://localhost:7860`

### Local Development

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Configure environment**:
   ```bash
   export MODEL__API_KEY="your-api-key"
   export MODEL__URL="https://api.groq.com/openai/v1"
   export MODEL__NAME="llama3-70b-8192"
   ```

3. **Run the application**:
   ```bash
   uv run chattr
   ```

## 📦 Installation

### System Requirements

- **Python**: 3.13+
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB for models and dependencies
- **Network**: Internet connection for AI model APIs

### Installation Methods

#### Using UV (Recommended)

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install chattr
uv tool install chattr

# Run directly
chattr
```

#### Using Pip

```bash
pip install chattr
chattr
```

#### From Source

```bash
git clone https://github.com/AlphaSphereDotAI/chattr.git
cd chattr
uv sync
uv run chattr
```

## ⚙️ Configuration

### Environment Variables

Chattr is configured using environment variables with the pattern `SECTION__VARIABLE`:

#### Model Configuration

| Variable             | Description                    | Required | Default                                  |
|:--------------------|:-------------------------------|:--------:|:-----------------------------------------|
| `MODEL__URL`        | OpenAI-compatible API endpoint | ✘        | `https://api.groq.com/openai/v1`         |
| `MODEL__NAME`       | Model name to use              | ✘        | `llama3-70b-8192`                        |
| `MODEL__API_KEY`    | API key for model access       | ✔        | `None`                                   |
| `MODEL__TEMPERATURE`| Generation temperature (0-1)   | ✘        | `0.0`                                    |

#### Vector Database

| Variable                 | Description               | Required | Default                  |
|:------------------------|:--------------------------|:--------:|:-------------------------|
| `VECTOR_DATABASE__URL`  | Qdrant server URL         | ✘        | `http://localhost:6333`  |
| `VECTOR_DATABASE__NAME` | Collection name           | ✘        | `chattr`                 |

#### Memory Settings

| Variable                      | Description               | Required | Default      |
|:-----------------------------|:--------------------------|:--------:|:-------------|
| `MEMORY__COLLECTION_NAME`    | Memory collection name    | ✘        | `memories`   |
| `MEMORY__EMBEDDING_DIMS`     | Embedding dimensions      | ✘        | `384`        |

#### Directory Configuration

| Variable            | Description              | Required | Default              |
|:-------------------|:-------------------------|:--------:|:---------------------|
| `DIRECTORY__BASE`  | Base directory           | ✘        | Current directory    |
| `DIRECTORY__ASSETS`| Assets directory         | ✘        | `./assets`           |
| `DIRECTORY__AUDIO` | Audio files directory    | ✘        | `./assets/audio`     |
| `DIRECTORY__VIDEO` | Video files directory    | ✘        | `./assets/video`     |

#### MCP Services

| Variable              | Description                    | Required | Default                                    |
|:---------------------|:-------------------------------|:--------:|:-------------------------------------------|
| `MCP__PATH`          | Path to MCP config JSON        | ✘        | `./mcp.json`                               |

### MCP Configuration File

Create a `mcp.json` file to configure Model Context Protocol services:

```json
{
  "mcp_servers": [
    {
      "name": "voice_generator",
      "type": "url",
      "url": "http://localhost:8001/gradio_api/mcp/sse",
      "transport": "sse"
    },
    {
      "name": "video_generator",
      "type": "url",
      "url": "http://localhost:8002/gradio_api/mcp/sse",
      "transport": "sse"
    }
  ]
}
```

### Character Configuration

Customize character prompts by editing files in `assets/prompts/`:

```
assets/
  prompts/
    template.poml    # Character prompt template
  image/
    Napoleon.jpg     # Character images
    Einstein.jpg
```

## 📖 Usage

### Basic Chat

1. Start the application
2. Navigate to `http://localhost:7860`
3. Type your message and press Enter
4. The character will respond with text, audio, and optionally video

### Advanced Features

#### Memory and Context

Chattr automatically maintains conversation history and long-term memory:

```python
# Conversations are automatically saved
# References to past conversations work seamlessly
"Remember what I asked you earlier about..."
```

#### Tool Usage

The agent can use various tools during conversations:

- **Text Generation**: Standard conversational responses
- **Audio Generation**: Converts responses to speech
- **Video Generation**: Creates video representations
- **Knowledge Search**: Searches vector database for relevant information

### API Access

Gradio provides automatic API endpoints:

```python
from gradio_client import Client

client = Client("http://localhost:7860")
result = client.predict(
    message="Hello Napoleon!",
    history=[],
    api_name="/chat"
)
```

## 🛠️ Development

### Setting Up Development Environment

1. **Clone and install**:
   ```bash
   git clone https://github.com/AlphaSphereDotAI/chattr.git
   cd chattr
   uv sync
   ```

2. **Install pre-commit hooks**:
   ```bash
   uv run pre-commit install
   ```

3. **Run in development mode**:
   ```bash
   uv run chattr
   ```

### Code Quality

#### Linting and Formatting

```bash
# Format code
trunk fmt --all --no-progress

# Run linters
trunk check

# Type checking
mypy src/
```

#### Testing

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_app.py::test_app

# With coverage
pytest --cov=chattr --cov-report=html
```

### Building

```bash
# Build distributions
uv build

# Build Docker image
docker build -t chattr:latest .
```

### Project Structure

```
chattr/
├── src/
│   └── chattr/
│       ├── __init__.py
│       ├── __main__.py
│       └── app/
│           ├── builder.py      # Main app logic
│           ├── runner.py       # Entry point
│           ├── settings.py     # Configuration
│           ├── scheme.py       # Data models
│           └── logger.py       # Logging setup
├── tests/
│   └── test_app.py            # Tests
├── assets/
│   ├── prompts/               # Character prompts
│   ├── image/                 # Character images
│   ├── audio/                 # Generated audio
│   └── video/                 # Generated video
├── docker-compose.yaml        # Production compose
├── docker-compose-dev.yaml    # Development compose
├── Dockerfile                 # Container definition
├── pyproject.toml            # Project metadata
└── README.md                 # This file
```

## 📚 Documentation

For comprehensive documentation, see the [Documentation Index](docs/INDEX.md).

### Core Documentation

- [**Quick Start Guide**](docs/QUICKSTART.md) - Get running in 5 minutes
- [**API Reference**](docs/API.md) - Detailed API documentation
- [**Deployment Guide**](docs/DEPLOYMENT.md) - Production deployment instructions
- [**Development Guide**](docs/DEVELOPMENT.md) - Contributing and development workflow
- [**Architecture**](docs/ARCHITECTURE.md) - System design and architecture details
- [**Troubleshooting**](docs/TROUBLESHOOTING.md) - Common issues and solutions
- [**Security Policy**](SECURITY.md) - Security best practices and reporting

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `pytest`
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💡 Support

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/AlphaSphereDotAI/chattr/issues)
- **Discussions**: [GitHub Discussions](https://github.com/AlphaSphereDotAI/chattr/discussions)
- **Email**: mohamed.hisham.abdelzaher@gmail.com

### Troubleshooting

#### Common Issues

**Application won't start**:
- Ensure Docker services are running
- Check `MODEL__API_KEY` is set correctly
- Verify Qdrant is accessible

**Audio/Video not generating**:
- Confirm MCP services are running and configured in `mcp.json`
- Check service URLs are accessible

**Memory/Performance issues**:
- Increase Docker memory allocation
- Use lighter model alternatives
- Check Qdrant storage capacity

For more issues, see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

## 🙏 Acknowledgments

Built with amazing open-source technologies:

- [Agno](https://github.com/agno-dev/agno) - AI agent framework
- [Gradio](https://gradio.app) - Web UI framework
- [Qdrant](https://qdrant.tech) - Vector database
- [Mem0](https://mem0.ai) - Memory layer
- [FastEmbed](https://qdrant.github.io/fastembed/) - Fast embeddings
- [Pydantic](https://pydantic.dev) - Data validation

---

<div align="center">

**Made with ❤️ by [AlphaSphere.AI](https://github.com/AlphaSphereDotAI)**

⭐ Star us on GitHub if you find Chattr useful!

</div>
