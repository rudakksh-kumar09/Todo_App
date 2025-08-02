#!/usr/bin/env python3
"""
Generate secure keys for production deployment.
Run this script to generate SECRET_KEY and JWT_SECRET_KEY for your .env file.
"""

import secrets

def generate_secure_key():
    """Generate a secure random key."""
    return secrets.token_hex(32)

if __name__ == "__main__":
    print("Generated secure keys for production:")
    print(f"SECRET_KEY={generate_secure_key()}")
    print(f"JWT_SECRET_KEY={generate_secure_key()}")
    print("\nCopy these values to your Render environment variables.")
