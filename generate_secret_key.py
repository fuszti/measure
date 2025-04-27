#!/usr/bin/env python
"""
Generate a secure random key for JWT authentication
"""
import secrets
import argparse

def generate_key(length=32):
    """Generate a random hexadecimal string of the given length."""
    return secrets.token_hex(length)

def main():
    parser = argparse.ArgumentParser(description='Generate a secure random key for authentication')
    parser.add_argument('--length', type=int, default=32, help='Length of the key in bytes (default: 32)')
    args = parser.parse_args()
    
    key = generate_key(args.length)
    print(f"Generated SECRET_KEY:")
    print(key)
    print("\nAdd this to your environment variables:")
    print(f"export SECRET_KEY={key}")
    print("\nOr for Docker Compose:")
    print(f"SECRET_KEY={key}")

if __name__ == "__main__":
    main()