# Architecture

This document describes the architecture and design of Chattr.

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Component Details](#component-details)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [Design Decisions](#design-decisions)
- [Performance Considerations](#performance-considerations)

## Overview

Chattr is a multi-modal AI chat application built on a microservices architecture. It combines natural language processing, vector databases, and multi-modal generation services to create an immersive conversational experience with AI-powered historical characters.

### Architecture Goals

- **Modularity**: Each component serves a specific purpose
- **Scalability**: Horizontal scaling for high traffic
- **Maintainability**: Clear separation of concerns
- **Extensibility**: Easy to add new features and characters
- **Reliability**: Fault tolerance and graceful degradation

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
│                    (Web Browser/API Client)                  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      Presentation Layer                      │
│                        Gradio Interface                      │
│              (ChatInterface + Multi-modal UI)                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                       │
│                                                              │
│  ┌──────────────┐     ┌──────────────┐    ┌─────────────┐  │
│  │     App      │────▶│    Agent     │───▶│   Tools     │  │
│  │   Builder    │     │   (Agno)     │    │   (MCP)     │  │
│  └──────────────┘     └──────┬───────┘    └─────────────┘  │
│                               │                              │
│                    ┌──────────┴──────────┐                  │
│                    ▼                     ▼                   │
│            ┌──────────────┐      ┌──────────────┐           │
│            │   Memory     │      │  Knowledge   │           │
│            │  Manager     │      │    Base      │           │
│            └──────────────┘      └──────────────┘           │
└────────────────────────┬────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│   Qdrant    │  │ Voice Gen    │  │  Video Gen   │
│  (Vector    │  │   Service    │  │   Service    │
│    DB)      │  │    (MCP)     │  │    (MCP)     │
└─────────────┘  └──────────────┘  └──────────────┘
        │
        ▼
┌─────────────┐
│   Model     │
│   API       │
│ (Groq/etc)  │
└─────────────┘
```

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                      Chattr Core                         │
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────┐  │
│  │  Settings  │  │   Logger   │  │  Scheme (Models) │  │
│  └────────────┘  └────────────┘  └──────────────────┘  │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │              App Builder                         │   │
│  │  • Agent setup                                   │   │
│  │  • Tool configuration                            │   │
│  │  • Model initialization                          │   │
│  │  • Knowledge base setup                          │   │
│  │  • GUI creation                                  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Runner                              │   │
│  │  • Application entry point                       │   │
│  │  • Gradio launch configuration                   │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Gradio Interface (Presentation Layer)

**Purpose**: Provides the web-based chat interface

**Technology**: Gradio ChatInterface

**Responsibilities**:
- Render chat UI
- Handle user input
- Display multi-modal responses (text, audio, video)
- Manage conversation history
- Provide API endpoints

**Key Features**:
- Real-time streaming responses
- Multi-modal message support
- History persistence
- PWA support
- Auto-generated REST API

### 2. App Builder (Application Core)

**Purpose**: Orchestrates the entire application

**Location**: `src/chattr/app/builder.py`

**Responsibilities**:
- Initialize and configure AI agent
- Set up model connections
- Configure tools and services
- Manage knowledge base
- Handle request/response flow
- Coordinate multi-modal generation

**Key Methods**:
- `__init__()`: Initialize with settings
- `_setup_agent()`: Configure Agno agent
- `_setup_model()`: Initialize LLM
- `_setup_tools()`: Configure MCP tools
- `generate_response()`: Main request handler
- `gui()`: Create Gradio interface

### 3. Agno Agent (AI Core)

**Purpose**: Main AI reasoning and coordination

**Technology**: Agno Framework

**Features**:
- Multi-turn conversations
- Tool calling
- Memory management
- Context awareness
- Streaming responses
- Guardrails (PII, prompt injection)

**Configuration**:
```python
Agent(
    model=OpenAILike(...),
    tools=[MultiMCPTools(...)],
    instructions=[...],
    db=JsonDb(...),
    knowledge=Knowledge(...),
    guardrails=[
        PIIDetectionGuardrail(),
        PromptInjectionGuardrail()
    ]
)
```

### 4. Vector Database (Qdrant)

**Purpose**: Store and retrieve vector embeddings

**Use Cases**:
- Knowledge base search
- Semantic similarity
- Long-term memory
- Context retrieval

**Collections**:
- `chattr`: Main knowledge collection
- `memories`: Conversation memories

**Features**:
- Fast vector search
- Filtering capabilities
- Persistence
- Scalability

### 5. Model Context Protocol (MCP) Services

**Purpose**: Enable tool calling for audio/video generation

**Services**:
- **Voice Generator**: Text-to-speech conversion
- **Video Generator**: Video synthesis from audio/image

**Protocol**: Server-Sent Events (SSE) over HTTP

**Integration**: Via Agno's MultiMCPTools

### 6. Settings & Configuration

**Purpose**: Centralized configuration management

**Location**: `src/chattr/app/settings.py`

**Technology**: Pydantic Settings

**Features**:
- Environment variable parsing
- Type validation
- Nested configuration
- Default values
- Computed fields

**Structure**:
```python
Settings
├── model: ModelSettings
├── vector_database: VectorDatabaseSettings
├── memory: MemorySettings
├── directory: DirectorySettings
├── mcp: MCPSettings
└── character: CharacterSettings
```

## Data Flow

### Request Flow

```
1. User Input
   │
   └─▶ Gradio ChatInterface
       │
       └─▶ App.generate_response()
           │
           ├─▶ Agent.arun()
           │   │
           │   ├─▶ Model API (Text Generation)
           │   │   └─▶ Returns: Text response
           │   │
           │   ├─▶ Knowledge Base Search
           │   │   └─▶ Qdrant vector search
           │   │       └─▶ Returns: Context
           │   │
           │   ├─▶ Memory Retrieval
           │   │   └─▶ Returns: Past context
           │   │
           │   └─▶ Tool Calls
           │       ├─▶ Voice Generator (MCP)
           │       │   └─▶ Returns: Audio file path
           │       │
           │       └─▶ Video Generator (MCP)
           │           └─▶ Returns: Video file path
           │
           └─▶ Stream results to UI
               └─▶ Display in ChatInterface
```

### Event Flow

```
RunContentEvent
├─▶ Text content from model
└─▶ Appended to chat history

ToolCallStartedEvent
├─▶ Tool invocation begins
└─▶ Shows tool arguments in UI

ToolCallCompletedEvent
├─▶ Tool execution complete
├─▶ Result available
└─▶ Multi-modal content displayed
    ├─▶ Audio player (if audio generated)
    └─▶ Video player (if video generated)
```

## Technology Stack

### Core Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Language | Python 3.13+ | Application development |
| Framework | Gradio 6.5+ | Web interface |
| AI Agent | Agno 2.4+ | Agent orchestration |
| LLM | OpenAI-compatible | Text generation |
| Vector DB | Qdrant | Embeddings storage |
| Memory | Mem0 1.0+ | Long-term memory |
| Embeddings | FastEmbed 0.7+ | Vector embeddings |
| Config | Pydantic | Configuration management |
| Prompts | POML 0.0.8+ | Prompt templating |

### Infrastructure

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Container | Docker | Containerization |
| Orchestration | Docker Compose / K8s | Service management |
| Reverse Proxy | Nginx | Load balancing, SSL |
| Monitoring | Gradio built-in | Application metrics |

### Development Tools

| Tool | Purpose |
|------|---------|
| uv | Package management |
| pytest | Testing |
| trunk | Linting & formatting |
| pre-commit | Git hooks |
| ruff | Code formatting |
| mypy | Type checking |

## Design Decisions

### 1. Microservices Architecture

**Decision**: Separate audio/video generation into independent services

**Rationale**:
- Resource isolation
- Independent scaling
- Technology flexibility
- Fault isolation

**Trade-offs**:
- Increased complexity
- Network overhead
- More deployment components

### 2. Agno Framework

**Decision**: Use Agno for agent orchestration

**Rationale**:
- Built-in tool calling
- Memory management
- Streaming support
- OpenAI compatibility
- Guardrails integration

**Alternatives Considered**:
- LangChain: More complex, heavier
- Custom solution: More work, less features

### 3. Qdrant Vector Database

**Decision**: Use Qdrant for embeddings

**Rationale**:
- Fast vector search
- Easy Docker deployment
- Good Python support
- Filtering capabilities
- Persistent storage

**Alternatives Considered**:
- Pinecone: Cloud-only, cost
- Weaviate: More complex
- Chroma: Less mature

### 4. Gradio for UI

**Decision**: Use Gradio ChatInterface

**Rationale**:
- Rapid development
- Built-in API generation
- Multi-modal support
- PWA capabilities
- MCP integration

**Alternatives Considered**:
- React custom UI: More work
- Streamlit: Less chat-focused
- FastAPI + React: More complex

### 5. Pydantic Settings

**Decision**: Use Pydantic for configuration

**Rationale**:
- Type validation
- Environment variable parsing
- Clear error messages
- Computed fields
- Documentation

## Performance Considerations

### Optimization Strategies

1. **Streaming Responses**
   - Real-time content delivery
   - Better perceived performance
   - Progressive rendering

2. **Connection Pooling**
   - Reuse HTTP connections
   - Reduce latency
   - Lower overhead

3. **Caching**
   - Vector search results
   - Model responses (optional)
   - Static assets

4. **Async Operations**
   - Non-blocking I/O
   - Concurrent tool calls
   - Better resource utilization

### Scalability

**Horizontal Scaling**:
- Stateless application design
- Load balancer distribution
- Session affinity for WebSocket

**Resource Management**:
- Memory limits per container
- CPU quotas
- Connection pooling

**Bottlenecks**:
- Model API rate limits
- Vector DB query performance
- Multi-modal generation time

### Monitoring Metrics

- Request latency
- Tool call duration
- Memory usage
- Error rates
- Active connections

## Security Architecture

### Defense Layers

1. **Input Validation**
   - Pydantic schema validation
   - Type checking
   - Length limits

2. **Guardrails**
   - PII detection
   - Prompt injection prevention
   - Content filtering

3. **Network Security**
   - HTTPS/TLS encryption
   - Firewall rules
   - Rate limiting

4. **Secrets Management**
   - Environment variables
   - Docker secrets
   - Kubernetes secrets

## Future Considerations

### Planned Enhancements

- [ ] Redis caching layer
- [ ] Distributed tracing
- [ ] Advanced analytics
- [ ] Multi-character support
- [ ] User authentication
- [ ] Custom model fine-tuning
- [ ] Real-time collaboration
- [ ] Mobile app

### Technical Debt

- Add comprehensive integration tests
- Improve error handling
- Add request retries
- Implement circuit breakers
- Add metric collection

## References

- [Agno Documentation](https://github.com/agno-dev/agno)
- [Gradio Documentation](https://gradio.app/docs)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Pydantic Documentation](https://docs.pydantic.dev)
- [MCP Specification](https://github.com/gradio-app/gradio-mcp)
