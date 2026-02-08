#!/usr/bin/env python3
"""
Simple script to start the Guru API backend server.
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import uvicorn
    from src.main import app
    
    print("=" * 60)
    print("🚀 Starting Guru API Backend")
    print("=" * 60)
    print(f"Host: 127.0.0.1")
    print(f"Port: 8000")
    print(f"Health check: http://127.0.0.1:8000/health")
    print("=" * 60)
    print()
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install dependencies: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
