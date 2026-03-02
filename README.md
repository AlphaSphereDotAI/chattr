---
title: Chattr
emoji: 💬
colorFrom: gray
colorTo: blue
sdk: docker
app_port: 7860
short_description: Chat with Characters
---

## **Chattr**: App part of the Chatacter Backend

A multi-agent conversational system built with Gradio that enables character-based AI interactions with multi-modal responses (text, audio, video).

[![Build](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/build.yaml/badge.svg)](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/build.yaml)
[![CI Tools](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/ci_tools.yaml/badge.svg)](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/ci_tools.yaml)
[![CodeQL](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/github-code-scanning/codeql)
[![Dependabot Updates](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/dependabot/dependabot-updates/badge.svg)](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/dependabot/dependabot-updates)
[![Release](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/release.yaml/badge.svg)](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/release.yaml)
[![Test](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/test.yaml/badge.svg)](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/test.yaml)

## 📚 Documentation

- **[Getting Started](docs/getting-started.md)** - Installation and quick start guide
- **[Architecture](docs/architecture.md)** - System design and components
- **[Configuration](docs/configuration.md)** - Environment variables and settings
- **[API Reference](docs/api.md)** - Agent and tool API documentation
- **[Development](docs/development.md)** - Development setup and guidelines
- **[Deployment](docs/deployment.md)** - Production deployment guide
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions
- **[Contributing](CONTRIBUTING.md)** - How to contribute to Chattr
- **[Changelog](CHANGELOG.md)** - Version history and changes

## ✨ Features

- 🎭 **Character Agents**: AI agents with specific personality traits and behaviors
- 🔊 **Audio Generation**: Text-to-speech capabilities through MCP services
- 🎥 **Video Generation**: Animated video responses from audio
- 🧠 **Knowledge Base**: Vector database integration for contextual information
- 💾 **Memory System**: Redis-based memory for conversation continuity
- 🛡️ **Security**: PII detection and prompt injection guardrails
- 🐳 **Docker Ready**: Containerized deployment with docker-compose

## 🚀 Quick Start

### Using uv (Recommended)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/AlphaSphereDotAI/chattr.git
cd chattr
uv sync

# Set required environment variable
export MODEL__API_KEY=your_api_key_here

# Run
uv run chattr
```

### Using Docker

```bash
git clone https://github.com/AlphaSphereDotAI/chattr.git
cd chattr

# Create .env file with your API key
echo "MODEL__API_KEY=your_api_key_here" > .env

# Start all services
docker-compose up
```

Open http://localhost:7860 in your browser.

See [Getting Started Guide](docs/getting-started.md) for detailed instructions.

## ⚙️ Configuration

### Key Environment Variables

| Name                       | Description                      | Required | Default Value                              |
|:---------------------------|:---------------------------------|:--------:|:-------------------------------------------|
| `MODEL__API_KEY`           | API key for model access         |    ✔     | `None`                                     |
| `MODEL__URL`               | OpenAI-compatible endpoint       |    ✘     | `https://api.groq.com/openai/v1`           |
| `MODEL__NAME`              | Model name to use for chat       |    ✘     | `llama3-70b-8192`                          |
| `MODEL__TEMPERATURE`       | Model temperature (0.0-1.0)      |    ✘     | `0.0`                                      |
| `SHORT_TERM_MEMORY__URL`   | Redis URL for memory store       |    ✘     | `redis://localhost:6379`                   |
| `VECTOR_DATABASE__NAME`    | Vector database collection name  |    ✘     | `chattr`                                   |
| `VOICE_GENERATOR_MCP__URL` | MCP service for audio generation |    ✘     | `http://localhost:8001/gradio_api/mcp/sse` |
| `VIDEO_GENERATOR_MCP__URL` | MCP service for video generation |    ✘     | `http://localhost:8002/gradio_api/mcp/sse` |
| `DIRECTORY__ASSETS`        | Base assets directory            |    ✘     | `./assets`                                 |
| `DIRECTORY__LOG`           | Log files directory              |    ✘     | `./logs`                                   |

See [Configuration Guide](docs/configuration.md) for complete configuration options.

## 🛠️ Technology Stack

- **Python 3.13**: Modern Python with latest features
- **Gradio**: Web UI framework with chat interface
- **Agno**: Multi-agent framework with tool support
- **Qdrant**: Vector database for knowledge storage
- **Redis**: Short-term memory store
- **FastEmbed**: Fast embedding generation
- **MCP**: Multi-agent coordination protocol

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- Code of conduct
- Development setup
- Coding standards
- Testing requirements
- Pull request process

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with:
- [Agno](https://agno.dev) - Multi-agent framework
- [Gradio](https://gradio.app) - Web UI framework
- [Qdrant](https://qdrant.tech) - Vector database
- [FastEmbed](https://github.com/qdrant/fastembed) - Fast embeddings

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/AlphaSphereDotAI/chattr/issues)
- **Documentation**: [docs/](docs/)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
