"""
Phase 21: Production API Main Entry Point

FastAPI application with security, rate limiting, and error handling.
"""

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.errors import global_exception_handler, GuruAPIError
from api.logging import setup_logging, logger
from api.routes import (
    kundali_routes,
    prediction_routes,
    muhurtha_routes,
    karma_routes,
    healthcheck
)
from api.admin_routes import router as admin_router
from api.firebase_auth import initialize_firebase

# Import all additional routes from src/api (with error handling)
try:
    from src.api import (
        auth_routes,
        user_routes,
        subscription_routes,
        notification_routes,
        notification_settings_routes,
        admin_broadcast_routes,
        matching_routes,
        guru_routes,
        event_routes,
        guru2_routes,
        interpretation_routes,
        transit_prediction_routes,
        monthly_routes,
        yearly_routes,
        kundli_routes,
        dasha_routes,
        daily_routes,
        transit_routes,
        panchang_routes,
        strength_routes,
        yoga_routes,
        ai_routes
    )
    # Payment routes - should work with setuptools in requirements
    from src.api import payment_routes
except ImportError as e:
    logger.warning(f"Some routes not available: {e}")
    # Set all to None if import fails
    auth_routes = user_routes = subscription_routes = None
    notification_routes = notification_settings_routes = admin_broadcast_routes = None
    payment_routes = matching_routes = guru_routes = None
    event_routes = guru2_routes = interpretation_routes = None
    transit_prediction_routes = monthly_routes = yearly_routes = None
    kundli_routes = dasha_routes = daily_routes = None
    transit_routes = panchang_routes = strength_routes = None
    yoga_routes = ai_routes = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Phase 21: Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Guru API...")
    logger.info(f"Environment: {os.getenv('DEPLOYMENT_ENV', 'development')}")
    logger.info(f"Log Level: {os.getenv('LOG_LEVEL', 'INFO')}")
    
    # Initialize Firebase
    try:
        db = initialize_firebase()
        if db:
            logger.info("Firebase Firestore initialized successfully")
        else:
            logger.warning("Firebase not initialized - using environment variable API keys")
    except Exception as e:
        logger.warning(f"Firebase initialization failed: {e} - using fallback authentication")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Guru API...")


# Initialize FastAPI app
app = FastAPI(
    title="Guru Vedic Astrology API",
    version="2.1.0",
    description="Production-ready Vedic Astrology API with comprehensive predictions, Muhurtha, and karma analysis.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add global exception handler
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(GuruAPIError, global_exception_handler)

# Include API routes - Phase 21 Production Routes
app.include_router(kundali_routes.router, prefix="/api/kundali", tags=["Kundali"])
app.include_router(prediction_routes.router, prefix="/api/prediction", tags=["Predictions"])
app.include_router(muhurtha_routes.router, prefix="/api/muhurtha", tags=["Muhurtha"])
app.include_router(karma_routes.router, prefix="/api/karma", tags=["Karma"])
app.include_router(healthcheck.router, prefix="/api", tags=["Health"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])

# Include all additional routes from previous phases
# All routes included directly - production matches local exactly
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(user_routes.router, prefix="/user", tags=["User"])
app.include_router(subscription_routes.router, prefix="/subscription", tags=["Subscription"])

# Phase 10: Notification and Admin routes
app.include_router(notification_routes.router, prefix="/notifications", tags=["Notifications"])
app.include_router(notification_settings_routes.router, prefix="/notifications/settings", tags=["Notification Settings"])
app.include_router(admin_broadcast_routes.router, prefix="/admin/broadcast", tags=["Admin Broadcast"])

# Phase 11: Payment routes
app.include_router(payment_routes.router, prefix="/payments", tags=["Payments"])

# Phase 13: Kundli Matching routes
app.include_router(matching_routes.router, prefix="/match", tags=["Kundli Matching"])

# Phase 14: Ask the Guru routes
app.include_router(guru_routes.router, prefix="/guru", tags=["Ask the Guru"])

# Phase 17: Astro Event Detector and Guru Conversation 2.0
app.include_router(event_routes.router, prefix="/astro-events", tags=["Astro Events"])
app.include_router(guru2_routes.router, prefix="/guru2", tags=["Guru Conversation 2.0"])

# Phase 18: Interpretation Brain
app.include_router(interpretation_routes.router, prefix="/interpretation", tags=["Interpretation"])

# Phase 19: Daily Transit Prediction & Guidance Engine
app.include_router(transit_prediction_routes.router, prefix="/transit-prediction", tags=["Transit Prediction"])

# Phase 20: The Mega Engine (Monthly, Yearly)
app.include_router(monthly_routes.router, prefix="/monthly", tags=["Monthly Predictions"])
app.include_router(yearly_routes.router, prefix="/yearly", tags=["Yearly Predictions"])

# Additional API routes with /api/v1 prefix
app.include_router(kundli_routes.router, prefix="/api/v1", tags=["Kundli"])
app.include_router(dasha_routes.router, prefix="/api/v1", tags=["Dasha"])
app.include_router(daily_routes.router, prefix="/api/v1", tags=["Daily"])
app.include_router(transit_routes.router, prefix="/api/v1", tags=["Transits"])
app.include_router(panchang_routes.router, prefix="/api/v1", tags=["Panchang"])

# Other routes
app.include_router(strength_routes.router, prefix="/strength", tags=["Strength"])
app.include_router(yoga_routes.router, prefix="/yogas", tags=["Yogas"])
app.include_router(transit_routes.router, prefix="/transit", tags=["Transits"])
app.include_router(daily_routes.router, prefix="/daily", tags=["Daily"])
app.include_router(ai_routes.router, prefix="/ai", tags=["AI Guru"])

# Direct GET endpoints (for frontend compatibility)
from src.api.kundli_routes import kundli_get
from src.api.dasha_routes import get_dasha
from src.api.panchang_routes import get_panchang

app.get("/kundli")(kundli_get)
app.get("/dasha")(get_dasha)
app.get("/panchang")(get_panchang)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Guru Vedic Astrology API",
        "version": "2.1.0",
        "status": "running",
        "docs": "/docs"
    }


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Phase 21: Request logging middleware."""
    import time
    
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add performance header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    except Exception as e:
        from api.logging import log_error
        log_error(e, request)
        raise


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("PORT", os.getenv("API_PORT", "8080")))  # Cloud Run sets PORT env var
    
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=os.getenv("DEPLOYMENT_ENV") == "development",
        workers=int(os.getenv("WORKERS", "1"))
    )

