"""
Phase 12: Push Notification Channel

Push notification delivery via Firebase Cloud Messaging (FCM) using Admin SDK (HTTP v1).
"""

import os
from typing import Dict, Optional, List

from src.config import settings

# Phase 12: Firebase Admin SDK initialization
_firebase_app = None
_fcm_initialized = False


def _initialize_firebase():
    """
    Phase 12: Initialize Firebase Admin SDK.
    
    Supports two methods:
    1. Service Account JSON file (recommended)
    2. Environment variables (GOOGLE_APPLICATION_CREDENTIALS)
    """
    global _firebase_app, _fcm_initialized
    
    if _fcm_initialized:
        return _firebase_app
    
    try:
        import firebase_admin
        from firebase_admin import credentials, messaging
        
        # Check if already initialized
        try:
            _firebase_app = firebase_admin.get_app()
            _fcm_initialized = True
            return _firebase_app
        except ValueError:
            pass  # Not initialized yet
        
        # Method 1: Service Account JSON file (recommended)
        service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if service_account_path and os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
            _firebase_app = firebase_admin.initialize_app(cred)
            _fcm_initialized = True
            return _firebase_app
        
        # Method 2: Use default credentials (if set via gcloud)
        try:
            _firebase_app = firebase_admin.initialize_app()
            _fcm_initialized = True
            return _firebase_app
        except Exception:
            pass
        
        # Method 3: Fallback - try to use FCM_SERVER_KEY for legacy (if still available)
        fcm_server_key = os.getenv("FCM_SERVER_KEY")
        if fcm_server_key:
            print("Warning: Using legacy FCM_SERVER_KEY. Consider migrating to Firebase Admin SDK.")
            _fcm_initialized = True  # Mark as initialized but use legacy method
            return None
        
        return None
    
    except ImportError:
        print("Warning: firebase-admin not installed. Push notifications will not work.")
        return None
    except Exception as e:
        print(f"Warning: Could not initialize Firebase: {e}")
        return None


def send_push(token: str, title: str, message: str, data: Optional[Dict] = None) -> Dict:
    """
    Phase 12: Send push notification via FCM using Firebase Admin SDK (HTTP v1).
    
    Args:
        token: FCM device token
        title: Notification title
        message: Notification message body
        data: Optional additional data payload
    
    Returns:
        Dictionary with success status
    """
    # Initialize Firebase
    app = _initialize_firebase()
    
    # Fallback to legacy API if Admin SDK not available
    if not app and not _fcm_initialized:
        return {
            "success": False,
            "error": "Firebase not initialized. Set GOOGLE_APPLICATION_CREDENTIALS or use legacy FCM_SERVER_KEY."
        }
    
    try:
        if app:
            # Use Firebase Admin SDK (HTTP v1 - Modern)
            from firebase_admin import messaging
            
            # Build notification
            notification = messaging.Notification(
                title=title,
                body=message
            )
            
            # Build message
            message_obj = messaging.Message(
                notification=notification,
                token=token,
                data=data if data else {}
            )
            
            # Send
            response = messaging.send(message_obj)
            
            return {
                "success": True,
                "message_id": response,
                "method": "firebase_admin_sdk"
            }
        
        else:
            # Fallback to legacy API (if FCM_SERVER_KEY is set)
            return _send_push_legacy(token, title, message, data)
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def _send_push_legacy(token: str, title: str, message: str, data: Optional[Dict] = None) -> Dict:
    """
    Phase 12: Legacy FCM API (fallback only).
    
    This method is deprecated but kept for backward compatibility.
    """
    import requests
    
    fcm_server_key = os.getenv("FCM_SERVER_KEY")
    if not fcm_server_key:
        return {
            "success": False,
            "error": "FCM_SERVER_KEY not configured"
        }
    
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        headers = {
            "Authorization": f"key={fcm_server_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "to": token,
            "notification": {
                "title": title,
                "body": message
            }
        }
        
        if data:
            payload["data"] = data
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success") == 1:
                return {
                    "success": True,
                    "message_id": result.get("results", [{}])[0].get("message_id"),
                    "method": "legacy_api"
                }
            else:
                return {
                    "success": False,
                    "error": result.get("results", [{}])[0].get("error", "Unknown FCM error")
                }
        else:
            return {
                "success": False,
                "error": f"FCM API error: {response.status_code} - {response.text}"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def send_push_multicast(tokens: List[str], title: str, message: str, data: Optional[Dict] = None) -> Dict:
    """
    Phase 12: Send push notification to multiple devices using Firebase Admin SDK.
    
    Args:
        tokens: List of FCM device tokens
        title: Notification title
        message: Notification message body
        data: Optional additional data payload
    
    Returns:
        Dictionary with success status and results
    """
    # Initialize Firebase
    app = _initialize_firebase()
    
    if not app:
        return {
            "success": False,
            "error": "Firebase not initialized. Set GOOGLE_APPLICATION_CREDENTIALS."
        }
    
    try:
        from firebase_admin import messaging
        
        # Build notification
        notification = messaging.Notification(
            title=title,
            body=message
        )
        
        # Build multicast message
        message_obj = messaging.MulticastMessage(
            notification=notification,
            tokens=tokens,
            data=data if data else {}
        )
        
        # Send
        response = messaging.send_multicast(message_obj)
        
        return {
            "success": True,
            "success_count": response.success_count,
            "failure_count": response.failure_count,
            "results": [
                {
                    "success": r.success,
                    "message_id": r.message_id if r.success else None,
                    "error": str(r.exception) if r.exception else None
                }
                for r in response.responses
            ],
            "method": "firebase_admin_sdk"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

