"""
Phase 9: Authentication Utilities

Password hashing and verification using bcrypt.
"""

import bcrypt

# Phase 9: Password hashing using bcrypt directly (more reliable)


def hash_password(password: str) -> str:
    """
    Phase 9: Hash a password using bcrypt.
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password string (bcrypt hash)
    """
    # Encode password to bytes
    password_bytes = password.encode('utf-8')
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Phase 9: Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
    
    Returns:
        True if password matches, False otherwise
    """
    try:
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False

