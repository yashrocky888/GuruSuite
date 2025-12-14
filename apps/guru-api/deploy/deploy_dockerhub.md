# Phase 21: Docker Hub Deployment Guide

## Push Docker Image to Docker Hub

### Step 1: Build Docker Image

```bash
# Build the image
docker build -t guru-api:latest .

# Tag for Docker Hub
docker tag guru-api:latest yourusername/guru-api:latest
docker tag guru-api:latest yourusername/guru-api:v2.1.0
```

### Step 2: Login to Docker Hub

```bash
docker login
# Enter your Docker Hub username and password
```

### Step 3: Push to Docker Hub

```bash
# Push latest
docker push yourusername/guru-api:latest

# Push versioned tag
docker push yourusername/guru-api:v2.1.0
```

### Step 4: Pull and Run on Server

On your server:

```bash
# Pull image
docker pull yourusername/guru-api:latest

# Run container
docker run -d \
  --name guru-api \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  yourusername/guru-api:latest
```

### Step 5: Using Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  guru-api:
    image: yourusername/guru-api:latest
    container_name: guru-api
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

Run:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Automated Builds

### Setup Automated Builds on Docker Hub

1. Go to Docker Hub → Create Repository
2. Connect to GitHub repository
3. Enable "Build Rules"
4. Docker Hub will automatically build on push to main branch

## Versioning Strategy

- `latest`: Always points to latest stable version
- `v2.1.0`: Specific version tag
- `v2.1`: Minor version tag
- `v2`: Major version tag

## Updating Production

```bash
# Pull latest
docker pull yourusername/guru-api:latest

# Stop and remove old container
docker stop guru-api
docker rm guru-api

# Run new container
docker run -d \
  --name guru-api \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  yourusername/guru-api:latest
```

Or with docker-compose:

```bash
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

