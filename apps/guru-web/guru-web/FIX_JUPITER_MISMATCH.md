# Fix Jupiter Sign Mismatch

## Problem
API is returning **OLD format** with Jupiter in "Dhanu" (wrong), but should return **NEW format** with Jupiter in "Scorpio" (correct).

## Root Cause
The Python backend (`guru-api`) is returning old cached/calculated data instead of the new Drik Panchang data.

## Solution

### 1. Restart Python Backend
```bash
# Find and kill the backend process
lsof -ti :8000 | xargs kill -9

# Restart backend
cd guru-api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Clear Browser Cache
- Press `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows) for hard refresh
- Or: DevTools (F12) → Application → Clear Storage → Clear site data

### 3. Verify API Response
After restart, check:
```bash
curl "http://localhost:8000/api/v1/kundli" | python3 -m json.tool | grep -A 3 "Jupiter"
```

Should show:
```json
"Jupiter": {
    "sign": "Scorpio",  // NOT "Dhanu"
    "house": 1,
    "degree": 228.6896
}
```

### 4. Check Frontend Console
Open browser DevTools → Console, look for:
- `Raw chartData:` - Should show `data.kundli.Planets.Jupiter.sign = "Scorpio"`
- `Planet Jupiter: API says house=1, sign=Scorpio->Vrishchika`

## Expected API Format
```json
{
  "data": {
    "kundli": {
      "Ascendant": { "sign": "Scorpio" },
      "Planets": {
        "Jupiter": { "sign": "Scorpio", "house": 1, "degree": 228.6896 }
      },
      "Houses": [
        { "house": 1, "sign": "Scorpio" }
      ]
    }
  }
}
```

## If Still Wrong
1. Check Python backend logs for errors
2. Verify the backend is using Drik Panchang calculations
3. Check if there's cached data in the backend
4. Restart both frontend and backend

