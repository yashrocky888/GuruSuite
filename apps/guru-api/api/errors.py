"""
Phase 21: Unified Error Handling

Provides consistent error response format.
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_500_INTERNAL_SERVER_ERROR
)


class GuruAPIError(Exception):
    """
    Phase 21: Base exception for Guru API errors.
    """
    
    def __init__(
        self,
        message: str,
        code: int = HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize error.
        
        Args:
            message: Error message
            code: HTTP status code
            details: Additional error details
        """
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(GuruAPIError):
    """Phase 21: Validation error (400)."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, HTTP_400_BAD_REQUEST, details)


class AuthenticationError(GuruAPIError):
    """Phase 21: Authentication error (401)."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, HTTP_401_UNAUTHORIZED)


class NotFoundError(GuruAPIError):
    """Phase 21: Not found error (404)."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, HTTP_404_NOT_FOUND)


class RateLimitError(GuruAPIError):
    """Phase 21: Rate limit error (429)."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, HTTP_429_TOO_MANY_REQUESTS)


def format_error_response(
    error: Exception,
    code: int = HTTP_500_INTERNAL_SERVER_ERROR
) -> Dict[str, Any]:
    """
    Phase 21: Format error response in unified format.
    
    Args:
        error: Exception object
        code: HTTP status code
    
    Returns:
        Formatted error dictionary
    """
    response = {
        "error": True,
        "message": str(error),
        "code": code
    }
    
    # Add details if available
    if isinstance(error, GuruAPIError) and error.details:
        response["details"] = error.details
    
    # In development, include traceback
    import os
    if os.getenv("DEPLOYMENT_ENV", "development") == "development":
        import traceback
        response["traceback"] = traceback.format_exc()
    
    return response


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Phase 21: Global exception handler.
    
    Args:
        request: FastAPI request
        exc: Exception
    
    Returns:
        JSON error response
    """
    # Handle GuruAPIError
    if isinstance(exc, GuruAPIError):
        return JSONResponse(
            status_code=exc.code,
            content=format_error_response(exc, exc.code)
        )
    
    # Handle HTTPException
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=format_error_response(exc, exc.status_code)
        )
    
    # Handle validation errors
    if "validation" in str(type(exc)).lower():
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content=format_error_response(exc, HTTP_400_BAD_REQUEST)
        )
    
    # Handle ephemeris/calculation errors
    if "swisseph" in str(type(exc)).lower() or "ephemeris" in str(exc).lower():
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={
                "error": True,
                "message": "Invalid birth data or calculation error. Please check your input.",
                "code": HTTP_400_BAD_REQUEST
            }
        )
    
    # Generic server error
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content=format_error_response(exc, HTTP_500_INTERNAL_SERVER_ERROR)
    )

