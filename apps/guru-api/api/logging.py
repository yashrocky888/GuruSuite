"""
Phase 21: Logging and Monitoring

Implements request logging, error logging, and performance monitoring.
"""

import os
import logging
import time
from typing import Optional
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from fastapi import Request


def setup_logging(log_level: Optional[str] = None) -> logging.Logger:
    """
    Phase 21: Setup application logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger
    """
    log_level = log_level or os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger("guru_api")
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level, logging.INFO))
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    log_file = logs_dir / "guru_api.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Error log file
    error_log_file = logs_dir / "guru_api_errors.log"
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    logger.addHandler(error_handler)
    
    return logger


# Global logger instance
logger = setup_logging()


def log_request(request: Request, api_key: str, duration: float):
    """
    Phase 21: Log API request.
    
    Args:
        request: FastAPI request
        api_key: API key (masked)
        duration: Request duration in seconds
    """
    masked_key = api_key[:8] + "..." if len(api_key) > 8 else "***"
    
    logger.info(
        f"Request: {request.method} {request.url.path} | "
        f"API Key: {masked_key} | "
        f"Duration: {duration:.3f}s | "
        f"Status: 200"
    )


def log_error(error: Exception, request: Optional[Request] = None):
    """
    Phase 21: Log error.
    
    Args:
        error: Exception object
        request: Optional FastAPI request
    """
    error_msg = f"Error: {type(error).__name__} - {str(error)}"
    
    if request:
        error_msg += f" | Path: {request.url.path} | Method: {request.method}"
    
    logger.error(error_msg, exc_info=True)


class PerformanceTimer:
    """
    Phase 21: Performance timer context manager.
    """
    
    def __init__(self, operation_name: str):
        """
        Initialize timer.
        
        Args:
            operation_name: Name of the operation being timed
        """
        self.operation_name = operation_name
        self.start_time = None
        self.duration = None
    
    def __enter__(self):
        """Start timer."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timer and log duration."""
        self.duration = time.time() - self.start_time
        
        if self.duration > 1.0:  # Log slow operations
            logger.warning(
                f"Slow operation: {self.operation_name} took {self.duration:.3f}s"
            )
        else:
            logger.debug(
                f"Operation: {self.operation_name} took {self.duration:.3f}s"
            )

