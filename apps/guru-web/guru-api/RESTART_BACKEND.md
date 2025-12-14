# How to Restart the Backend

## ✅ Backend is Already Running!

The backend is currently running on port 8000. You can verify with:
```bash
curl http://localhost:8000/health
```

## If You Need to Restart:

### Step 1: Find the process
```bash
lsof -i :8000
```

### Step 2: Kill the process(es)
```bash
# Kill all Python processes on port 8000
kill -9 65005 65007

# Or kill all at once:
lsof -ti :8000 | xargs kill -9
```

### Step 3: Start fresh
```bash
cd guru-api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Quick Restart Script:
```bash
# Kill existing
lsof -ti :8000 | xargs kill -9 2>/dev/null

# Wait a moment
sleep 1

# Start new
cd guru-api && uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Current Status:
✅ Backend is running and healthy
✅ API key is loaded
✅ Ready to accept requests

No action needed unless you want to restart!

