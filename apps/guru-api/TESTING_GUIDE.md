# 🧪 Testing Guide for Guru API - Beginner's Guide

This guide will help you test the Guru Vedic Astrology API step by step.

## 📋 Table of Contents
1. [Check if Server is Running](#1-check-if-server-is-running)
2. [Method 1: Using Browser (Easiest)](#method-1-using-browser-easiest)
3. [Method 2: Using Interactive API Docs](#method-2-using-interactive-api-docs-recommended)
4. [Method 3: Using curl (Command Line)](#method-3-using-curl-command-line)
5. [Method 4: Using Python](#method-4-using-python)
6. [Example Test Cases](#example-test-cases)

---

## 1. Check if Server is Running

First, make sure your server is running. Open a terminal and run:

```bash
cd /Users/yashm/Guru_API
uvicorn src.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

---

## Method 1: Using Browser (Easiest) 🖥️

### Test 1: Health Check
Open your browser and go to:
```
http://localhost:8000/health
```

You should see:
```json
{"status": "healthy"}
```

### Test 2: Root Endpoint
Go to:
```
http://localhost:8000/
```

You should see API information.

### Test 3: Kundli Calculation (GET Request)
Go to:
```
http://localhost:8000/kundli?dob=1995-05-16&time=18:38&lat=12.97&lon=77.59
```

**Parameters explained:**
- `dob` = Date of birth (YYYY-MM-DD format)
- `time` = Time of birth (HH:MM format, 24-hour)
- `lat` = Latitude (e.g., 12.97 for Bangalore)
- `lon` = Longitude (e.g., 77.59 for Bangalore)

You should see a JSON response with:
- Julian Day
- D1 chart (Ascendant, Planets, Houses)
- D9 (Navamsa) degrees
- D10 (Dasamsa) degrees

---

## Method 2: Using Interactive API Docs (Recommended) 📚

This is the **BEST way** for beginners!

### Step 1: Open API Documentation
Go to:
```
http://localhost:8000/docs
```

You'll see an interactive Swagger UI with all available endpoints.

### Step 2: Test Kundli Endpoint
1. Find the **GET /kundli** endpoint
2. Click on it to expand
3. Click the **"Try it out"** button
4. Fill in the parameters:
   - `dob`: `1995-05-16`
   - `time`: `18:38`
   - `lat`: `12.97`
   - `lon`: `77.59`
5. Click **"Execute"**
6. See the response below!

### Step 3: Test Other Endpoints
You can test:
- POST `/api/v1/kundli` - Full Kundli with more details
- POST `/api/v1/dasha` - Dasha calculations
- POST `/api/v1/panchang` - Panchang for a date
- And many more!

---

## Method 3: Using curl (Command Line) 💻

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

### Test 2: Kundli Calculation
```bash
curl "http://localhost:8000/kundli?dob=1995-05-16&time=18:38&lat=12.97&lon=77.59"
```

### Test 3: Pretty Print JSON
```bash
curl -s "http://localhost:8000/kundli?dob=1995-05-16&time=18:38&lat=12.97&lon=77.59" | python3 -m json.tool
```

### Test 4: Save Response to File
```bash
curl -s "http://localhost:8000/kundli?dob=1995-05-16&time=18:38&lat=12.97&lon=77.59" > kundli_response.json
```

---

## Method 4: Using Python 🐍

### Create a Test Script

Create a file `test_api.py`:

```python
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

# Test 1: Health Check
print("1. Testing Health Check...")
response = requests.get(f"{BASE_URL}/health")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
print()

# Test 2: Kundli Calculation
print("2. Testing Kundli Calculation...")
params = {
    "dob": "1995-05-16",
    "time": "18:38",
    "lat": 12.97,
    "lon": 77.59
}
response = requests.get(f"{BASE_URL}/kundli", params=params)
print(f"Status: {response.status_code}")
kundli_data = response.json()

# Pretty print
print(json.dumps(kundli_data, indent=2))

# Extract specific information
print("\n3. Extracted Information:")
print(f"Ascendant: {kundli_data['D1']['Ascendant']['sign']} at {kundli_data['D1']['Ascendant']['degree']:.2f}°")
print(f"Sun: {kundli_data['D1']['Planets']['Sun']['sign']} at {kundli_data['D1']['Planets']['Sun']['degree']:.2f}°")
print(f"Moon: {kundli_data['D1']['Planets']['Moon']['sign']} at {kundli_data['D1']['Planets']['Moon']['degree']:.2f}°")
```

### Run the Test Script
```bash
python3 test_api.py
```

---

## Example Test Cases 📝

### Test Case 1: Your Own Birth Details
Replace with your actual birth details:

```
http://localhost:8000/kundli?dob=YYYY-MM-DD&time=HH:MM&lat=LATITUDE&lon=LONGITUDE
```

**How to find your coordinates:**
- Google: "latitude longitude of [your city]"
- Example: Bangalore = 12.97, 77.59

### Test Case 2: Different Cities

**Mumbai:**
```
http://localhost:8000/kundli?dob=1990-01-15&time=10:30&lat=19.0760&lon=72.8777
```

**Delhi:**
```
http://localhost:8000/kundli?dob=1990-01-15&time=10:30&lat=28.6139&lon=77.2090
```

**New York:**
```
http://localhost:8000/kundli?dob=1990-01-15&time=10:30&lat=40.7128&lon=-74.0060
```

### Test Case 3: Testing POST Endpoints

For POST endpoints, use the interactive docs at `/docs` or use Python:

```python
import requests

url = "http://localhost:8000/api/v1/kundli"
data = {
    "name": "Test User",
    "birth_date": "1995-05-16T18:38:00",
    "birth_time": "18:38",
    "birth_latitude": 12.97,
    "birth_longitude": 77.59,
    "birth_place": "Bangalore",
    "timezone": "Asia/Kolkata"
}

response = requests.post(url, json=data)
print(response.json())
```

---

## Understanding the Response 📊

### Kundli Response Structure:
```json
{
  "julian_day": 2449854.276389,
  "D1": {
    "Ascendant": {
      "degree": 290.949,
      "sign": "Capricorn"
    },
    "Planets": {
      "Sun": {
        "degree": 31.637,
        "sign": "Taurus"
      },
      // ... other planets
    },
    "Houses": [
      {
        "house": 1,
        "degree": 290.949,
        "sign": "Capricorn"
      },
      // ... 11 more houses
    ]
  },
  "D9": {
    "Sun": 14.733,
    // ... Navamsa degrees
  },
  "D10": {
    "Sun": 16.37,
    // ... Dasamsa degrees
  }
}
```

### What Each Field Means:
- **julian_day**: Astronomical time reference
- **Ascendant**: Rising sign at birth
- **Planets**: Positions of all 9 planets
- **Houses**: 12 house cusps
- **D9**: Navamsa (9th division chart)
- **D10**: Dasamsa (10th division chart)

---

## Common Issues & Solutions 🔧

### Issue 1: "Connection Refused"
**Solution:** Make sure the server is running:
```bash
uvicorn src.main:app --reload
```

### Issue 2: "Not Found" Error
**Solution:** Check the URL - make sure it's exactly:
```
http://localhost:8000/kundli?dob=1995-05-16&time=18:38&lat=12.97&lon=77.59
```

### Issue 3: Invalid Date Format
**Solution:** Use correct format:
- Date: `YYYY-MM-DD` (e.g., `1995-05-16`)
- Time: `HH:MM` (24-hour format, e.g., `18:38`)

### Issue 4: Coordinates Out of Range
**Solution:** 
- Latitude: -90 to 90
- Longitude: -180 to 180

---

## Quick Test Checklist ✅

- [ ] Server is running (`uvicorn src.main:app --reload`)
- [ ] Health check works (`http://localhost:8000/health`)
- [ ] Can access docs (`http://localhost:8000/docs`)
- [ ] Kundli endpoint works with test data
- [ ] Response contains Ascendant, Planets, Houses
- [ ] D9 and D10 are included in response

---

## Next Steps 🚀

Once you're comfortable with testing:

1. **Try different birth dates and times**
2. **Test other endpoints** (dasha, panchang, transits)
3. **Build a simple frontend** to visualize the Kundli
4. **Integrate with your application**

---

## Need Help? 💬

- Check the API docs: `http://localhost:8000/docs`
- Read the README.md file
- Check error messages in the terminal where server is running

Happy Testing! 🎉

