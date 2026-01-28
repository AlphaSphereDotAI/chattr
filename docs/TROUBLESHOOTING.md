# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with Chattr.

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Installation Issues](#installation-issues)
- [Configuration Issues](#configuration-issues)
- [Runtime Issues](#runtime-issues)
- [Performance Issues](#performance-issues)
- [Docker Issues](#docker-issues)
- [Database Issues](#database-issues)
- [MCP Service Issues](#mcp-service-issues)
- [Getting Help](#getting-help)

## Quick Diagnostics

### Health Check Script

```bash
#!/bin/bash
echo "=== Chattr Health Check ==="

# Check Docker
echo -n "Docker: "
docker --version && echo "✓ OK" || echo "✗ FAILED"

# Check services
echo -n "Chattr service: "
curl -sf http://localhost:7860/ > /dev/null && echo "✓ OK" || echo "✗ FAILED"

echo -n "Qdrant service: "
curl -sf http://localhost:6333/ > /dev/null && echo "✓ OK" || echo "✗ FAILED"

# Check logs for errors
echo "Recent errors:"
docker-compose logs --tail=20 chattr | grep -i error || echo "No errors found"
```

### Log Collection

```bash
# Collect all logs
docker-compose logs > chattr-logs.txt

# Watch logs in real-time
docker-compose logs -f

# Check specific service
docker-compose logs chattr
docker-compose logs vector_database
```

## Installation Issues

### Issue: `uv` command not found

**Symptoms**:
```
bash: uv: command not found
```

**Solutions**:

1. Install uv:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Add to PATH:
   ```bash
   export PATH="$HOME/.cargo/bin:$PATH"
   ```

3. Restart shell:
   ```bash
   exec $SHELL
   ```

### Issue: Python version mismatch

**Symptoms**:
```
Python 3.13+ required, found 3.11
```

**Solutions**:

1. Using pyenv:
   ```bash
   pyenv install 3.13.0
   pyenv local 3.13.0
   ```

2. Using uv:
   ```bash
   uv python install 3.13
   ```

### Issue: Dependency installation fails

**Symptoms**:
```
error: Failed to download package
```

**Solutions**:

1. Clear cache:
   ```bash
   uv cache clean
   ```

2. Retry installation:
   ```bash
   uv sync --refresh
   ```

3. Check internet connection:
   ```bash
   ping pypi.org
   ```

## Configuration Issues

### Issue: MODEL__API_KEY not set

**Symptoms**:
```
ValueError: You need to provide API Key for the Model provider
```

**Solutions**:

1. Set environment variable:
   ```bash
   export MODEL__API_KEY="your-api-key"
   ```

2. Create .env file:
   ```bash
   echo "MODEL__API_KEY=your-api-key" > .env
   ```

3. Verify it's set:
   ```bash
   echo $MODEL__API_KEY
   ```

### Issue: Invalid model configuration

**Symptoms**:
```
Failed to initialize ChatOpenAI model
```

**Solutions**:

1. Check MODEL__URL is correct:
   ```bash
   echo $MODEL__URL
   ```

2. Verify API key is valid:
   ```bash
   curl -H "Authorization: Bearer $MODEL__API_KEY" $MODEL__URL/models
   ```

3. Test with different model:
   ```bash
   export MODEL__NAME="llama3-8b-8192"
   ```

### Issue: mcp.json not found

**Symptoms**:
```
WARNING: `mcp.json` not found.
```

**Solutions**:

1. Create mcp.json:
   ```bash
   cat > mcp.json << 'EOF'
   {
     "mcp_servers": []
   }
   EOF
   ```

2. Verify path:
   ```bash
   ls -la mcp.json
   ```

3. Set custom path:
   ```bash
   export MCP__PATH="/path/to/mcp.json"
   ```

## Runtime Issues

### Issue: Application won't start

**Symptoms**:
```
Error launching Gradio app
```

**Diagnostics**:

```bash
# Check port availability
netstat -tuln | grep 7860

# Check process
ps aux | grep chattr

# Check logs
docker-compose logs chattr
```

**Solutions**:

1. Kill process on port:
   ```bash
   lsof -ti:7860 | xargs kill -9
   ```

2. Use different port:
   ```bash
   export GRADIO_SERVER_PORT=8080
   ```

3. Check permissions:
   ```bash
   chmod +x src/chattr/__main__.py
   ```

### Issue: Connection timeout

**Symptoms**:
```
TimeoutError: Request timed out
```

**Solutions**:

1. Increase timeout in settings
2. Check network connectivity:
   ```bash
   ping -c 4 api.groq.com
   ```

3. Use different model endpoint
4. Check firewall settings

### Issue: Out of memory

**Symptoms**:
```
MemoryError
OSError: Cannot allocate memory
```

**Solutions**:

1. Check memory usage:
   ```bash
   docker stats
   ```

2. Increase Docker memory:
   ```bash
   # In Docker Desktop: Settings > Resources > Memory
   ```

3. Reduce batch size or use lighter model

4. Monitor memory:
   ```bash
   watch -n 1 docker stats
   ```

### Issue: Agent responses are slow

**Symptoms**:
- Long wait times for responses
- Timeouts

**Solutions**:

1. Use faster model:
   ```bash
   export MODEL__NAME="llama3-8b-8192"  # Instead of 70b
   ```

2. Disable unnecessary tools

3. Reduce context length

4. Check network latency:
   ```bash
   curl -w "@curl-format.txt" -o /dev/null -s $MODEL__URL/models
   ```

## Performance Issues

### Issue: High CPU usage

**Diagnostics**:
```bash
# Check CPU usage
docker stats

# Check processes
docker-compose top
```

**Solutions**:

1. Limit CPU usage:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
   ```

2. Scale horizontally instead of vertically

3. Use lighter model

### Issue: Slow vector search

**Symptoms**:
- Knowledge retrieval is slow
- Search timeouts

**Solutions**:

1. Check Qdrant performance:
   ```bash
   curl http://localhost:6333/metrics
   ```

2. Optimize collection:
   - Reduce vector dimensions
   - Add indexes
   - Increase memory

3. Monitor query time:
   ```bash
   docker-compose logs vector_database | grep -i "query time"
   ```

### Issue: Disk space full

**Symptoms**:
```
OSError: No space left on device
```

**Solutions**:

1. Check disk usage:
   ```bash
   df -h
   docker system df
   ```

2. Clean Docker:
   ```bash
   docker system prune -a
   docker volume prune
   ```

3. Clear logs:
   ```bash
   docker-compose down
   rm -rf logs/*
   docker-compose up -d
   ```

## Docker Issues

### Issue: Docker daemon not running

**Symptoms**:
```
Cannot connect to the Docker daemon
```

**Solutions**:

1. Start Docker:
   ```bash
   # Linux
   sudo systemctl start docker
   
   # macOS
   open -a Docker
   ```

2. Check status:
   ```bash
   docker info
   ```

### Issue: Permission denied

**Symptoms**:
```
Permission denied while trying to connect to Docker daemon
```

**Solutions**:

1. Add user to docker group:
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

2. Or use sudo:
   ```bash
   sudo docker-compose up
   ```

### Issue: Port already in use

**Symptoms**:
```
Bind for 0.0.0.0:7860 failed: port is already allocated
```

**Solutions**:

1. Find process using port:
   ```bash
   lsof -i :7860
   ```

2. Kill the process:
   ```bash
   kill -9 <PID>
   ```

3. Use different port:
   ```yaml
   ports:
     - "8080:7860"
   ```

### Issue: Container keeps restarting

**Symptoms**:
```
chattr_1 exited with code 1
```

**Diagnostics**:
```bash
# Check logs
docker-compose logs chattr

# Check events
docker events --filter container=chattr

# Inspect container
docker inspect chattr
```

**Solutions**:

1. Check configuration
2. Verify environment variables
3. Check resource limits
4. Review error logs

## Database Issues

### Issue: Qdrant won't start

**Symptoms**:
```
vector_database_1 exited with code 1
```

**Solutions**:

1. Check logs:
   ```bash
   docker-compose logs vector_database
   ```

2. Clear data and restart:
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

3. Check permissions:
   ```bash
   ls -la volumes/qdrant
   ```

### Issue: Collection not found

**Symptoms**:
```
Collection 'chattr' not found
```

**Solutions**:

1. Create collection:
   ```bash
   curl -X PUT http://localhost:6333/collections/chattr \
     -H 'Content-Type: application/json' \
     -d '{
       "vectors": {
         "size": 384,
         "distance": "Cosine"
       }
     }'
   ```

2. Verify collection:
   ```bash
   curl http://localhost:6333/collections/chattr
   ```

### Issue: Cannot connect to Qdrant

**Symptoms**:
```
ConnectionError: Cannot connect to Qdrant
```

**Solutions**:

1. Check Qdrant is running:
   ```bash
   curl http://localhost:6333/
   ```

2. Verify network:
   ```bash
   docker network ls
   docker network inspect chattr_default
   ```

3. Check URL in settings:
   ```bash
   echo $VECTOR_DATABASE__URL
   ```

## MCP Service Issues

### Issue: MCP tools not available

**Symptoms**:
```
No MCP tools found
```

**Solutions**:

1. Check mcp.json configuration
2. Verify service URLs are accessible:
   ```bash
   curl http://localhost:8001/gradio_api/mcp/sse
   ```

3. Check services are running:
   ```bash
   docker-compose ps
   ```

### Issue: Audio generation fails

**Symptoms**:
```
Tool call failed: generate_audio_for_text
```

**Solutions**:

1. Check voice generator service:
   ```bash
   docker-compose logs voice_generator
   ```

2. Test service directly:
   ```bash
   curl -X POST http://localhost:8001/api/predict
   ```

3. Verify MCP configuration

### Issue: Video generation fails

**Symptoms**:
```
Tool call failed: generate_video_mcp
```

**Solutions**:

1. Check video generator service:
   ```bash
   docker-compose logs video_generator
   ```

2. Verify GPU availability (if needed)

3. Check disk space for output

4. Increase timeout

## Common Error Messages

### ValidationError

```
ValidationError: 1 validation error for Settings
```

**Cause**: Invalid configuration value

**Fix**: Check environment variables match expected types

### OSError

```
OSError: [Errno 24] Too many open files
```

**Cause**: File descriptor limit reached

**Fix**: Increase limit:
```bash
ulimit -n 4096
```

### ImportError

```
ImportError: cannot import name 'X' from 'Y'
```

**Cause**: Dependency version mismatch

**Fix**: Reinstall dependencies:
```bash
uv sync --refresh
```

## Debug Mode

Enable debug mode for detailed logs:

```bash
# Environment variable
export DEBUG=true

# In code
settings = Settings(debug=True)
```

View detailed logs:
```bash
tail -f logs/chattr.log
```

## Getting Help

### Before Asking for Help

1. Check this troubleshooting guide
2. Search existing issues
3. Check recent changes
4. Collect relevant logs
5. Try minimal reproduction

### Information to Include

When reporting issues, include:

- Chattr version
- Python version
- OS and version
- Docker version
- Error messages (full stack trace)
- Configuration (sanitized)
- Steps to reproduce
- Expected vs actual behavior

### Where to Get Help

1. **GitHub Issues**: https://github.com/AlphaSphereDotAI/chattr/issues
2. **Discussions**: https://github.com/AlphaSphereDotAI/chattr/discussions
3. **Email**: mohamed.hisham.abdelzaher@gmail.com

### Issue Template

```markdown
**Description**
Brief description of the problem

**Environment**
- OS: Ubuntu 22.04
- Python: 3.13.0
- Docker: 24.0.5
- Chattr: 0.0.100

**Steps to Reproduce**
1. Step one
2. Step two
3. ...

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Logs**
```
Paste relevant logs here
```

**Additional Context**
Any other relevant information
```

## Useful Commands

```bash
# Health check
curl -f http://localhost:7860/ && echo "OK" || echo "FAIL"

# View logs
docker-compose logs -f --tail=100

# Restart service
docker-compose restart chattr

# Full reset
docker-compose down -v && docker-compose up -d

# Check resource usage
docker stats --no-stream

# Exec into container
docker-compose exec chattr /bin/sh

# Test configuration
uv run python -c "from chattr.app.settings import Settings; print(Settings())"

# Check dependencies
uv pip list

# Test model connection
curl -H "Authorization: Bearer $MODEL__API_KEY" $MODEL__URL/models
```

## Prevention Tips

1. **Always use version control**
2. **Test configuration changes in isolation**
3. **Monitor resource usage**
4. **Keep dependencies updated**
5. **Regular backups**
6. **Use health checks**
7. **Implement proper logging**
8. **Document custom changes**

For more information, refer to the [Documentation](../README.md).
