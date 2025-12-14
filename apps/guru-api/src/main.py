"""
Main FastAPI application entry point for Guru API.

This module initializes the FastAPI app, includes all route modules,
and sets up middleware and error handling.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from src.config import settings
from src.db.database import engine, Base
from src.notifications.scheduler import start_scheduler, stop_scheduler
from src.notifications.scheduler_extended import start_extended_scheduler, stop_extended_scheduler
from src.api import (
    kundli_routes,
    dasha_routes,
    daily_routes,
    transit_routes,
    user_routes,
    panchang_routes
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Creates database tables on startup and starts notification scheduler.
    """
    # Startup: Create database tables (with error handling)
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        # Log error but don't fail startup if database is not available
        # This allows the API to run without database for basic calculations
        print(f"Warning: Could not connect to database: {e}")
        print("API will run in limited mode without database features.")
    
    # Phase 10: Start notification scheduler (daily at 6 AM)
    try:
        start_scheduler()
    except Exception as e:
        print(f"Warning: Could not start notification scheduler: {e}")
        print("Daily notifications will not be automatically generated.")
    
    # Phase 12: Start extended scheduler (every 5 minutes for multi-channel delivery)
    try:
        start_extended_scheduler()
    except Exception as e:
        print(f"Warning: Could not start extended notification scheduler: {e}")
        print("Multi-channel notifications will not be automatically delivered.")
    
    yield
    
    # Shutdown: Stop schedulers
    try:
        stop_scheduler()
    except Exception as e:
        print(f"Warning: Error stopping scheduler: {e}")
    
    try:
        stop_extended_scheduler()
    except Exception as e:
        print(f"Warning: Error stopping extended scheduler: {e}")


# Initialize FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A comprehensive Vedic Astrology API for calculating kundli, dasha, transits, and more.",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API route modules
# Phase 2: Core Kundli GET endpoint (direct path as per specification)
from src.api.kundli_routes import kundli_get
app.get("/kundli")(kundli_get)

# Phase 3: Core Dasha GET endpoint (direct path as per specification)
from src.api.dasha_routes import get_dasha
app.get("/dasha")(get_dasha)

# Phase 4: Core Panchang GET endpoint (direct path as per specification)
from src.api.panchang_routes import get_panchang
app.get("/panchang")(get_panchang)

# Phase 5: Strength routes (Shadbala and Ashtakavarga)
from src.api import strength_routes
app.include_router(strength_routes.router, prefix="/strength", tags=["Strength"])

# Phase 6: Yoga routes
from src.api import yoga_routes
app.include_router(yoga_routes.router, prefix="/yogas", tags=["Yogas"])

# Phase 7: Transit and Daily routes
from src.api import transit_routes, daily_routes
app.include_router(transit_routes.router, prefix="/transit", tags=["Transits"])
app.include_router(daily_routes.router, prefix="/daily", tags=["Daily"])

# Phase 8: AI Guru Interpretation routes
from src.api import ai_routes
app.include_router(ai_routes.router, prefix="/ai", tags=["AI Guru"])

# Phase 9: Authentication and User Management routes
from src.api import auth_routes, user_routes, subscription_routes
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(user_routes.router, prefix="/user", tags=["User"])
app.include_router(subscription_routes.router, prefix="/subscription", tags=["Subscription"])

# Phase 10: Notification and Admin routes
from src.api import notification_routes, admin_routes
app.include_router(notification_routes.router, prefix="/notifications", tags=["Notifications"])
app.include_router(admin_routes.router, prefix="/admin", tags=["Admin"])

# Phase 12: Notification Settings and Admin Broadcast routes
from src.api import notification_settings_routes, admin_broadcast_routes
app.include_router(notification_settings_routes.router, prefix="/notifications/settings", tags=["Notification Settings"])
app.include_router(admin_broadcast_routes.router, prefix="/admin/broadcast", tags=["Admin Broadcast"])

# Phase 11: Payment routes
from src.api import payment_routes
app.include_router(payment_routes.router, prefix="/payments", tags=["Payments"])

# Phase 13: Kundli Matching routes
from src.api import matching_routes
app.include_router(matching_routes.router, prefix="/match", tags=["Kundli Matching"])

# Phase 14: Ask the Guru routes
from src.api import guru_routes
app.include_router(guru_routes.router, prefix="/guru", tags=["Ask the Guru"])

# Phase 17: Astro Event Detector and Guru Conversation 2.0
from src.api import event_routes, guru2_routes
app.include_router(event_routes.router, prefix="/astro-events", tags=["Astro Events"])
app.include_router(guru2_routes.router, prefix="/guru2", tags=["Guru Conversation 2.0"])

# Phase 18: Interpretation Brain
from src.api import interpretation_routes
app.include_router(interpretation_routes.router, prefix="/interpretation", tags=["Interpretation"])

# Phase 19: Daily Transit Prediction & Guidance Engine
from src.api import transit_prediction_routes
app.include_router(transit_prediction_routes.router, prefix="/transit-prediction", tags=["Transit Prediction"])

# Phase 20: The Mega Engine (Muhurtha, Monthly, Yearly, Karma)
from src.api import muhurtha_routes, monthly_routes, yearly_routes, karma_routes
app.include_router(muhurtha_routes.router, prefix="/muhurtha", tags=["Muhurtha"])
app.include_router(monthly_routes.router, prefix="/monthly", tags=["Monthly Predictions"])
app.include_router(yearly_routes.router, prefix="/yearly", tags=["Yearly Predictions"])
app.include_router(karma_routes.router, prefix="/karma", tags=["Karma & Soul Path"])

# Other API routes with /api/v1 prefix
app.include_router(kundli_routes.router, prefix="/api/v1", tags=["Kundli"])
app.include_router(dasha_routes.router, prefix="/api/v1", tags=["Dasha"])
app.include_router(daily_routes.router, prefix="/api/v1", tags=["Daily"])
app.include_router(transit_routes.router, prefix="/api/v1", tags=["Transits"])
app.include_router(panchang_routes.router, prefix="/api/v1", tags=["Panchang"])
app.include_router(user_routes.router, prefix="/api/v1", tags=["Users"])


@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )

