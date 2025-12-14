"""
Pydantic schemas for request/response validation.

Defines data models for API request bodies and responses,
ensuring type safety and validation.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    name: str


class UserCreate(UserBase):
    """Schema for creating a new user."""
    pass


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Birth Detail Schemas
class BirthDetailBase(BaseModel):
    """Base birth detail schema."""
    name: str
    birth_date: datetime
    birth_time: str = Field(..., pattern=r'^\d{2}:\d{2}$')  # HH:MM format
    birth_latitude: float = Field(..., ge=-90, le=90)
    birth_longitude: float = Field(..., ge=-180, le=180)
    birth_place: str
    timezone: str


class BirthDetailCreate(BirthDetailBase):
    """Schema for creating birth details."""
    user_id: int


class BirthDetailResponse(BirthDetailBase):
    """Schema for birth detail response."""
    id: int
    user_id: int
    kundli_data: Optional[Dict[str, Any]] = None
    navamsa_data: Optional[Dict[str, Any]] = None
    dasamsa_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Kundli Request Schema
class KundliRequest(BaseModel):
    """Schema for kundli calculation request."""
    name: str
    birth_date: datetime
    birth_time: str = Field(..., pattern=r'^\d{2}:\d{2}$')
    birth_latitude: float = Field(..., ge=-90, le=90)
    birth_longitude: float = Field(..., ge=-180, le=180)
    birth_place: str
    timezone: str


# Dasha Request Schema
class DashaRequest(BaseModel):
    """Schema for dasha calculation request."""
    birth_date: datetime
    birth_time: str = Field(..., pattern=r'^\d{2}:\d{2}$')
    birth_latitude: float = Field(..., ge=-90, le=90)
    birth_longitude: float = Field(..., ge=-180, le=180)
    timezone: str
    calculation_date: Optional[datetime] = None  # Defaults to current date


# Transit Request Schema
class TransitRequest(BaseModel):
    """Schema for transit calculation request."""
    birth_date: datetime
    birth_time: str = Field(..., pattern=r'^\d{2}:\d{2}$')
    birth_latitude: float = Field(..., ge=-90, le=90)
    birth_longitude: float = Field(..., ge=-180, le=180)
    timezone: str
    transit_date: Optional[datetime] = None  # Defaults to current date


# Panchang Request Schema
class PanchangRequest(BaseModel):
    """Schema for panchang calculation request."""
    date: datetime
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone: str


# Daily Request Schema
class DailyRequest(BaseModel):
    """Schema for daily prediction request."""
    birth_date: datetime
    birth_time: str = Field(..., pattern=r'^\d{2}:\d{2}$')
    birth_latitude: float = Field(..., ge=-90, le=90)
    birth_longitude: float = Field(..., ge=-180, le=180)
    timezone: str
    query_date: Optional[datetime] = None  # Defaults to current date


# Saved Prediction Schemas
class SavedPredictionCreate(BaseModel):
    """Schema for creating a saved prediction."""
    title: str
    prediction_type: str
    prediction_data: Dict[str, Any]
    notes: Optional[str] = None


class SavedPredictionResponse(SavedPredictionCreate):
    """Schema for saved prediction response."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

