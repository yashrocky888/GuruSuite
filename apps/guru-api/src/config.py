"""
Configuration module for Guru API.

This module handles all environment variables and application settings.
Loads configuration from .env file and provides typed access to settings.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://user:password@localhost:5432/guru_api_db"
    )
    
    # API Configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # OpenAI Configuration (Optional)
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # Local LLM Configuration (Alternative)
    local_llm_url: Optional[str] = os.getenv("LOCAL_LLM_URL")
    local_llm_model: str = os.getenv("LOCAL_LLM_MODEL", "llama2")
    
    # Swiss Ephemeris Path
    se_path: Optional[str] = os.getenv("SE_PATH")
    
    # Application Settings
    app_name: str = os.getenv("APP_NAME", "Guru API")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    secret_key: str = os.getenv("SECRET_KEY", "change_this_in_production")
    
    # Phase 9: JWT Secret
    jwt_secret: Optional[str] = os.getenv("JWT_SECRET")
    
    # Phase 12: Notification delivery credentials
    twilio_sid: Optional[str] = os.getenv("TWILIO_SID")
    twilio_auth_token: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_whatsapp_from: Optional[str] = os.getenv("TWILIO_WHATSAPP_FROM")
    smtp_user: Optional[str] = os.getenv("SMTP_USER")
    smtp_pass: Optional[str] = os.getenv("SMTP_PASS")
    smtp_host: Optional[str] = os.getenv("SMTP_HOST")
    smtp_port: Optional[int] = int(os.getenv("SMTP_PORT", "587")) if os.getenv("SMTP_PORT") else None
    sendgrid_api_key: Optional[str] = os.getenv("SENDGRID_API_KEY")
    fcm_server_key: Optional[str] = os.getenv("FCM_SERVER_KEY")
    google_application_credentials: Optional[str] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    class Config:
        """Pydantic config for settings."""
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env


# Global settings instance
settings = Settings()

