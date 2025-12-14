# Quick Start - Python Backend

## ❌ Wrong Command
```bash
npm run dev  # ❌ This is for Node.js, not Python!
```

## ✅ Correct Commands

### Option 1: Using the run script
```bash
cd guru-api
chmod +x run.sh
./run.sh
```

### Option 2: Using uvicorn directly
```bash
cd guru-api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Using Python directly
```bash
cd guru-api
python main.py
```

## Verify It's Running

```bash
# Check health
curl http://localhost:8000/health

# Check root
curl http://localhost:8000/
```

## Backend Runs On:
- **URL**: http://localhost:8000
- **API**: http://localhost:8000/api/v1

## Note:
- `guru-api` = Python FastAPI backend (port 8000)
- `guru-astro-api` = Node.js TypeScript backend (port 3001)
- `guru-web` = Next.js frontend (port 3000)

