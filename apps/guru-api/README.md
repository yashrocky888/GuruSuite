# 🌟 Guru Vedic Astrology API

Production-ready Vedic Astrology API with comprehensive predictions, Muhurtha calculations, and karma analysis.

## 🚀 Quick Start

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/guru-api.git
cd guru-api

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Run API
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Docker Deployment

```bash
# Build and run
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## 🔐 API Authentication

### API Key System

The API uses **Firebase Firestore** for API key management with environment variable fallback.

### Getting an API Key

#### Option 1: Admin Endpoint (Recommended)

```bash
# Create API key via admin endpoint
curl -X POST https://YOUR_API_URL/api/admin/create-key \
  -H "x-master-admin-key: YOUR_MASTER_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My API Key",
    "description": "Key for my application"
  }'
```

**Response:**
```json
{
  "success": true,
  "api_key": "your-64-character-secure-key",
  "name": "My API Key",
  "message": "API key created successfully. Save this key securely - it won't be shown again."
}
```

⚠️ **Save the API key immediately - it won't be shown again!**

#### Option 2: Environment Variable (Fallback)

Set `API_KEYS` in `.env`:
```bash
API_KEYS=key1,key2,key3
```

### Using API Keys

All API endpoints require the `x-api-key` header:

```bash
curl -X POST https://YOUR_API_URL/api/kundali/full \
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

### Admin Endpoints

Admin endpoints require `x-master-admin-key` header:

- `POST /api/admin/create-key` - Create new API key
- `GET /api/admin/list-keys` - List all API keys
- `POST /api/admin/deactivate-key/{key_id}` - Deactivate API key

## 📚 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check (no auth) |
| `/api/kundali/full` | POST | Full birth chart with interpretation |
| `/api/prediction/today` | POST | Today's transit prediction |
| `/api/prediction/monthly` | POST | Monthly prediction |
| `/api/prediction/yearly` | POST | Yearly prediction |
| `/api/muhurtha/get` | POST | Best Muhurtha time windows |
| `/api/karma/report` | POST | Karma and soul path report |

### Request Format

All POST endpoints require:
- Header: `x-api-key: YOUR_API_KEY`
- Content-Type: `application/json`
- Body: JSON with required parameters

### Response Format

All endpoints return:
```json
{
  "success": true,
  "data": { ... },
  "generated_at": "2025-01-15T10:30:00"
}
```

## ☁️ Firebase Cloud Run Deployment

### Prerequisites

1. Google Cloud Account
2. Firebase Project
3. `gcloud` CLI installed
4. Firebase service account JSON

### Quick Deploy

```bash
# 1. Set project
gcloud config set project YOUR_PROJECT_ID

# 2. Build image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/guru-api

# 3. Deploy to Cloud Run
gcloud run deploy guru-api \
  --image gcr.io/YOUR_PROJECT_ID/guru-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --set-secrets "GOOGLE_APPLICATION_CREDENTIALS=firebase-credentials:latest,MASTER_ADMIN_KEY=master-key:latest"
```

See [FIREBASE_DEPLOYMENT.md](FIREBASE_DEPLOYMENT.md) for detailed instructions.

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```bash
# Firebase (Required for API key management)
GOOGLE_APPLICATION_CREDENTIALS=./firebase-service-account.json
MASTER_ADMIN_KEY=your-super-secret-master-key

# API Configuration
DEPLOYMENT_ENV=production
LOG_LEVEL=INFO

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_DAY=1000

# Fallback API Keys (if Firebase unavailable)
API_KEYS=fallback-key-1,fallback-key-2

# Server
API_HOST=0.0.0.0
API_PORT=8080  # Use 8080 for Cloud Run, 8000 for local
WORKERS=4
```

### Firebase Setup

1. Create Firebase project
2. Enable Firestore Database
3. Download service account JSON
4. Set `GOOGLE_APPLICATION_CREDENTIALS` path
5. Create `api_keys` collection in Firestore (auto-created on first use)

## 📖 API Documentation

### Interactive Docs

Once deployed, visit:
- Swagger UI: `http://YOUR_API_URL/docs`
- ReDoc: `http://YOUR_API_URL/redoc`

### Example Requests

#### Full Kundali Report

```bash
curl -X POST https://YOUR_API_URL/api/kundali/full \
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

#### Today's Prediction

```bash
curl -X POST https://YOUR_API_URL/api/prediction/today \
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

#### Muhurtha Calculation

```bash
curl -X POST "https://YOUR_API_URL/api/muhurtha/get?task=travel&date=2025-01-20" \
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

## 🔒 Security Best Practices

1. **Use Firebase for API keys** - Centralized management
2. **Rotate master admin key** regularly
3. **Use strong master admin key** (64+ characters)
4. **Monitor API key usage** via Firestore
5. **Deactivate unused keys** immediately
6. **Never commit credentials** - Use Secret Manager
7. **Use HTTPS only** (Cloud Run provides this)
8. **Set up rate limiting** appropriately

## 📊 Rate Limiting

Default limits:
- **60 requests per minute** per API key
- **1000 requests per day** per API key

Configure via environment variables:
```bash
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_DAY=1000
```

Rate limit headers in response:
- `X-RateLimit-Limit-Minute`
- `X-RateLimit-Remaining-Minute`
- `X-RateLimit-Limit-Day`
- `X-RateLimit-Remaining-Day`

## 🐛 Error Handling

All errors return unified format:

```json
{
  "error": true,
  "message": "Error description",
  "code": 400
}
```

Common error codes:
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (missing/invalid API key)
- `403` - Forbidden (invalid master admin key)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

## 📝 Logging

Logs are written to:
- `logs/guru_api.log` - All logs
- `logs/guru_api_errors.log` - Error logs only

Log rotation:
- Max file size: 10MB
- Backup files: 5
- Automatic rotation

## 🧪 Testing

### Health Check

```bash
curl http://localhost:8000/api/health
```

### Test with API Key

```bash
# Get your API key first
export API_KEY="your-api-key"

# Test endpoint
curl -X POST http://localhost:8000/api/kundali/full \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "birth_date": "1990-01-15",
    "birth_time": "10:30",
    "birth_latitude": 28.6139,
    "birth_longitude": 77.2090,
    "timezone": "Asia/Kolkata"
  }'
```

## 🚀 Deployment Options

1. **Docker** - `docker-compose up -d`
2. **Firebase Cloud Run** - See [FIREBASE_DEPLOYMENT.md](FIREBASE_DEPLOYMENT.md)
3. **AWS EC2** - See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
4. **Direct Python** - `uvicorn api.main:app --host 0.0.0.0 --port 8000`

## 📚 Features

- ✅ Full birth chart generation
- ✅ Vimshottari Dasha calculations
- ✅ Transit predictions (daily/monthly/yearly)
- ✅ Muhurtha (auspicious timing)
- ✅ Karma and soul path analysis
- ✅ API key management via Firebase
- ✅ Rate limiting
- ✅ Comprehensive error handling
- ✅ Request logging
- ✅ Performance caching

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request

## 📄 License

[Your License Here]

## 🆘 Support

- Documentation: `/docs` endpoint
- Issues: GitHub Issues
- Email: [Your Email]

---

**Made with ❤️ for Vedic Astrology**
