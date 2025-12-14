# Setup Guide for Guru API

## Quick Setup Steps

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root with the following content:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/guru_api_db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# OpenAI Configuration (Optional)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Local LLM Configuration (Alternative to OpenAI)
LOCAL_LLM_URL=http://localhost:11434
LOCAL_LLM_MODEL=llama2

# Application Settings
APP_NAME=Guru API
APP_VERSION=1.0.0
SECRET_KEY=your_secret_key_here_change_in_production
```

### 3. Set Up Database

For PostgreSQL:

```bash
# Create database
createdb guru_api_db

# Or using psql
psql -U postgres
CREATE DATABASE guru_api_db;
```

### 4. Run the Application

```bash
# Option 1: Using uvicorn directly
uvicorn src.main:app --reload

# Option 2: Using the startup script
chmod +x start.sh
./start.sh
```

### 5. Verify Installation

- Open http://localhost:8000/docs for interactive API documentation
- Test the health endpoint: http://localhost:8000/health
- Test root endpoint: http://localhost:8000/

## Testing

Run the test suite:

```bash
pytest tests/
```

## Docker Setup

```bash
# Build image
docker build -t guru-api .

# Run container
docker run -p 8000:8000 --env-file .env guru-api
```

## Troubleshooting

### Swiss Ephemeris Issues

If you encounter issues with Swiss Ephemeris:
- Ensure pyswisseph is installed: `pip install pyswisseph`
- The library should automatically download ephemeris files on first use

### Database Connection Issues

- Verify PostgreSQL is running
- Check DATABASE_URL format: `postgresql://user:password@host:port/database`
- Ensure database exists

### Import Errors

- Ensure you're in the project root directory
- Verify virtual environment is activated
- Check that all dependencies are installed

## Next Steps

1. Read the [README.md](README.md) for API documentation
2. Explore the interactive docs at `/docs`
3. Start making API calls!

