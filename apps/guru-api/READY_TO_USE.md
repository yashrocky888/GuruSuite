# 🚀 READY TO USE - Your Guru API Credentials

## ✅ Everything is Set Up and Ready!

### 🔑 Your API Key

```
XhsJ59EZ5vtMjrt7Yk1iFiK7E3FhMhVmCJr5OW7fs1eeLBjdHwCOBlLalntaB-BlXklxwrBxMHnB_4SlQlyt7g
```

**⚠️ SAVE THIS KEY SECURELY - Do NOT commit to git!**

---

### 📍 API Endpoint

```
https://guru-api-660206747784.us-central1.run.app
```

---

### 🧪 Quick Test

```bash
# Test Health (no auth needed)
curl https://guru-api-660206747784.us-central1.run.app/api/health

# Test with API Key
curl -X POST https://guru-api-660206747784.us-central1.run.app/api/kundali/full \
  -H "x-api-key: XhsJ59EZ5vtMjrt7Yk1iFiK7E3FhMhVmCJr5OW7fs1eeLBjdHwCOBlLalntaB-BlXklxwrBxMHnB_4SlQlyt7g" \
  -H "Content-Type: application/json" \
  -d '{
    "birth_date": "1990-01-15",
    "birth_time": "10:30",
    "birth_latitude": 28.6139,
    "birth_longitude": 77.2090,
    "timezone": "Asia/Kolkata"
  }'
```

---

### 💻 JavaScript/Node.js Example

```javascript
const axios = require('axios');

const API_KEY = 'XhsJ59EZ5vtMjrt7Yk1iFiK7E3FhMhVmCJr5OW7fs1eeLBjdHwCOBlLalntaB-BlXklxwrBxMHnB_4SlQlyt7g';
const API_URL = 'https://guru-api-660206747784.us-central1.run.app';

// Get Kundali
async function getKundali(birthDetails) {
  try {
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
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
    throw error;
  }
}

// Usage
getKundali({
  birth_date: '1990-01-15',
  birth_time: '10:30',
  birth_latitude: 28.6139,
  birth_longitude: 77.2090,
  timezone: 'Asia/Kolkata'
}).then(data => console.log(data));
```

---

### 🐍 Python Example

```python
import requests

API_KEY = 'XhsJ59EZ5vtMjrt7Yk1iFiK7E3FhMhVmCJr5OW7fs1eeLBjdHwCOBlLalntaB-BlXklxwrBxMHnB_4SlQlyt7g'
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
    response.raise_for_status()
    return response.json()

# Usage
result = get_kundali({
    'birth_date': '1990-01-15',
    'birth_time': '10:30',
    'birth_latitude': 28.6139,
    'birth_longitude': 77.2090,
    'timezone': 'Asia/Kolkata'
})
print(result)
```

---

### 📋 Available Endpoints

**Phase 21 Endpoints (Require API Key):**
- `POST /api/kundali/full` - Full birth chart
- `POST /api/prediction/today` - Daily prediction
- `POST /api/prediction/monthly` - Monthly prediction
- `POST /api/prediction/yearly` - Yearly prediction
- `POST /api/muhurtha/get` - Muhurtha timings
- `POST /api/karma/report` - Karma report
- `GET /api/health` - Health check (no auth)

**User Endpoints (Require JWT Token):**
- `POST /auth/register` - Register user
- `POST /auth/login` - Login (get token)
- `POST /guru/ask` - Ask the Guru
- `GET /guru/history` - Question history
- `POST /match/full-report` - Kundli matching
- And many more...

---

### 📖 Full Documentation

- **Interactive API Docs:** https://guru-api-660206747784.us-central1.run.app/docs
- **Usage Guide:** See API_USAGE_GUIDE.md
- **Get API Key Guide:** See GET_API_KEY.md

---

### 🔐 Environment Variables

Create a `.env` file in your project:

```bash
GURU_API_URL=https://guru-api-660206747784.us-central1.run.app
GURU_API_KEY=XhsJ59EZ5vtMjrt7Yk1iFiK7E3FhMhVmCJr5OW7fs1eeLBjdHwCOBlLalntaB-BlXklxwrBxMHnB_4SlQlyt7g
```

---

### ✅ Status

- ✅ API is live and running
- ✅ API key is configured
- ✅ All endpoints are available
- ✅ Ready for production use

**🎉 You're all set! Start integrating with your Guru project!**
