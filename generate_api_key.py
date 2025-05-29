#!/usr/bin/env python3
"""
Generate a secure API key for the AI Hedge Fund API.
"""

import secrets
import os


def generate_api_key() -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)


def main():
    """Generate and display an API key."""
    api_key = generate_api_key()
    
    print("🔐 AI Hedge Fund API - Secure Key Generator")
    print("=" * 50)
    print(f"Generated API Key: {api_key}")
    print()
    print("📋 Setup Instructions:")
    print("1. Copy this API key")
    print("2. For local development:")
    print(f"   Add to .env file: API_KEY={api_key}")
    print("3. For Railway deployment:")
    print(f"   Set environment variable: API_KEY={api_key}")
    print("   Or: HEDGE_FUND_API_KEY={api_key}")
    print()
    print("🔑 Usage Examples:")
    print("Header method:")
    print(f'   curl -H "X-API-Key: {api_key}" ...')
    print("Bearer token method:")
    print(f'   curl -H "Authorization: Bearer {api_key}" ...')
    print()
    print("⚠️  Security Notes:")
    print("- Keep this key secret and secure")
    print("- Don't commit it to version control")
    print("- Rotate regularly for production use")
    print("- Use environment variables only")


if __name__ == "__main__":
    main() 