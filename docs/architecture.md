# Architecture

This document describes the architecture and design of the Chattr system.

## System Overview

Chattr is a multi-agent conversational system built on top of the Agno framework, providing character-based AI interactions with multi-modal response capabilities.

```
┌─────────────────────────────────────────────────────────────┐
│                        Gradio UI                             │
│                    (Chat Interface)                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                      Chattr App                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │              Agent (Napoleon)                      │     │
│  │  - Model: OpenAI-compatible LLM                   │     │
│  │  - Instructions: Character personality            │     │
│  │  - Guardrails: PII + Prompt Injection            │     │
│  └──────────┬─────────────────────────┬───────────────┘     │
│             │                         │                     │
│  ┌──────────▼──────────┐   ┌──────────▼──────────┐         │
│  │   Tools & MCP       │   │   Memory & Knowledge │         │
│  │  - Voice Gen MCP    │   │  - Redis (Short-term)│         │
│  │  - Video Gen MCP    │   │  - Qdrant (Vector DB)│         │
│  └─────────────────────┘   └──────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Application Layer (`App`)

**Location**: `src/chattr/app/builder.py`

The main application class that orchestrates all components:

- **Initialization**: Sets up all system components and dependencies
- **Agent Management**: Creates and configures the AI agent
- **UI Integration**: Connects the agent to the Gradio interface
- **Event Handling**: Processes user messages and agent responses

Key responsibilities:
- Agent lifecycle management
- Tool and MCP server integration
- Database connections
- Knowledge base setup

### 2. Agent System

**Framework**: Agno Agent

The agent is the core intelligence of the system:

```python
Agent(
    model=OpenAI-compatible model,
    tools=[MCP tools],
    description="Character description",
    instructions=[Behavior guidelines],
    db=Database for session storage,
    knowledge=Knowledge base,
    guardrails=[Security checks],
)
```

**Key Features**:
- Character-based personality (Napoleon by default)
- Multi-step reasoning with tool usage
- Context-aware responses
- Memory integration
- Security guardrails

### 3. Model Layer

**Type**: OpenAI-compatible LLM

Configurable model connection:
- Default: Groq API with llama3-70b-8192
- Supports any OpenAI-compatible endpoint
- Configurable temperature and parameters

### 4. Tools and MCP Integration

**MCP (Multi-agent Coordination Protocol)**: Allows integration with external services

Supported tools:
- **Voice Generator MCP**: Text-to-speech service
- **Video Generator MCP**: Audio-to-video animation service
- **Web Search**: DuckDuckGo search capability
- **M3U8 Processing**: Video playlist handling

MCP servers are configured in `mcp.json` and loaded dynamically.

### 5. Memory System

**Two-tier memory architecture**:

#### Short-term Memory (Redis)
- Session-based conversation history
- Fast access to recent interactions
- Temporary context storage
- Default: `redis://localhost:6379`

#### Long-term Memory (Qdrant)
- Vector embeddings of important information
- Semantic search capabilities
- Persistent knowledge storage
- Embedding model: FastEmbed

### 6. Knowledge Base

**Location**: Agno Knowledge system with Qdrant backend

Features:
- Document ingestion and indexing
- Semantic similarity search
- Context retrieval for agent responses
- Automatic embedding generation

### 7. Guardrails

**Security layers** that protect against misuse:

1. **PII Detection Guardrail**
   - Detects and filters personal identifiable information
   - Prevents leakage of sensitive data

2. **Prompt Injection Guardrail**
   - Detects attempts to manipulate the agent
   - Prevents jailbreak attempts

### 8. UI Layer (Gradio)

**Interface**: Gradio ChatInterface

Features:
- Real-time chat interactions
- Multi-modal content display (text, audio, video)
- File upload capabilities
- Progressive web app (PWA) support
- API access for programmatic use

## Data Flow

### Typical Message Processing Flow

```
1. User Input
   ↓
2. Gradio UI captures message
   ↓
3. App.respond() processes message
   ↓
4. Agent receives message with context
   ↓
5. Agent checks guardrails
   ↓
6. Agent retrieves relevant knowledge from Qdrant
   ↓
7. Agent loads conversation history from Redis
   ↓
8. Agent generates response using LLM
   ↓
9. Agent calls MCP tools (voice/video generation)
   ↓
10. Agent returns complete response
    ↓
11. UI displays text, audio, and video
    ↓
12. Memory updated (Redis + Qdrant)
```

### Event Streaming

The system uses async generators for real-time updates:

```python
async def respond() -> AsyncGenerator[ChatMessage, None]:
    async for event in agent.run():
        if isinstance(event, RunContentEvent):
            yield ChatMessage(role="assistant", content=event.content)
        elif isinstance(event, ToolCallStartedEvent):
            yield ChatMessage(role="assistant", metadata=tool_info)
```

## Configuration System

**Settings Management**: Pydantic BaseSettings

All configuration is loaded from environment variables with validation:

```python
class Settings(BaseSettings):
    model: ModelSettings
    short_term_memory: MemorySettings
    vector_database: VectorDBSettings
    mcp: MCPSettings
    directory: DirectorySettings
```

Benefits:
- Type safety and validation
- Environment variable parsing
- Nested configuration objects
- Default values with overrides

## Directory Structure

```
chattr/
├── src/chattr/
│   ├── __init__.py
│   ├── __main__.py          # Entry point
│   └── app/
│       ├── __init__.py
│       ├── builder.py       # Main App class
│       ├── logger.py        # Logging configuration
│       ├── runner.py        # App instance
│       ├── scheme.py        # Data schemas
│       └── settings.py      # Configuration
├── assets/                  # Generated media files
│   ├── audio/
│   ├── video/
│   └── image/
├── logs/                    # Application logs
├── mcp.json                 # MCP server configuration
└── pyproject.toml          # Project dependencies
```

## Deployment Architecture

### Docker Deployment

The system is containerized for easy deployment:

```
┌─────────────────────────────────────────────┐
│         Chattr Container                    │
│  - Python 3.13                             │
│  - Gradio app on port 7860                 │
│  - FastEmbed cache                         │
└──────────────┬──────────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────┐         ┌──────▼────┐
│ Redis  │         │  Qdrant   │
│ :6379  │         │  :6333    │
└────────┘         └───────────┘
```

### Scalability Considerations

- **Stateless design**: Each request is independent
- **External storage**: Redis and Qdrant can be scaled separately
- **MCP services**: Can run on separate instances
- **Load balancing**: Multiple Chattr instances can share databases

## Extension Points

### Adding New Characters

Modify agent configuration in `builder.py`:
```python
description="New character description",
instructions=["Character-specific instructions"],
```

### Adding New Tools

1. Implement tool in MCP server
2. Add server URL to `mcp.json`
3. Tools are automatically discovered and loaded

### Custom Guardrails

Extend the guardrails list:
```python
pre_hooks=[
    PIIDetectionGuardrail(),
    PromptInjectionGuardrail(),
    CustomGuardrail(),  # Add custom guardrail
]
```

### Alternative Models

Change model configuration:
```python
MODEL__URL=https://api.openai.com/v1
MODEL__NAME=gpt-4
MODEL__API_KEY=your_key
```

## Performance Considerations

- **Embedding Cache**: FastEmbed caches models locally
- **Redis Connection Pooling**: Reuses connections for efficiency
- **Async Operations**: Non-blocking I/O for concurrent requests
- **Vector Search**: Optimized similarity search with Qdrant
- **Streaming Responses**: Progressive UI updates via async generators

## Security Architecture

1. **Guardrails**: Pre-processing security checks
2. **Environment Variables**: Secrets not in code
3. **Container Isolation**: Docker security boundaries
4. **Network Policies**: Configurable service access
5. **Input Validation**: Pydantic models validate all inputs
