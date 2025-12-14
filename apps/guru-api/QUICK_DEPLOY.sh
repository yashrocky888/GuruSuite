#!/bin/bash
# Quick Deployment Script for Guru API

echo "🚀 Guru API Quick Deployment"
echo "============================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from template..."
    
    cat > .env << EOL
# API Configuration
API_KEYS=dev-api-key-change-in-production
DEPLOYMENT_ENV=development
LOG_LEVEL=INFO

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_DAY=1000

# API Server
API_HOST=0.0.0.0
API_PORT=8000
WORKERS=4
EOL
    
    echo "✅ Created .env file with default values"
    echo "⚠️  Please edit .env and add your API keys!"
    echo ""
fi

# Check Docker
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "🐳 Docker detected - Using Docker deployment"
    echo ""
    echo "Building Docker image..."
    docker build -t guru-api:latest .
    
    echo ""
    echo "Starting containers..."
    docker-compose up -d
    
    echo ""
    echo "✅ Deployment complete!"
    echo ""
    echo "Check status: docker-compose ps"
    echo "View logs: docker-compose logs -f"
    echo "Test: curl http://localhost:8000/api/health"
    echo ""
    echo "API will be available at: http://localhost:8000"
    echo "API Docs: http://localhost:8000/docs"
    
elif command -v python3 &> /dev/null; then
    echo "🐍 Python detected - Using direct Python deployment"
    echo ""
    
    # Check virtual environment
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    echo "Activating virtual environment..."
    source venv/bin/activate
    
    echo "Installing dependencies..."
    pip install -r requirements.txt --quiet
    
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "Starting server..."
    echo "Press Ctrl+C to stop"
    echo ""
    
    uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
    
else
    echo "❌ Error: Neither Docker nor Python3 found!"
    echo "Please install Docker or Python 3.11+"
    exit 1
fi
