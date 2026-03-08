# Chattr Documentation

Welcome to the comprehensive documentation for **Chattr**, a multi-agent conversational system built with Gradio that enables character-based interactions with AI models.

## Quick Links

- [Getting Started](getting-started.md) - Installation and quick start guide
- [Architecture](architecture.md) - System design and components
- [Configuration](configuration.md) - Environment variables and settings
- [API Reference](api.md) - Agent and tool API documentation
- [Development](development.md) - Development setup and guidelines
- [Deployment](deployment.md) - Production deployment guide
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

## What is Chattr?

Chattr is the application component of the Character Backend system that enables:

- **Character-based AI interactions**: Agents that can mimic specific characters and personalities
- **Multi-modal responses**: Generate text, audio, and video responses
- **Knowledge integration**: Vector database support for contextual responses
- **Memory management**: Short-term and long-term memory capabilities
- **MCP integration**: Multi-agent coordination through MCP servers
- **Guardrails**: Built-in PII detection and prompt injection protection

## Key Features

- 🎭 **Character Agents**: AI agents with specific personality traits and behaviors
- 🔊 **Audio Generation**: Text-to-speech capabilities through MCP services
- 🎥 **Video Generation**: Animated video responses from audio
- 🧠 **Knowledge Base**: Vector database integration for contextual information
- 💾 **Memory System**: Redis-based memory for conversation continuity
- 🛡️ **Security**: PII detection and prompt injection guardrails
- 🐳 **Docker Ready**: Containerized deployment with docker-compose

## Technology Stack

- **Python 3.13**: Modern Python with latest features
- **Gradio**: Web UI framework with chat interface
- **Agno**: Multi-agent framework with tool support
- **Qdrant**: Vector database for knowledge storage
- **Redis**: Short-term memory store
- **FastEmbed**: Fast embedding generation
- **MCP**: Multi-agent coordination protocol

## Getting Help

- **Issues**: Report bugs on [GitHub Issues](https://github.com/AlphaSphereDotAI/chattr/issues)
- **Documentation**: Browse this documentation for guides and references
- **Contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines

## Project Status

[![Build](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/build.yaml/badge.svg)](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/build.yaml)
[![Test](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/test.yaml/badge.svg)](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/test.yaml)
[![CodeQL](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/AlphaSphereDotAI/chattr/actions/workflows/github-code-scanning/codeql)
