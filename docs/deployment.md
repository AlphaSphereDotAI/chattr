# Deployment Guide

This guide covers deploying Chattr to various environments.

## Deployment Options

- **Docker**: Containerized deployment (recommended)
- **Cloud Platforms**: AWS, GCP, Azure, Hugging Face Spaces
- **Kubernetes**: Orchestrated container deployment
- **Bare Metal**: Direct installation on servers

## Docker Deployment

### Basic Docker Setup

#### Using docker-compose (Recommended)

The simplest way to deploy Chattr with all dependencies:

```bash
# Clone repository
git clone https://github.com/AlphaSphereDotAI/chattr.git
cd chattr

# Create .env file
cat > .env << EOF
MODEL__API_KEY=your_api_key_here
MODEL__URL=https://api.groq.com/openai/v1
MODEL__NAME=llama3-70b-8192
EOF

# Start services
docker-compose up -d

# View logs
docker-compose logs -f chattr

# Stop services
docker-compose down
```

The docker-compose setup includes:
- Chattr application on port 7860
- Redis for memory storage
- Qdrant for vector database
- Persistent volumes for data

#### Using Docker CLI

Build and run manually:

```bash
# Build image
docker build -t chattr:latest \
  --build-arg INSTALL_SOURCE="git+https://github.com/AlphaSphereDotAI/chattr.git" \
  --build-arg PYTHON_VERSION="3.13" \
  .

# Run container
docker run -d \
  --name chattr \
  -p 7860:7860 \
  -e MODEL__API_KEY=your_key \
  -v $(pwd)/assets:/home/nonroot/assets \
  -v $(pwd)/logs:/home/nonroot/logs \
  chattr:latest
```

### Production docker-compose

For production, use a more robust configuration:

```yaml
version: '3.8'

services:
  chattr:
    image: chattr:latest
    build:
      context: .
      args:
        INSTALL_SOURCE: "chattr"
        PYTHON_VERSION: "3.13"
    ports:
      - "7860:7860"
    environment:
      # Model configuration
      - MODEL__API_KEY=${MODEL__API_KEY}
      - MODEL__URL=${MODEL__URL:-https://api.groq.com/openai/v1}
      - MODEL__NAME=${MODEL__NAME:-llama3-70b-8192}
      - MODEL__TEMPERATURE=${MODEL__TEMPERATURE:-0.0}
      
      # Service URLs
      - SHORT_TERM_MEMORY__URL=redis://redis:6379
      - VOICE_GENERATOR_MCP__URL=${VOICE_GENERATOR_MCP__URL}
      - VIDEO_GENERATOR_MCP__URL=${VIDEO_GENERATOR_MCP__URL}
      
      # Gradio configuration
      - GRADIO_SERVER_NAME=0.0.0.0
      - GRADIO_SERVER_PORT=7860
    
    volumes:
      - ./assets:/home/nonroot/assets
      - ./logs:/home/nonroot/logs
      - fastembed-cache:/home/nonroot/fastembed
    
    depends_on:
      redis:
        condition: service_healthy
      qdrant:
        condition: service_healthy
    
    restart: unless-stopped
    
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7860"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant-data:/qdrant/storage
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/healthz"]
      interval: 10s
      timeout: 3s
      retries: 3

volumes:
  redis-data:
    driver: local
  qdrant-data:
    driver: local
  fastembed-cache:
    driver: local
```

## Cloud Deployments

### Hugging Face Spaces

Chattr is configured for Hugging Face Spaces deployment:

1. **Fork the repository** on GitHub

2. **Create a new Space** on Hugging Face:
   - SDK: Docker
   - App Port: 7860

3. **Set environment variables** in Space settings:
   ```
   MODEL__API_KEY=your_key
   MODEL__URL=https://api.groq.com/openai/v1
   MODEL__NAME=llama3-70b-8192
   ```

4. **Link to GitHub repository** for automatic deployments

The `README.md` header configures the Space:
```yaml
---
title: Chattr
emoji: 💬
sdk: docker
app_port: 7860
---
```

### AWS Deployment

#### AWS EC2

Deploy on EC2 instance:

```bash
# Launch EC2 instance (Amazon Linux 2 or Ubuntu)
# SSH into instance

# Install Docker
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone and deploy
git clone https://github.com/AlphaSphereDotAI/chattr.git
cd chattr

# Configure environment
cat > .env << EOF
MODEL__API_KEY=$(aws secretsmanager get-secret-value --secret-id chattr/api-key --query SecretString --output text)
EOF

# Start services
docker-compose up -d

# Configure security group to allow port 7860
```

#### AWS ECS (Elastic Container Service)

1. **Build and push image**:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   
   docker build -t chattr:latest .
   docker tag chattr:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/chattr:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/chattr:latest
   ```

2. **Create ECS task definition**
3. **Create ECS service**
4. **Configure load balancer**
5. **Set environment variables** from AWS Secrets Manager

### Google Cloud Platform

#### Cloud Run

Deploy serverless container:

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/chattr

# Deploy to Cloud Run
gcloud run deploy chattr \
  --image gcr.io/PROJECT_ID/chattr \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 7860 \
  --set-env-vars MODEL__API_KEY=your_key
```

#### GKE (Google Kubernetes Engine)

See Kubernetes section below.

### Azure Deployment

#### Azure Container Instances

```bash
# Create resource group
az group create --name chattr-rg --location eastus

# Create container
az container create \
  --resource-group chattr-rg \
  --name chattr \
  --image chattr:latest \
  --dns-name-label chattr-app \
  --ports 7860 \
  --environment-variables \
    MODEL__API_KEY=your_key \
    MODEL__URL=https://api.groq.com/openai/v1
```

## Kubernetes Deployment

### Basic Deployment

Create Kubernetes manifests:

#### 1. Namespace

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: chattr
```

#### 2. ConfigMap

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: chattr-config
  namespace: chattr
data:
  MODEL__URL: "https://api.groq.com/openai/v1"
  MODEL__NAME: "llama3-70b-8192"
  SHORT_TERM_MEMORY__URL: "redis://redis:6379"
```

#### 3. Secret

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: chattr-secret
  namespace: chattr
type: Opaque
stringData:
  MODEL__API_KEY: "your_api_key_here"
```

#### 4. Redis Deployment

```yaml
# redis.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: chattr
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        volumeMounts:
        - name: redis-data
          mountPath: /data
      volumes:
      - name: redis-data
        persistentVolumeClaim:
          claimName: redis-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: chattr
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
```

#### 5. Chattr Deployment

```yaml
# chattr.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chattr
  namespace: chattr
spec:
  replicas: 2
  selector:
    matchLabels:
      app: chattr
  template:
    metadata:
      labels:
        app: chattr
    spec:
      containers:
      - name: chattr
        image: chattr:latest
        ports:
        - containerPort: 7860
        env:
        - name: MODEL__API_KEY
          valueFrom:
            secretKeyRef:
              name: chattr-secret
              key: MODEL__API_KEY
        envFrom:
        - configMapRef:
            name: chattr-config
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /
            port: 7860
          initialDelaySeconds: 60
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 7860
          initialDelaySeconds: 30
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: chattr
  namespace: chattr
spec:
  type: LoadBalancer
  selector:
    app: chattr
  ports:
  - port: 80
    targetPort: 7860
```

#### Deploy to Kubernetes

```bash
# Apply manifests
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f redis.yaml
kubectl apply -f chattr.yaml

# Check status
kubectl get pods -n chattr
kubectl get svc -n chattr

# View logs
kubectl logs -f deployment/chattr -n chattr
```

## Environment Configuration

### Production Environment Variables

```bash
# Required
MODEL__API_KEY=<secret>

# Recommended for production
MODEL__URL=https://api.openai.com/v1
MODEL__NAME=gpt-4
MODEL__TEMPERATURE=0.0

# Redis with persistence
SHORT_TERM_MEMORY__URL=redis://:password@redis-cluster:6379/0

# Qdrant cluster
VECTOR_DATABASE__NAME=chattr_production

# MCP services
VOICE_GENERATOR_MCP__URL=http://voice-service:8001/gradio_api/mcp/sse
VIDEO_GENERATOR_MCP__URL=http://video-service:8002/gradio_api/mcp/sse

# Production directories
DIRECTORY__ASSETS=/data/assets
DIRECTORY__LOG=/data/logs
```

## Monitoring and Logging

### Logging

Configure logging for production:

```python
# Set log level via environment
LOGGING_LEVEL=INFO

# Or in code
from chattr.app.settings import logger
logger.setLevel("INFO")
```

### Health Checks

Chattr exposes Gradio's built-in health endpoint:

```bash
curl http://localhost:7860/
```

For Kubernetes:
```yaml
livenessProbe:
  httpGet:
    path: /
    port: 7860
  initialDelaySeconds: 60
  periodSeconds: 10
```

### Metrics

Monitor these metrics:

- Request rate
- Response time
- Error rate
- Memory usage
- CPU usage
- Redis connection pool
- Model API latency

## Security Considerations

### Secrets Management

Never hardcode secrets:

```bash
# Use environment variables
export MODEL__API_KEY=$(cat secret.key)

# Or secrets management systems
export MODEL__API_KEY=$(aws secretsmanager get-secret-value --secret-id chattr/api-key)
```

### Network Security

- Use HTTPS in production
- Restrict access with firewalls
- Use VPC/private networks
- Enable CORS appropriately

### Container Security

- Run as non-root user (already configured)
- Scan images for vulnerabilities
- Keep base images updated
- Minimize image size

## Scaling

### Horizontal Scaling

Chattr is stateless and can be scaled horizontally:

```bash
# Docker Compose
docker-compose up --scale chattr=3

# Kubernetes
kubectl scale deployment chattr --replicas=5 -n chattr
```

### Database Scaling

- **Redis**: Use Redis Cluster or Sentinel for HA
- **Qdrant**: Deploy Qdrant cluster for distributed search

## Backup and Recovery

### Data Backup

```bash
# Backup Redis
docker exec redis redis-cli SAVE
docker cp redis:/data/dump.rdb ./backup/

# Backup Qdrant
docker exec qdrant tar czf /tmp/qdrant-backup.tar.gz /qdrant/storage
docker cp qdrant:/tmp/qdrant-backup.tar.gz ./backup/
```

### Disaster Recovery

1. Maintain backups of:
   - Redis data
   - Qdrant collections
   - Configuration files
   - Asset directories

2. Document recovery procedures
3. Test recovery regularly

## Troubleshooting Deployments

### Container won't start

```bash
# Check logs
docker logs chattr

# Check environment
docker exec chattr env

# Verify connectivity
docker exec chattr curl http://redis:6379
```

### High memory usage

- Monitor FastEmbed cache size
- Limit conversation history
- Configure Qdrant memory limits
- Set container memory limits

### Slow responses

- Check model API latency
- Verify network connectivity
- Monitor Redis performance
- Review Qdrant query performance

## Best Practices

1. **Use environment-specific configs**
2. **Enable health checks**
3. **Set resource limits**
4. **Implement logging and monitoring**
5. **Use secrets management**
6. **Enable HTTPS**
7. **Regular backups**
8. **Test disaster recovery**
9. **Document deployment procedures**
10. **Monitor costs and usage**
