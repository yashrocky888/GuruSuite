# Phase 21: AWS EC2 Deployment Guide

## Step-by-Step Deployment on AWS EC2

### Prerequisites
- AWS account
- EC2 instance (Ubuntu 22.04 LTS recommended)
- Domain name (optional, for SSL)

### Step 1: Launch EC2 Instance

1. Go to AWS Console → EC2 → Launch Instance
2. Choose Ubuntu 22.04 LTS
3. Select instance type (t3.medium or larger recommended)
4. Configure security group:
   - Allow SSH (port 22) from your IP
   - Allow HTTP (port 80) from anywhere
   - Allow HTTPS (port 443) from anywhere
   - Allow custom TCP (port 8000) from anywhere (or restrict to your IP)
5. Launch instance and save key pair

### Step 2: Connect to EC2 Instance

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### Step 3: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# Install Nginx
sudo apt install -y nginx

# Install Git
sudo apt install -y git
```

### Step 4: Clone and Setup Project

```bash
# Clone repository
git clone https://github.com/yourusername/guru-api.git
cd guru-api

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
nano .env  # Edit with your values
```

### Step 5: Configure Nginx Reverse Proxy

Create Nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/guru-api
```

Add:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/guru-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: Setup SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal is set up automatically
```

### Step 7: Setup Systemd Service

Create service file:

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

### Step 8: Configure Firewall

```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### Step 9: Monitor Logs

```bash
# Application logs
tail -f logs/guru_api.log

# Error logs
tail -f logs/guru_api_errors.log

# Systemd logs
sudo journalctl -u guru-api -f
```

### Step 10: Update Application

```bash
cd /home/ubuntu/guru-api
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart guru-api
```

## Maintenance

- **Check status**: `sudo systemctl status guru-api`
- **Restart service**: `sudo systemctl restart guru-api`
- **View logs**: `sudo journalctl -u guru-api -f`
- **Update code**: Follow Step 10

## Security Recommendations

1. Use strong API keys in `.env`
2. Enable firewall (UFW)
3. Regularly update system: `sudo apt update && sudo apt upgrade`
4. Monitor logs for suspicious activity
5. Use HTTPS only (SSL certificate)
6. Restrict API port 8000 to localhost only (Nginx handles external access)

