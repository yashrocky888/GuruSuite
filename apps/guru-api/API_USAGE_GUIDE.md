# 🔑 API Key & Authentication Guide

## API Key (For Phase 21 Endpoints)

### Getting an API Key

Use the admin endpoint to create an API key:

```bash
curl -X POST https://guru-api-660206747784.us-central1.run.app/api/admin/create-key \
  -H "x-master-admin-key: YOUR_MASTER_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Project Name",
    "description": "Description of your project"
  }'
```

**Response:**
```json
{
  "success": true,
  "api_key": "your-64-character-secure-key-here",
  "name": "My Project Name",
  "message": "API key created successfully. Save this key securely - it won't be shown again."
}
```

⚠️ **IMPORTANT:** Save the API key immediately - it won't be shown again!

### Using API Key

Add the API key to all Phase 21 endpoints:

```bash
curl -X POST https://guru-api-660206747784.us-central1.run.app/api/kundali/full \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "birth_date": "1990-01-15",
    "birth_time": "10:30",
    "birth_latitude": 28.6139,
    "birth_longitude": 77.2090,
    "timezone": "Asia/Kolkata"
  }'
```

### Phase 21 Endpoints (Require API Key)

All endpoints under `/api/*` require the `x-api-key` header:

- `POST /api/kundali/full` - Full birth chart
- `POST /api/prediction/today` - Daily prediction
- `POST /api/prediction/monthly` - Monthly prediction
- `POST /api/prediction/yearly` - Yearly prediction
- `POST /api/muhurtha/get` - Muhurtha timings
- `POST /api/karma/report` - Karma report
- `GET /api/health` - Health check (no auth needed)

---

## JWT Token (For User Authentication Endpoints)

### Getting a JWT Token

1. **Register a User:**
```bash
curl -X POST https://guru-api-660206747784.us-central1.run.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123"
  }'
```

2. **Login to Get Token:**
```bash
curl -X POST https://guru-api-660206747784.us-central1.run.app/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "securepassword123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using JWT Token

Add the token to user-specific endpoints:

```bash
curl -X GET https://guru-api-660206747784.us-central1.run.app/user/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### User Authentication Endpoints (Require JWT Token)

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get token
- `GET /user/profile` - Get user profile
- `POST /guru/ask` - Ask the Guru (requires user account)
- `GET /guru/history` - Get question history
- `POST /match/full-report` - Kundli matching
- And many more...

---

## Quick Start for Your Guru Project

### Option 1: Use API Key (Recommended for Server-Side)

```javascript
// Node.js/Express example
const axios = require('axios');

const API_KEY = 'your-api-key-here';
const API_URL = 'https://guru-api-660206747784.us-central1.run.app';

async function getKundali(birthDetails) {
  const response = await axios.post(
    `${API_URL}/api/kundali/full`,
    birthDetails,
    {
      headers: {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
      }
    }
  );
  return response.data;
}
```

### Option 2: Use JWT Token (For User-Specific Features)

```javascript
// Login first
async function login(username, password) {
  const response = await axios.post(
    `${API_URL}/auth/login`,
    { username, password }
  );
  return response.data.access_token;
}

// Use token for authenticated requests
async function askGuru(question, token) {
  const response = await axios.post(
    `${API_URL}/guru/ask`,
    { question },
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  return response.data;
}
```

### Option 3: Python Example

```python
import requests

API_KEY = 'your-api-key-here'
API_URL = 'https://guru-api-660206747784.us-central1.run.app'

def get_kundali(birth_details):
    response = requests.post(
        f'{API_URL}/api/kundali/full',
        json=birth_details,
        headers={
            'x-api-key': API_KEY,
            'Content-Type': 'application/json'
        }
    )
    return response.json()
```

---

## Environment Variables

Store your credentials securely:

```bash
# .env file
GURU_API_URL=https://guru-api-660206747784.us-central1.run.app
GURU_API_KEY=your-api-key-here
GURU_MASTER_ADMIN_KEY=your-master-admin-key-here
```

---

## Rate Limits

- **API Key endpoints:** 60 requests/minute, 1000 requests/day
- **JWT endpoints:** Varies by endpoint

---

## Support

- API Documentation: https://guru-api-660206747784.us-central1.run.app/docs
- Health Check: https://guru-api-660206747784.us-central1.run.app/api/health
