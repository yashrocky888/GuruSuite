# 🚀 Guru API Deployment Information

## Deployment Status: ✅ ACTIVE

### Access Information

- **API Base URL**: http://localhost:8000
- **Health Check**: http://localhost:8000/api/health
- **API Documentation**: http://localhost:8000/docs (if not in production mode)

### API Keys

Your API keys are stored in `.env` file. Use them in the `x-api-key` header:

```bash
curl -H "x-api-key: YOUR_API_KEY" http://localhost:8000/api/...
```

### Available Endpoints

1. **POST /api/kundali/full** - Full birth chart with interpretation
2. **POST /api/prediction/today** - Today's transit prediction
3. **POST /api/prediction/monthly** - Monthly prediction
4. **POST /api/prediction/yearly** - Yearly prediction
5. **POST /api/muhurtha/get** - Best Muhurtha time windows
6. **POST /api/karma/report** - Karma and soul path report
7. **GET /api/health** - Health check (no auth required)

### Docker Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View status
docker-compose ps

# Update and redeploy
git pull
docker-compose build
docker-compose up -d
```

### Security Notes

- ✅ API keys are required for all endpoints (except /health)
- ✅ Rate limiting: 60 requests/minute, 1000 requests/day
- ✅ All requests are logged
- ✅ Errors are handled securely (no internal details exposed)

### Monitoring

- Application logs: `logs/guru_api.log`
- Error logs: `logs/guru_api_errors.log`
- Docker logs: `docker-compose logs -f`

### Next Steps

1. Test the API using the health endpoint
2. Use your API keys to make authenticated requests
3. Monitor logs for any issues
4. Configure Nginx reverse proxy for production (optional)
5. Setup SSL certificate for HTTPS (recommended)

