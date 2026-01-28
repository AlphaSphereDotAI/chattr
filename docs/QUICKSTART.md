# Quick Start Guide

Get Chattr running in 5 minutes! ⚡

## Prerequisites

You need ONE of the following:

- **Docker & Docker Compose** (Recommended - Easiest)
- **Python 3.13+ & uv** (For local development)

And:
- An API key from an OpenAI-compatible provider (Groq, OpenAI, Google Gemini, etc.)

## Option 1: Docker (Recommended)

### Step 1: Clone the Repository

```bash
git clone https://github.com/AlphaSphereDotAI/chattr.git
cd chattr
```

### Step 2: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API key
nano .env  # or use your preferred editor
```

**Minimum required configuration in `.env`:**
```env
MODEL__API_KEY=your-api-key-here
```

### Step 3: Launch with Docker Compose

```bash
docker-compose up -d
```

This will:
- Pull necessary Docker images
- Start Chattr application
- Start Qdrant vector database
- Start audio/video generator services (if configured)

### Step 4: Access the Application

Open your browser to: **http://localhost:7860**

That's it! 🎉

### Verify Installation

```bash
# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f chattr
```

## Option 2: Local Python Installation

### Step 1: Install Prerequisites

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart your shell
exec $SHELL
```

### Step 2: Clone and Install

```bash
# Clone repository
git clone https://github.com/AlphaSphereDotAI/chattr.git
cd chattr

# Install dependencies
uv sync
```

### Step 3: Configure Environment

```bash
# Set required environment variables
export MODEL__API_KEY="your-api-key-here"
export MODEL__URL="https://api.groq.com/openai/v1"
export MODEL__NAME="llama3-70b-8192"
```

### Step 4: Start Qdrant (Separate Terminal)

```bash
docker run -p 6333:6333 qdrant/qdrant:latest
```

### Step 5: Run Chattr

```bash
uv run chattr
```

### Step 6: Access the Application

Open your browser to: **http://localhost:7860**

## First Conversation

1. Open http://localhost:7860 in your browser
2. Type a message like: "Hello! Who are you?"
3. Press Enter or click Send
4. Watch as the character responds with:
   - Text response
   - Generated audio (voice)
   - Generated video (if configured)

## Common Issues

### Port Already in Use

```bash
# Find what's using port 7860
lsof -i :7860

# Kill the process
kill -9 <PID>

# Or use a different port
export GRADIO_SERVER_PORT=8080
```

### API Key Not Working

1. Verify your API key is correct
2. Check it has sufficient credits/quota
3. Test with curl:
   ```bash
   curl -H "Authorization: Bearer $MODEL__API_KEY" \
        "$MODEL__URL/models"
   ```

### Services Not Starting

```bash
# Check Docker is running
docker info

# Restart services
docker-compose restart

# View detailed logs
docker-compose logs
```

## Next Steps

Now that Chattr is running:

1. **Explore Features**
   - Try different types of questions
   - Test multi-modal responses
   - Review conversation history

2. **Customize Configuration**
   - Change character (Napoleon, Einstein, or custom)
   - Adjust model parameters
   - Configure additional services

3. **Read Documentation**
   - [Full README](../README.md)
   - [Configuration Guide](../README.md#configuration)
   - [API Documentation](API.md)

4. **Deploy to Production**
   - See [Deployment Guide](DEPLOYMENT.md)
   - Set up monitoring
   - Configure SSL/HTTPS

## Getting Help

- **Documentation**: [docs/INDEX.md](INDEX.md)
- **Troubleshooting**: [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Issues**: https://github.com/AlphaSphereDotAI/chattr/issues

## Configuration Examples

### Using Groq (Fast, Free Tier)

```env
MODEL__URL=https://api.groq.com/openai/v1
MODEL__NAME=llama3-70b-8192
MODEL__API_KEY=your-groq-api-key
```

### Using OpenAI

```env
MODEL__URL=https://api.openai.com/v1
MODEL__NAME=gpt-4
MODEL__API_KEY=your-openai-api-key
```

### Using Google Gemini

```env
MODEL__URL=https://generativelanguage.googleapis.com/v1beta/openai
MODEL__NAME=gemini-2.0-flash-exp
MODEL__API_KEY=your-google-api-key
```

## Development Mode

For development with hot reload:

```bash
# Install dev dependencies
uv sync

# Run with auto-reload
uv run chattr
```

## Stopping Chattr

### Docker

```bash
# Stop services
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v
```

### Local

Press `Ctrl+C` in the terminal where Chattr is running

## Useful Commands

```bash
# View logs
docker-compose logs -f

# Restart single service
docker-compose restart chattr

# Check resource usage
docker stats

# Access container shell
docker-compose exec chattr /bin/sh

# Update images
docker-compose pull
docker-compose up -d
```

## Tips for Best Experience

1. **Use a good model**: llama3-70b-8192 or gpt-4 for best results
2. **Set temperature to 0**: For consistent, factual responses
3. **Enable MCP services**: For full multi-modal experience
4. **Monitor resources**: Ensure adequate RAM and CPU
5. **Use HTTPS**: In production deployments

## What's Next?

- ⚙️ [Customize Configuration](../README.md#configuration)
- 🚀 [Deploy to Production](DEPLOYMENT.md)
- 🔧 [Develop & Contribute](DEVELOPMENT.md)
- 📚 [Read Full Documentation](INDEX.md)

---

**Congratulations!** You now have Chattr running! 🎉

For more detailed information, see the [complete documentation](INDEX.md).
