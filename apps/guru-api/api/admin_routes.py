"""
Phase 21: Admin Routes for API Key Management

Protected admin endpoints for managing API keys.
"""

import os
import secrets
from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import Dict
from pydantic import BaseModel
from datetime import datetime
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from api.firebase_auth import initialize_firebase, clear_api_keys_cache

# Firebase imports
try:
    from firebase_admin import firestore
except ImportError:
    firestore = None

router = APIRouter()


class CreateKeyRequest(BaseModel):
    """Request model for creating API key."""
    name: str
    description: str = ""


def verify_master_admin_key(request: Request) -> bool:
    """
    Verify master admin key from request.
    
    Args:
        request: FastAPI request
    
    Returns:
        True if valid
    
    Raises:
        HTTPException: If invalid
    """
    master_key = request.headers.get("x-master-admin-key")
    expected_key = os.getenv("MASTER_ADMIN_KEY")
    
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Master admin key not configured"
        )
    
    if not master_key or master_key != expected_key:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid master admin key"
        )
    
    return True


def generate_secure_api_key(length: int = 48) -> str:
    """
    Generate a secure random API key.
    
    Args:
        length: Length of the key (default: 48)
    
    Returns:
        Secure API key string
    """
    return secrets.token_urlsafe(length)


@router.post("/create-key", response_model=Dict)
async def create_api_key(
    request: Request,
    key_request: CreateKeyRequest,
    _: bool = Depends(verify_master_admin_key)
):
    """
    Create a new API key and store in Firestore.
    
    POST /api/admin/create-key
    Requires: x-master-admin-key header
    """
    db = initialize_firebase()
    
    if not db:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Firebase not initialized. Check GOOGLE_APPLICATION_CREDENTIALS."
        )
    
    # Generate secure API key
    api_key = generate_secure_api_key(64)
    
    # Store in Firestore
    try:
        api_keys_ref = db.collection('api_keys')
        doc_ref = api_keys_ref.document()
        
        doc_ref.set({
            'key': api_key,
            'name': key_request.name,
            'description': key_request.description,
            'active': True,
            'created_at': firestore.SERVER_TIMESTAMP,
            'created_by': request.client.host if request.client else 'unknown',
            'last_used': None,
            'usage_count': 0
        })
        
        # Clear cache to force reload
        clear_api_keys_cache()
        
        return {
            "success": True,
            "api_key": api_key,
            "name": key_request.name,
            "message": "API key created successfully. Save this key securely - it won't be shown again.",
            "created_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating API key: {str(e)}"
        )


@router.get("/list-keys", response_model=Dict)
async def list_api_keys(
    request: Request,
    _: bool = Depends(verify_master_admin_key)
):
    """
    List all API keys (without showing the actual keys).
    
    GET /api/admin/list-keys
    Requires: x-master-admin-key header
    """
    db = initialize_firebase()
    
    if not db:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Firebase not initialized."
        )
    
    try:
        api_keys_ref = db.collection('api_keys')
        docs = api_keys_ref.stream()
        
        keys_list = []
        for doc in docs:
            data = doc.to_dict()
            keys_list.append({
                'id': doc.id,
                'name': data.get('name', ''),
                'description': data.get('description', ''),
                'active': data.get('active', True),
                'created_at': data.get('created_at'),
                'last_used': data.get('last_used'),
                'usage_count': data.get('usage_count', 0),
                'key_preview': data.get('key', '')[:8] + '...' if data.get('key') else ''
            })
        
        return {
            "success": True,
            "keys": keys_list,
            "count": len(keys_list)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing API keys: {str(e)}"
        )


@router.post("/deactivate-key/{key_id}", response_model=Dict)
async def deactivate_api_key(
    request: Request,
    key_id: str,
    _: bool = Depends(verify_master_admin_key)
):
    """
    Deactivate an API key.
    
    POST /api/admin/deactivate-key/{key_id}
    Requires: x-master-admin-key header
    """
    db = initialize_firebase()
    
    if not db:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Firebase not initialized."
        )
    
    try:
        doc_ref = db.collection('api_keys').document(key_id)
        doc_ref.update({'active': False})
        
        clear_api_keys_cache()
        
        return {
            "success": True,
            "message": f"API key {key_id} deactivated successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deactivating API key: {str(e)}"
        )

