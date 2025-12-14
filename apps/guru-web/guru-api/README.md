# GURU API Backend

Backend API server for the GURU astrology application.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file in project root:
```bash
GURU_API_KEY=your_api_key_here
```

3. The API key is automatically loaded by `llm_client.py` and used in all AI-related endpoints.

## Security

- The `.env` file is in `.gitignore` and should NEVER be committed
- API key is loaded from environment variables only
- API key is NEVER exposed to the frontend
- All AI requests automatically include the Authorization header

## Usage

```python
from llm_client import get_llm_client, generate_guru_response

# Get client instance
client = get_llm_client()

# Generate response
response = generate_guru_response(
    user_message="What does my chart say?",
    context="You are a Vedic astrology guru..."
)
```

