# Deployment Guide

This guide covers deploying Chattr in various environments from development to production.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Cloud Deployments](#cloud-deployments)
- [Configuration](#configuration)
- [Scaling](#scaling)
- [Security](#security)
- [Monitoring](#monitoring)
- [Backup and Recovery](#backup-and-recovery)

## Prerequisites

### System Requirements

#### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 10GB
- **Network**: Stable internet connection

#### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 50GB SSD
- **Network**: High-speed connection

### Software Requirements

- Docker 24.0+
- Docker Compose 2.20+
- (Optional) Kubernetes 1.28+
- (Optional) Helm 3.0+

## Docker Deployment

### Simple Deployment

The easiest way to deploy Chattr is using Docker Compose.

#### 1. Clone Repository

```bash
git clone https://github.com/AlphaSphereDotAI/chattr.git
cd chattr
```

#### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your configuration
nano .env
```

Required variables:
```env
MODEL__API_KEY=your-api-key-here
MODEL__URL=https://api.groq.com/openai/v1
MODEL__NAME=llama3-70b-8192
```

#### 3. Start Services

```bash
docker-compose up -d
```

#### 4. Verify Deployment

```bash
# Check services are running
docker-compose ps

# Check logs
docker-compose logs -f chattr

# Test health
curl http://localhost:7860/
```

#### 5. Access Application

Open browser to: `http://localhost:7860`

### Production Deployment

For production, use the optimized configuration:

#### docker-compose.prod.yaml

```yaml
name: Chattr-Production

services:
  chattr:
    image: alphaspheredotai/chattr:latest
    restart: always
    volumes:
      - ./logs:/home/nonroot/logs
      - ./assets:/home/nonroot/assets
      - fastembed:/home/nonroot/fastembed
    environment:
      MODEL__URL: ${MODEL__URL}
      MODEL__NAME: ${MODEL__NAME}
      MODEL__API_KEY: ${MODEL__API_KEY}
      VECTOR_DATABASE__URL: http://vector_database:6333
      VECTOR_DATABASE__NAME: production
    ports:
      - "7860:7860"
    depends_on:
      vector_database:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7860/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  vector_database:
    image: qdrant/qdrant:latest
    restart: always
    volumes:
      - qdrant_storage:/qdrant/storage
    environment:
      QDRANT_ALLOW_RECOVERY_MODE: "true"
    ports:
      - "6333:6333"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/"]
      interval: 30s
      timeout: 5s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - chattr

volumes:
  qdrant_storage:
    driver: local
  fastembed:
    driver: local
```

#### Launch Production

```bash
docker-compose -f docker-compose.prod.yaml up -d
```

### Nginx Configuration

Create `nginx.conf` for reverse proxy:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream chattr_backend {
        server chattr:7860;
    }

    server {
        listen 80;
        server_name your-domain.com;

        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;

        # Proxy settings
        location / {
            proxy_pass http://chattr_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";

            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Rate limiting
        limit_req_zone $binary_remote_addr zone=chattr_limit:10m rate=10r/s;
        limit_req zone=chattr_limit burst=20 nodelay;

        # File size limit
        client_max_body_size 10M;
    }
}
```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.28+)
- kubectl configured
- Helm 3.0+ (optional)

### Deployment Files

#### namespace.yaml

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: chattr
```

#### configmap.yaml

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: chattr-config
  namespace: chattr
data:
  MODEL__URL: "https://api.groq.com/openai/v1"
  MODEL__NAME: "llama3-70b-8192"
  VECTOR_DATABASE__URL: "http://qdrant:6333"
  VECTOR_DATABASE__NAME: "chattr"
```

#### secret.yaml

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: chattr-secrets
  namespace: chattr
type: Opaque
stringData:
  MODEL__API_KEY: "your-api-key-here"
```

#### deployment.yaml

```yaml
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
        image: alphaspheredotai/chattr:latest
        ports:
        - containerPort: 7860
          name: http
        env:
        - name: MODEL__API_KEY
          valueFrom:
            secretKeyRef:
              name: chattr-secrets
              key: MODEL__API_KEY
        envFrom:
        - configMapRef:
            name: chattr-config
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /
            port: 7860
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /
            port: 7860
          initialDelaySeconds: 30
          periodSeconds: 10
        volumeMounts:
        - name: assets
          mountPath: /home/nonroot/assets
      volumes:
      - name: assets
        persistentVolumeClaim:
          claimName: chattr-assets-pvc
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: chattr-assets-pvc
  namespace: chattr
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
```

#### service.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: chattr
  namespace: chattr
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 7860
    protocol: TCP
  selector:
    app: chattr
```

#### qdrant-deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qdrant
  namespace: chattr
spec:
  replicas: 1
  selector:
    matchLabels:
      app: qdrant
  template:
    metadata:
      labels:
        app: qdrant
    spec:
      containers:
      - name: qdrant
        image: qdrant/qdrant:latest
        ports:
        - containerPort: 6333
        - containerPort: 6334
        volumeMounts:
        - name: qdrant-storage
          mountPath: /qdrant/storage
      volumes:
      - name: qdrant-storage
        persistentVolumeClaim:
          claimName: qdrant-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: qdrant
  namespace: chattr
spec:
  ports:
  - port: 6333
    targetPort: 6333
    name: http
  - port: 6334
    targetPort: 6334
    name: grpc
  selector:
    app: qdrant
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: qdrant-pvc
  namespace: chattr
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
```

### Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f namespace.yaml

# Create secrets and config
kubectl apply -f secret.yaml
kubectl apply -f configmap.yaml

# Deploy Qdrant
kubectl apply -f qdrant-deployment.yaml

# Deploy Chattr
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Check status
kubectl get pods -n chattr
kubectl get services -n chattr

# Get external IP
kubectl get service chattr -n chattr
```

## Cloud Deployments

### AWS ECS

```bash
# Build and push image
aws ecr get-login-password | docker login --username AWS --password-stdin
docker build -t chattr:latest .
docker tag chattr:latest YOUR_ECR_REPO:latest
docker push YOUR_ECR_REPO:latest

# Create ECS task definition and service
aws ecs create-service --cluster chattr-cluster \
  --service-name chattr \
  --task-definition chattr-task \
  --desired-count 2 \
  --launch-type FARGATE
```

### Google Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/chattr
gcloud run deploy chattr \
  --image gcr.io/PROJECT_ID/chattr \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Container Instances

```bash
az container create \
  --resource-group chattr-rg \
  --name chattr \
  --image alphaspheredotai/chattr:latest \
  --dns-name-label chattr \
  --ports 7860 \
  --environment-variables \
    MODEL__API_KEY=$MODEL_API_KEY \
    MODEL__URL=$MODEL_URL
```

## Configuration

### Environment Variables

See [Configuration Guide](../README.md#configuration) for full list.

### Secrets Management

#### Docker Secrets

```bash
echo "api-key-value" | docker secret create model_api_key -
```

```yaml
services:
  chattr:
    secrets:
      - model_api_key
    environment:
      MODEL__API_KEY_FILE: /run/secrets/model_api_key

secrets:
  model_api_key:
    external: true
```

#### Kubernetes Secrets

```bash
kubectl create secret generic chattr-secrets \
  --from-literal=MODEL__API_KEY='your-key' \
  -n chattr
```

## Scaling

### Horizontal Scaling

#### Docker Swarm

```bash
docker service scale chattr=3
```

#### Kubernetes

```bash
kubectl scale deployment chattr --replicas=5 -n chattr
```

### Auto-scaling

#### Kubernetes HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: chattr-hpa
  namespace: chattr
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: chattr
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Security

### TLS/SSL

Always use HTTPS in production. Use Let's Encrypt for free certificates:

```bash
certbot certonly --standalone -d your-domain.com
```

### Network Security

- Use firewall rules to restrict access
- Deploy in private subnet
- Use VPN for admin access

### API Key Security

- Never commit keys to git
- Use secrets management
- Rotate keys regularly
- Use environment-specific keys

## Monitoring

### Logging

```bash
# Docker logs
docker-compose logs -f chattr

# Kubernetes logs
kubectl logs -f deployment/chattr -n chattr
```

### Metrics

Use Prometheus and Grafana:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'chattr'
    static_configs:
      - targets: ['chattr:7860']
```

### Alerting

Configure alerts for:
- High memory usage
- Service downtime
- Error rates
- Response times

## Backup and Recovery

### Qdrant Backup

```bash
# Backup
docker exec qdrant_container \
  tar czf /tmp/qdrant-backup.tar.gz /qdrant/storage

docker cp qdrant_container:/tmp/qdrant-backup.tar.gz ./backups/

# Restore
docker cp ./backups/qdrant-backup.tar.gz qdrant_container:/tmp/
docker exec qdrant_container \
  tar xzf /tmp/qdrant-backup.tar.gz -C /
```

### Assets Backup

```bash
# Backup assets
tar czf assets-backup.tar.gz assets/

# Restore
tar xzf assets-backup.tar.gz
```

### Automated Backups

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
docker exec qdrant tar czf - /qdrant/storage > "qdrant-$DATE.tar.gz"
tar czf "assets-$DATE.tar.gz" assets/
```

Add to crontab:
```bash
0 2 * * * /path/to/backup.sh
```

## Troubleshooting

### Common Issues

**Service won't start:**
- Check environment variables
- Verify API key is valid
- Check resource limits

**Poor performance:**
- Increase memory allocation
- Scale horizontally
- Check network latency

**Database connection errors:**
- Verify Qdrant is running
- Check network connectivity
- Verify port mappings

For more help, see [Troubleshooting Guide](TROUBLESHOOTING.md).

## Support

- GitHub Issues: https://github.com/AlphaSphereDotAI/chattr/issues
- Documentation: https://github.com/AlphaSphereDotAI/chattr/docs
- Email: mohamed.hisham.abdelzaher@gmail.com
