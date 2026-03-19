# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation suite
  - Getting Started guide
  - Architecture documentation
  - Configuration guide with all environment variables
  - API reference documentation
  - Development guide with coding standards
  - Deployment guide for various platforms
  - Troubleshooting guide with common issues
- CONTRIBUTING.md with contribution guidelines
- CHANGELOG.md for tracking changes
- LICENSE file

### Changed
- Enhanced README.md with links to documentation

### Fixed
- N/A

### Security
- N/A

## [0.0.106] - 2024-02-04

### Added
- Initial release of Chattr
- Multi-agent conversational system
- Character-based AI interactions (Napoleon by default)
- Gradio web interface
- MCP integration for audio/video generation
- Redis-based short-term memory
- Qdrant vector database for knowledge storage
- PII detection guardrail
- Prompt injection protection guardrail
- Docker deployment support
- Environment-based configuration
- FastEmbed integration for embeddings

### Features
- Character agent with personality instructions
- Multi-modal responses (text, audio, video)
- Knowledge base integration
- Memory management (short-term and long-term)
- Tool usage through MCP servers
- Progressive web app support
- API access for programmatic use

### Dependencies
- Python 3.13
- agno[google,qdrant] >= 2.4.8
- gradio[mcp] >= 6.5.1
- fastembed >= 0.7.4
- mem0ai >= 1.0.3
- Redis for memory storage
- Qdrant for vector database

### Development
- pytest test framework
- ruff for linting and formatting
- pre-commit hooks
- trunk for code quality
- Docker and docker-compose support

---

## Version History Format

### Added
For new features.

### Changed
For changes in existing functionality.

### Deprecated
For soon-to-be removed features.

### Removed
For now removed features.

### Fixed
For any bug fixes.

### Security
In case of vulnerabilities.

---

[Unreleased]: https://github.com/AlphaSphereDotAI/chattr/compare/v0.0.106...HEAD
[0.0.106]: https://github.com/AlphaSphereDotAI/chattr/releases/tag/v0.0.106
