# 🚀 Guru API Deployment Guide

## Quick Start - Choose Your Deployment Method

### Option 1: Docker (Easiest - Recommended) ⭐
### Option 2: Direct Python (Local/Development)
### Option 3: AWS EC2 (Production Server)
### Option 4: Docker Hub (Cloud Deployment)

---

## 🐳 Option 1: Docker Deployment (Recommended)

### Prerequisites
- Docker installed
- Docker Compose installed

### Steps

#### 1. Create Environment File

```bash
# Copy and edit environment variables
cp .env.example .env
nano .env  # or use your favorite editor
```

**Required variables in `.env`:**
```bash
API_KEYS=your-secret-api-key-1,your-secret-api-key-2
DEPLOYMENT_ENV=production
LOG_LEVEL=INFO
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_DAY=1000
```

#### 2. Build and Run

```bash
# Build Docker image
docker build -t guru-api:latest .

# Run with Docker Compose
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

#### 3. Test Deployment

```bash
# Health check
curl http://localhost:8000/api/health

# Test with API key
curl -X POST http://localhost:8000/api/kundali/full \
  -H "x-api-key: your-secret-api-key-1" \
  -H "Content-Type: application/json" \
  -d '{
    "birth_date": "1990-01-15",
    "birth_time": "10:30",
    "birth_latitude": 28.6139,
    "birth_longitude": 77.2090,
    "timezone": "Asia/Kolkata"
  }'
```

#### 4. Stop/Start/Restart

```bash
# Stop
docker-compose down

# Start
docker-compose up -d

# Restart
docker-compose restart
```

---

## 🐍 Option 2: Direct Python Deployment

### Prerequisites
- Python 3.11+
- Virtual environment

### Steps

#### 1. Setup Environment

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
nano .env  # Edit with your values
```

#### 2. Run Application

```bash
# Development mode (single worker, auto-reload)
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Production mode (multiple workers)
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 3. Using Start Script

```bash
# Make executable
chmod +x deploy/start.sh

# Run
./deploy/start.sh
```

---

## ☁️ Option 3: AWS EC2 Deployment

### Prerequisites
- AWS account
- EC2 instance (Ubuntu 22.04 recommended)
- SSH access to EC2

### Quick Steps

#### 1. Connect to EC2

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

#### 2. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip git

# Install Nginx (for reverse proxy)
sudo apt install -y nginx
```

#### 3. Clone and Setup

```bash
# Clone your repository
git clone https://github.com/yourusername/guru-api.git
cd guru-api

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env
# Add your API_KEYS and other variables
```

#### 4. Setup Nginx Reverse Proxy

```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/guru-api
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or EC2 IP

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart:

```bash
sudo ln -s /etc/nginx/sites-available/guru-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 5. Setup SSL (Optional but Recommended)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is automatic
```

#### 6. Create Systemd Service

```bash
sudo nano /etc/systemd/system/guru-api.service
```

Add:

```ini
[Unit]
Description=Guru API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/guru-api
Environment="PATH=/home/ubuntu/guru-api/venv/bin"
ExecStart=/home/ubuntu/guru-api/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable guru-api
sudo systemctl start guru-api
sudo systemctl status guru-api
```

#### 7. Configure Firewall

```bash
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

#### 8. Monitor

```bash
# View logs
tail -f logs/guru_api.log
sudo journalctl -u guru-api -f

# Check status
sudo systemctl status guru-api
```

---

## 🐋 Option 4: Docker Hub Deployment

### Steps

#### 1. Build and Tag Image

```bash
# Build
docker build -t guru-api:latest .

# Tag for Docker Hub
docker tag guru-api:latest yourusername/guru-api:latest
docker tag guru-api:latest yourusername/guru-api:v2.1.0
```

#### 2. Push to Docker Hub

```bash
# Login
docker login

# Push
docker push yourusername/guru-api:latest
docker push yourusername/guru-api:v2.1.0
```

#### 3. Pull and Run on Server

On your server:

```bash
# Pull
docker pull yourusername/guru-api:latest

# Run
docker run -d \
  --name guru-api \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  yourusername/guru-api:latest
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file with:

```bash
# Required
API_KEYS=key1,key2,key3                    # Comma-separated API keys
DEPLOYMENT_ENV=production                   # or "development"

# Optional
LOG_LEVEL=INFO                              # DEBUG, INFO, WARNING, ERROR
RATE_LIMIT_PER_MINUTE=60                    # Requests per minute
RATE_LIMIT_PER_DAY=1000                     # Requests per day
API_HOST=0.0.0.0                            # Server host
API_PORT=8000                               # Server port
WORKERS=4                                   # Number of workers
CORS_ORIGINS=https://yourdomain.com         # Comma-separated origins

# Database (if using)
DATABASE_URL=postgresql://user:pass@localhost:5432/guru_db

# JWT (if using)
JWT_SECRET=your-jwt-secret-key
```

### Generate API Keys

```bash
# Generate secure API keys
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Run multiple times to generate multiple keys.

---

## ✅ Verification

### 1. Health Check

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00",
  "service": "Guru API"
}
```

### 2. Test API Endpoint

```bash
curl -X POST http://localhost:8000/api/kundali/full \
  -H "x-api-key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "birth_date": "1990-01-15",
    "birth_time": "10:30",
    "birth_latitude": 28.6139,
    "birth_longitude": 77.2090,
    "timezone": "Asia/Kolkata"
  }'
```

### 3. Check Logs

```bash
# Docker
docker-compose logs -f

# Direct Python
tail -f logs/guru_api.log

# Systemd
sudo journalctl -u guru-api -f
```

---

## 🔍 Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000
# or
netstat -tulpn | grep 8000

# Kill process
kill -9 <PID>
```

### Permission Denied

```bash
# Make scripts executable
chmod +x deploy/start.sh

# Check file permissions
ls -la
```

### API Key Not Working

```bash
# Verify API key in .env
cat .env | grep API_KEYS

# Check if API key matches request header
# Header should be: x-api-key: your-key
```

### Docker Issues

```bash
# Rebuild image
docker-compose build --no-cache

# Remove old containers
docker-compose down -v

# Check Docker logs
docker-compose logs
```

---

## 📊 Monitoring

### View Logs

```bash
# Application logs
tail -f logs/guru_api.log

# Error logs
tail -f logs/guru_api_errors.log

# Docker logs
docker-compose logs -f guru-api
```

### Check Status

```bash
# Docker
docker-compose ps

# Systemd
sudo systemctl status guru-api

# Process
ps aux | grep uvicorn
```

---

## 🔄 Updates

### Update Application

```bash
# Git pull
git pull origin main

# Rebuild (Docker)
docker-compose build
docker-compose up -d

# Restart (Direct)
sudo systemctl restart guru-api

# Restart (Docker)
docker-compose restart
```

---

## 🎯 Recommended Setup for Production

1. **Use Docker** - Easier management and deployment
2. **Use Nginx** - Reverse proxy and SSL termination
3. **Use SSL** - Let's Encrypt free certificates
4. **Use Systemd** - Auto-restart on failure
5. **Monitor Logs** - Set up log rotation
6. **Use Strong API Keys** - Generate secure keys
7. **Configure Firewall** - Only allow necessary ports
8. **Regular Updates** - Keep system and dependencies updated

---

## 📞 Need Help?

- Check logs: `logs/guru_api.log` and `logs/guru_api_errors.log`
- Verify environment variables in `.env`
- Test health endpoint first: `/api/health`
- Verify API key format and header name: `x-api-key`

---

## 🚀 Quick Deploy Commands

```bash
# Docker (Fastest)
docker-compose up -d

# Direct Python
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Systemd
sudo systemctl start guru-api
```

Choose the method that works best for your setup! 🎉

