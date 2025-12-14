"""
Phase 10: Notification Sender

Placeholder for email and push notification delivery.
Future integration points for SMTP and mobile push services.
"""

from typing import Optional
from src.db.models import Notification, User


def send_email(to: str, subject: str, body: str) -> bool:
    """
    Phase 10: Send email notification (placeholder).
    
    Future integration:
    - SMTP server configuration
    - Email templates
    - HTML email support
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body
    
    Returns:
        True if sent successfully, False otherwise
    """
    # TODO: Integrate SMTP server
    # Example: Use smtplib or SendGrid/Mailgun API
    print(f"[EMAIL] To: {to}, Subject: {subject}")
    return True


def send_push(user_id: int, message: str) -> bool:
    """
    Phase 10: Send push notification (placeholder).
    
    Future integration:
    - Firebase Cloud Messaging (FCM)
    - Apple Push Notification Service (APNs)
    - Web Push API
    
    Args:
        user_id: User ID
        message: Push notification message
    
    Returns:
        True if sent successfully, False otherwise
    """
    # TODO: Integrate push notification service
    # Example: Use FCM or APNs
    print(f"[PUSH] User: {user_id}, Message: {message[:50]}...")
    return True


def deliver_notification(notification: Notification, user: User) -> bool:
    """
    Phase 10: Deliver notification through all enabled channels.
    
    Args:
        notification: Notification object
        user: User object
    
    Returns:
        True if at least one channel succeeded
    """
    success = False
    
    # Store in database (always done)
    # This is handled by notification_engine
    
    # Email delivery (if user has email and preferences allow)
    if user.email:
        try:
            email_sent = send_email(
                to=user.email,
                subject=notification.title or "Daily Horoscope",
                body=notification.message
            )
            if email_sent:
                success = True
        except Exception as e:
            print(f"Email delivery failed for user {user.id}: {e}")
    
    # Push notification (if user has device tokens)
    try:
        push_sent = send_push(user.id, notification.summary or notification.message)
        if push_sent:
            success = True
    except Exception as e:
        print(f"Push delivery failed for user {user.id}: {e}")
    
    return success

