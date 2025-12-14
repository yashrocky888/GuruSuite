# Server Troubleshooting Guide

## 🚨 Server Not Loading?

### Quick Fix: Start the Server

**Option 1: Use the start script (Easiest)**
```bash
cd /Users/yashm/Guru_API
./start_server.sh
```

**Option 2: Manual start**
```bash
cd /Users/yashm/Guru_API
uvicorn src.main:app --reload
```

**Option 3: Start with specific host/port**
```bash
cd /Users/yashm/Guru_API
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Check if Server is Running

```bash
# Check if server is running
curl http://localhost:8000/health

# Check what's using port 8000
lsof -i:8000

# Check if uvicorn process exists
ps aux | grep uvicorn
```

### Common Issues

#### 1. Port 8000 Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Find and kill the process using port 8000
kill $(lsof -ti:8000)

# Or use a different port
uvicorn src.main:app --reload --port 8001
```

#### 2. Server Not Starting

**Check for errors**:
```bash
cd /Users/yashm/Guru_API
python3 -m uvicorn src.main:app --reload
```

**Common fixes**:
- Make sure you're in the project directory
- Check if all dependencies are installed: `pip3 install -r requirements.txt`
- Check for import errors

#### 3. Server Starts But Docs Don't Load

**Check**:
- Server is actually running (check terminal output)
- No errors in server logs
- Try: http://localhost:8000/ (root endpoint)
- Try: http://localhost:8000/health

**If root works but docs don't**:
- Clear browser cache
- Try incognito/private mode
- Check browser console for errors

### Verify Server is Working

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test root endpoint
curl http://localhost:8000/

# Test docs endpoint
curl http://localhost:8000/docs
```

### Start Server in Background

```bash
cd /Users/yashm/Guru_API
nohup uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 > server.log 2>&1 &
```

Then check logs:
```bash
tail -f server.log
```

### Stop Server

```bash
# Find and kill uvicorn process
pkill -f uvicorn

# Or kill by port
kill $(lsof -ti:8000)
```

### Quick Test Without Server

If server won't start, you can still test the yoga engine directly:

```bash
cd /Users/yashm/Guru_API
python3 test_yogas_quick.py
```

This tests the yoga detection logic without needing the HTTP server.

