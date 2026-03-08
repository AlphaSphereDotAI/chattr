# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with Chattr.

## Installation Issues

### Python Version Mismatch

**Problem**: Error about Python version compatibility

```
ERROR: This package requires Python 3.13
```

**Solution**:
```bash
# Check Python version
python --version

# Install Python 3.13
# On macOS with Homebrew
brew install python@3.13

# On Ubuntu
sudo apt install python3.13

# Use uv with specific version
uv run --python 3.13 chattr
```

### uv Installation Failed

**Problem**: Cannot install uv package manager

**Solution**:
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version

# Add to PATH if needed
export PATH="$HOME/.cargo/bin:$PATH"
```

### Dependency Resolution Failed

**Problem**: Dependencies cannot be resolved

```
ERROR: Could not find a version that satisfies the requirement
```

**Solution**:
```bash
# Clear cache and retry
rm -rf .venv
uv cache clean
uv sync

# Try with specific Python version
uv sync --python 3.13
```

## Configuration Issues

### Missing API Key

**Problem**: Application fails to start with API key error

```
ValidationError: MODEL__API_KEY field required
```

**Solution**:
```bash
# Set environment variable
export MODEL__API_KEY=your_api_key_here

# Or create .env file
echo "MODEL__API_KEY=your_api_key_here" > .env

# Verify it's set
echo $MODEL__API_KEY
```

### Invalid Environment Variables

**Problem**: Configuration validation errors

```
ValidationError: MODEL__TEMPERATURE must be between 0.0 and 1.0
```

**Solution**:
```bash
# Check your .env file format
# Variables should be:
MODEL__URL=https://api.groq.com/openai/v1  # Valid URL
MODEL__NAME=llama3-70b-8192                 # String
MODEL__TEMPERATURE=0.5                      # Float 0.0-1.0

# Validate configuration
uv run python -c "from chattr.app.settings import Settings; print(Settings())"
```

### Cannot Find mcp.json

**Problem**: MCP configuration file not found

```
FileNotFoundError: mcp.json not found
```

**Solution**:
```bash
# Ensure mcp.json exists in project root
ls -la mcp.json

# Create basic mcp.json if missing
cat > mcp.json << EOF
{
  "mcp_servers": []
}
EOF
```

## Connection Issues

### Redis Connection Failed

**Problem**: Cannot connect to Redis

```
ConnectionError: Error connecting to Redis
```

**Solution**:

1. **Check Redis is running**:
   ```bash
   # Test connection
   redis-cli ping
   # Should return: PONG
   
   # Start Redis if not running
   # macOS
   brew services start redis
   
   # Linux
   sudo systemctl start redis
   
   # Docker
   docker run -d -p 6379:6379 redis:latest
   ```

2. **Verify connection URL**:
   ```bash
   # Check environment variable
   echo $SHORT_TERM_MEMORY__URL
   
   # Should be: redis://localhost:6379
   # Or: redis://password@host:port
   ```

3. **Test connectivity**:
   ```bash
   # Try connecting
   redis-cli -h localhost -p 6379 ping
   ```

### Qdrant Connection Failed

**Problem**: Cannot connect to Qdrant vector database

```
ConnectionError: Could not connect to Qdrant
```

**Solution**:

1. **Start Qdrant**:
   ```bash
   # Using Docker
   docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest
   ```

2. **Verify Qdrant is running**:
   ```bash
   curl http://localhost:6333/healthz
   # Should return: {"status":"ok"}
   ```

3. **Check collection exists**:
   ```bash
   curl http://localhost:6333/collections
   ```

### MCP Service Unreachable

**Problem**: Cannot connect to MCP services

```
ConnectionError: MCP service at http://localhost:8001 unreachable
```

**Solution**:

1. **Verify MCP services are running**:
   ```bash
   curl http://localhost:8001/gradio_api/mcp/sse
   curl http://localhost:8002/gradio_api/mcp/sse
   ```

2. **Check mcp.json configuration**:
   ```json
   {
     "mcp_servers": [
       {
         "name": "voice-generator",
         "type": "url",
         "url": "http://localhost:8001/gradio_api/mcp/sse"
       }
     ]
   }
   ```

3. **Start MCP services** or disable if not needed:
   ```bash
   # Remove from mcp.json if not using
   {
     "mcp_servers": []
   }
   ```

## Runtime Issues

### Application Won't Start

**Problem**: Chattr fails to start

**Diagnostic Steps**:

1. **Check logs**:
   ```bash
   # View startup logs
   uv run chattr 2>&1 | tee startup.log
   ```

2. **Verify all services**:
   ```bash
   # Redis
   redis-cli ping
   
   # Qdrant
   curl http://localhost:6333/healthz
   ```

3. **Check port availability**:
   ```bash
   # Check if port 7860 is in use
   lsof -i :7860
   # Or
   netstat -an | grep 7860
   ```

4. **Try with minimal config**:
   ```bash
   # Only required variables
   export MODEL__API_KEY=your_key
   uv run chattr
   ```

### Gradio UI Not Loading

**Problem**: Web interface doesn't load or shows errors

**Solution**:

1. **Check application is running**:
   ```bash
   curl http://localhost:7860
   ```

2. **Try different browser**:
   - Clear browser cache
   - Try incognito/private mode
   - Try different browser

3. **Check firewall**:
   ```bash
   # Ensure port 7860 is open
   sudo ufw allow 7860  # Linux
   ```

4. **View browser console**:
   - Open browser DevTools (F12)
   - Check Console tab for errors
   - Check Network tab for failed requests

### Memory Errors

**Problem**: Out of memory errors

```
MemoryError: Unable to allocate memory
```

**Solution**:

1. **Monitor memory usage**:
   ```bash
   # Check process memory
   ps aux | grep chattr
   
   # Monitor in real-time
   top -p $(pgrep -f chattr)
   ```

2. **Clear FastEmbed cache**:
   ```bash
   rm -rf ~/fastembed
   # Or set custom cache location
   export FASTEMBED_CACHE_PATH=/tmp/fastembed
   ```

3. **Limit conversation history**:
   - Reduce context window size
   - Clear old sessions from Redis

4. **Increase Docker memory** (if using Docker):
   ```yaml
   # docker-compose.yaml
   services:
     chattr:
       deploy:
         resources:
           limits:
             memory: 4G
   ```

### Slow Response Times

**Problem**: Agent responses are very slow

**Diagnostic Steps**:

1. **Check model API latency**:
   ```bash
   curl -w "@curl-format.txt" -o /dev/null -s \
     "https://api.groq.com/openai/v1/models"
   ```

2. **Monitor Redis performance**:
   ```bash
   redis-cli --latency
   redis-cli info stats
   ```

3. **Check Qdrant query time**:
   ```bash
   # Enable debug logging
   export LOGGING_LEVEL=DEBUG
   # Check logs for query times
   ```

4. **Profile the application**:
   ```python
   # Add timing logs
   import time
   start = time.time()
   # ... operation
   print(f"Took {time.time() - start:.2f}s")
   ```

## Agent Issues

### Agent Not Responding

**Problem**: Agent doesn't generate responses

**Solution**:

1. **Check agent initialization**:
   ```bash
   # Enable debug mode
   uv run python -c "
   import asyncio
   from chattr.app.builder import App
   from chattr.app.settings import Settings
   
   async def test():
       app = App(Settings())
       agent = await app._setup_agent()
       print('Agent initialized:', agent)
   
   asyncio.run(test())
   "
   ```

2. **Verify model connection**:
   ```bash
   # Test API endpoint
   curl -H "Authorization: Bearer $MODEL__API_KEY" \
     https://api.groq.com/openai/v1/models
   ```

3. **Check guardrails**:
   - PII detection may be blocking input
   - Prompt injection detection may be triggered
   - Review logs for guardrail messages

### Character Not Working as Expected

**Problem**: Agent doesn't follow character instructions

**Solution**:

1. **Review instructions**:
   ```python
   # Check agent configuration in builder.py
   Agent(
       description="Character description",
       instructions=[
           "Specific instruction 1",
           "Specific instruction 2",
       ]
   )
   ```

2. **Adjust temperature**:
   ```bash
   # Higher temperature = more creative
   MODEL__TEMPERATURE=0.7
   ```

3. **Improve prompts**:
   - Be more specific in instructions
   - Add examples to description
   - Use system messages

### Tools Not Being Called

**Problem**: Agent doesn't use available tools

**Solution**:

1. **Verify tools are loaded**:
   ```bash
   # Check MCP tools initialization
   # Look for "Loaded tools: ..." in logs
   ```

2. **Check tool availability**:
   ```bash
   # Verify MCP services respond
   curl http://localhost:8001/gradio_api/mcp/sse
   ```

3. **Review instructions**:
   ```python
   # Ensure instructions mention tool usage
   instructions=[
       "ALWAYS generate audio using the appropriate Tool.",
       "Generate video from audio using the appropriate Tool.",
   ]
   ```

## Docker Issues

### Container Fails to Build

**Problem**: Docker build fails

```
ERROR: failed to solve: process "/bin/sh -c ..." failed
```

**Solution**:

1. **Check Docker is running**:
   ```bash
   docker info
   ```

2. **Clear build cache**:
   ```bash
   docker builder prune -a
   ```

3. **Build with verbose output**:
   ```bash
   docker build --progress=plain .
   ```

4. **Check build args**:
   ```bash
   docker build \
     --build-arg INSTALL_SOURCE="chattr" \
     --build-arg PYTHON_VERSION="3.13" \
     .
   ```

### Container Won't Start

**Problem**: Container exits immediately

**Solution**:

1. **Check container logs**:
   ```bash
   docker logs chattr
   docker logs -f chattr  # Follow logs
   ```

2. **Run interactively**:
   ```bash
   docker run -it --rm \
     -e MODEL__API_KEY=your_key \
     chattr:latest /bin/sh
   ```

3. **Check environment variables**:
   ```bash
   docker exec chattr env
   ```

### Docker Compose Issues

**Problem**: Services won't start with docker-compose

**Solution**:

1. **Check service health**:
   ```bash
   docker-compose ps
   ```

2. **View service logs**:
   ```bash
   docker-compose logs -f chattr
   docker-compose logs -f redis
   docker-compose logs -f qdrant
   ```

3. **Restart services**:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

4. **Rebuild containers**:
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

## Data Issues

### Lost Conversation History

**Problem**: Conversations not persisting

**Solution**:

1. **Check Redis persistence**:
   ```bash
   # Verify Redis is saving data
   redis-cli CONFIG GET save
   
   # Force save
   redis-cli SAVE
   ```

2. **Enable Redis persistence**:
   ```bash
   # Add to docker-compose.yaml
   command: redis-server --appendonly yes
   volumes:
     - redis-data:/data
   ```

3. **Check session management**:
   - Verify database path is writable
   - Check disk space
   - Review logs for errors

### Vector Database Issues

**Problem**: Knowledge base not working

**Solution**:

1. **Check Qdrant collections**:
   ```bash
   curl http://localhost:6333/collections
   ```

2. **Verify embeddings**:
   ```bash
   # Check collection info
   curl http://localhost:6333/collections/chattr
   ```

3. **Clear and rebuild**:
   ```bash
   # Delete collection
   curl -X DELETE http://localhost:6333/collections/chattr
   
   # Restart application to recreate
   ```

## Performance Issues

### High CPU Usage

**Problem**: Chattr consuming too much CPU

**Solution**:

1. **Profile the application**:
   ```bash
   # Use py-spy for profiling
   pip install py-spy
   py-spy top --pid $(pgrep -f chattr)
   ```

2. **Reduce model temperature**:
   ```bash
   MODEL__TEMPERATURE=0.0  # More deterministic
   ```

3. **Limit concurrent requests**:
   ```python
   # In Gradio launch
   application.queue(concurrency_count=2)
   ```

### Disk Space Issues

**Problem**: Running out of disk space

**Solution**:

1. **Check disk usage**:
   ```bash
   df -h
   du -sh assets/ logs/
   ```

2. **Clean old assets**:
   ```bash
   # Remove old audio/video files
   find assets/audio -type f -mtime +7 -delete
   find assets/video -type f -mtime +7 -delete
   ```

3. **Rotate logs**:
   ```bash
   # Configure log rotation
   # Or manually clean old logs
   find logs/ -type f -mtime +30 -delete
   ```

4. **Clean Docker**:
   ```bash
   docker system prune -a
   docker volume prune
   ```

## Getting Help

If you're still experiencing issues:

1. **Check GitHub Issues**: [https://github.com/AlphaSphereDotAI/chattr/issues](https://github.com/AlphaSphereDotAI/chattr/issues)

2. **Enable Debug Logging**:
   ```bash
   export LOGGING_LEVEL=DEBUG
   uv run chattr 2>&1 | tee debug.log
   ```

3. **Gather Information**:
   - Python version: `python --version`
   - uv version: `uv --version`
   - OS: `uname -a`
   - Docker version: `docker --version`
   - Error logs
   - Configuration (without secrets)

4. **Create Issue** with:
   - Description of the problem
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - System information
   - Relevant logs

## FAQ

### Q: Can I use a different LLM provider?

**A**: Yes, any OpenAI-compatible API works. Set `MODEL__URL` and `MODEL__API_KEY` appropriately.

### Q: Do I need MCP services?

**A**: No, they're optional. If not using audio/video generation, you can remove them from `mcp.json`.

### Q: Can I run without Redis?

**A**: Redis is required for memory management. Use Docker to run it easily: `docker run -d -p 6379:6379 redis:latest`

### Q: How do I change the character?

**A**: Modify the agent configuration in `src/chattr/app/builder.py`.

### Q: Is GPU required?

**A**: No, the LLM runs on external API. Only CPU is needed for the application.

### Q: How much memory is needed?

**A**: Minimum 2GB RAM, recommended 4GB+ depending on usage.
