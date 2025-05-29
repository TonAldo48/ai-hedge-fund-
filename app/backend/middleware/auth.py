"""
Authentication middleware for the AI Hedge Fund API.
Provides API key-based authentication for production security.
"""

import os
import secrets
from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.api_key import APIKeyHeader


# Security schemes
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_security = HTTPBearer(auto_error=False)


def generate_api_key() -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)


def get_api_key_from_env() -> Optional[str]:
    """Get API key from environment variables."""
    return os.getenv("API_KEY") or os.getenv("HEDGE_FUND_API_KEY")


async def verify_api_key(
    api_key_header: Optional[str] = Security(api_key_header),
    bearer_token: Optional[HTTPAuthorizationCredentials] = Security(bearer_security)
) -> str:
    """
    Verify API key from either header or bearer token.
    
    Supports two authentication methods:
    1. X-API-Key header
    2. Bearer token in Authorization header
    """
    
    # Get the expected API key from environment
    expected_api_key = get_api_key_from_env()
    
    # If no API key is configured, skip authentication (development mode)
    if not expected_api_key:
        return "development"
    
    # Check API key header first
    if api_key_header and api_key_header == expected_api_key:
        return api_key_header
    
    # Check bearer token
    if bearer_token and bearer_token.credentials == expected_api_key:
        return bearer_token.credentials
    
    # No valid authentication found
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def verify_api_key_optional(
    api_key_header: Optional[str] = Security(api_key_header),
    bearer_token: Optional[HTTPAuthorizationCredentials] = Security(bearer_security)
) -> Optional[str]:
    """
    Optional API key verification for public endpoints.
    Returns None if no authentication is provided, otherwise validates the key.
    """
    
    # If no authentication provided, allow access
    if not api_key_header and not bearer_token:
        return None
    
    # If authentication is provided, it must be valid
    return await verify_api_key(api_key_header, bearer_token) 