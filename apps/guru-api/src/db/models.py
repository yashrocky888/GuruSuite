"""
SQLAlchemy ORM models for database tables.

Defines User, BirthDetail, and SavedPrediction models
for storing user data and birth charts.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from src.db.database import Base


class User(Base):
    """User model for storing user account information."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)  # Phase 9: Hashed password
    phone = Column(String, nullable=True)  # Phase 9: Optional phone
    subscription_level = Column(String, default="free", nullable=False)  # Phase 9: free, premium, lifetime
    daily_notifications = Column(String, default="enabled", nullable=False)  # Phase 9: enabled, disabled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    birth_details = relationship("BirthDetail", back_populates="user", cascade="all, delete-orphan")
    saved_predictions = relationship("SavedPrediction", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")  # Phase 9


class BirthDetail(Base):
    """Birth detail model for storing birth chart information."""
    
    __tablename__ = "birth_details"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Birth information
    name = Column(String, nullable=False)
    birth_date = Column(DateTime(timezone=True), nullable=False)
    birth_time = Column(String, nullable=False)  # HH:MM format
    birth_latitude = Column(Float, nullable=False)
    birth_longitude = Column(Float, nullable=False)
    birth_place = Column(String, nullable=False)
    timezone = Column(String, nullable=False)
    
    # Calculated chart data (stored as JSON for flexibility)
    kundli_data = Column(JSON, nullable=True)
    navamsa_data = Column(JSON, nullable=True)
    dasamsa_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="birth_details")


class SavedPrediction(Base):
    """Saved prediction model for storing user's saved predictions."""
    
    __tablename__ = "saved_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Prediction details
    title = Column(String, nullable=False)
    prediction_type = Column(String, nullable=False)  # e.g., "daily", "transit", "dasha"
    prediction_data = Column(JSON, nullable=False)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="saved_predictions")


class Subscription(Base):
    """Phase 9: Subscription model for user subscription management."""
    
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan = Column(String, nullable=False)  # free, premium, lifetime
    starts_on = Column(DateTime(timezone=True), server_default=func.now())
    expires_on = Column(DateTime(timezone=True), nullable=True)  # None for lifetime
    is_active = Column(String, default="active", nullable=False)  # active, expired, cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")


class LoginLog(Base):
    """Phase 9: Login log model for tracking user logins."""
    
    __tablename__ = "login_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    login_time = Column(DateTime(timezone=True), server_default=func.now())
    success = Column(String, default="success", nullable=False)  # success, failed
    
    # Relationships
    user = relationship("User")


class Notification(Base):
    """Phase 10: Notification model for storing daily predictions and notifications."""
    
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    notification_type = Column(String, default="daily", nullable=False)  # daily, alert, reminder
    title = Column(String, nullable=True)
    message = Column(Text, nullable=False)  # Full notification message
    summary = Column(String, nullable=True)  # Short summary for free users
    prediction_data = Column(JSON, nullable=True)  # Full prediction data (JSON)
    is_read = Column(String, default="unread", nullable=False)  # read, unread
    delivery_status = Column(String, default="pending", nullable=False)  # pending, sent, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User")


class Transaction(Base):
    """Phase 11: Transaction model for storing payment transactions."""
    
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan = Column(String, nullable=False)  # premium_monthly, premium_yearly, lifetime
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR", nullable=False)  # INR, USD
    gateway = Column(String, nullable=False)  # razorpay, stripe
    gateway_order_id = Column(String, nullable=True)  # Order ID from gateway
    gateway_payment_id = Column(String, nullable=True)  # Payment ID from gateway
    status = Column(String, default="pending", nullable=False)  # pending, success, failed, refunded
    payment_data = Column(JSON, nullable=True)  # Additional payment data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")


class NotificationPreferences(Base):
    """Phase 12: User notification preferences for multi-channel delivery."""
    
    __tablename__ = "notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    delivery_time = Column(String, default="06:00", nullable=False)  # HH:MM format
    channel_whatsapp = Column(String, default="disabled", nullable=False)  # enabled, disabled
    channel_email = Column(String, default="enabled", nullable=False)  # enabled, disabled
    channel_push = Column(String, default="disabled", nullable=False)  # enabled, disabled
    channel_inapp = Column(String, default="enabled", nullable=False)  # enabled, disabled
    language = Column(String, default="english", nullable=False)  # english, hindi, kannada
    whatsapp_number = Column(String, nullable=True)  # WhatsApp number (if different from phone)
    push_token = Column(String, nullable=True)  # FCM push token
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")


class DeliveryLog(Base):
    """Phase 12: Delivery logs for tracking notification delivery status."""
    
    __tablename__ = "delivery_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    notification_id = Column(Integer, ForeignKey("notifications.id"), nullable=True)
    channel = Column(String, nullable=False)  # whatsapp, email, push, in_app
    status = Column(String, default="pending", nullable=False)  # pending, success, failed
    message_preview = Column(String, nullable=True)  # First 200 chars of message
    error_message = Column(Text, nullable=True)  # Error details if failed
    gateway_response = Column(JSON, nullable=True)  # Gateway response data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    notification = relationship("Notification")


# Phase 14: Ask the Guru - Question storage
class Question(Base):
    """Phase 14: Question model for storing user questions and AI Guru answers."""
    
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")

