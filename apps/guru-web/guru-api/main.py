"""
Main FastAPI Application for GURU API Backend
All AI endpoints automatically use the API key from llm_client
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api_routes import router
import os

# Initialize FastAPI app
app = FastAPI(
    title="GURU API",
    description="Vedic Astrology API with AI-powered insights",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes with v1 prefix
app.include_router(router, prefix="/api/v1", tags=["api"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "GURU API Backend",
        "status": "running",
        "version": "1.0.0",
        "note": "API key is securely loaded from .env and used automatically in all AI endpoints"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Verify API key is loaded
    from llm_client import API_KEY
    api_key_loaded = API_KEY is not None
    
    return {
        "status": "healthy",
        "api_key_loaded": api_key_loaded,
        "api_key_preview": f"{API_KEY[:10]}..." if API_KEY else "Not loaded"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

