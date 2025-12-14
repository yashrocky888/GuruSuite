# How to Run the GURU API Backend

## Quick Start

### 1. Navigate to the backend directory
```bash
cd guru-api
```

### 2. Install dependencies (if not already installed)
```bash
pip install -r requirements.txt
```

Or if you prefer using a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Verify .env file exists
Make sure `.env` file is in the project root (`/Users/yashm/Guru_project/.env`) with:
```
GURU_API_KEY=your_api_key_here
```

### 4. Run the backend server
```bash
# Option 1: Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using Python directly
python main.py
```

### 5. Verify it's running
Open your browser or use curl:
```bash
# Check root endpoint
curl http://localhost:8000/

# Check health endpoint
curl http://localhost:8000/health

# Check API endpoint
curl http://localhost:8000/api/v1/kundli
```

## Backend will run on:
- **URL**: http://localhost:8000
- **API Base**: http://localhost:8000/api/v1
- **Health Check**: http://localhost:8000/health

## Common Commands

### Run with auto-reload (development)
```bash
uvicorn main:app --reload
```

### Run on specific port
```bash
uvicorn main:app --port 8001
```

### Run in production mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Troubleshooting

### Port already in use
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Module not found errors
```bash
# Make sure you're in the guru-api directory
cd guru-api

# Reinstall dependencies
pip install -r requirements.txt
```

### API key not loading
```bash
# Verify .env file exists in project root
ls -la ../.env

# Test API key loading
python -c "from llm_client import API_KEY; print(f'Key loaded: {API_KEY[:10] if API_KEY else None}...')"
```

## API Endpoints

All endpoints are prefixed with `/api/v1`:

- `GET /api/v1/kundli` - Get kundli chart data
- `GET /api/v1/kundli/divisional/{chart_type}` - Get divisional charts
- `GET /api/v1/dasha` - Get dasha information
- `GET /api/v1/transits` - Get transit data
- `GET /api/v1/panchang` - Get panchang data
- `POST /api/v1/interpret` - AI interpretation
- `POST /api/v1/chat` - Guru chat
- And more...

## Frontend Connection

The frontend (Next.js) should connect to:
```
http://localhost:8000/api/v1
```

Make sure CORS is enabled (already configured in `main.py`).

