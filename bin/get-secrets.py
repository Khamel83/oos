#!/usr/bin/env python3
"""
Simple AI Secrets Client
No complex interfaces - just works
"""

import os
from pathlib import Path
from dotenv import load_dotenv

class SimpleSecrets:
    def __init__(self):
        load_dotenv()  # Load from .env file

    def get(self, key):
        """Get a secret value"""
        value = os.getenv(key)
        if value:
            # Mask for logging
            masked = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            print(f"🔑 {key}: {masked}")
            return value
        else:
            print(f"❌ Secret not found: {key}")
            return None

    def list_all(self):
        """List all available secrets"""
        print("🔑 Available secrets:")
        for key, value in os.environ.items():
            if any(secret_type in key.upper() for secret_type in ['API', 'KEY', 'SECRET', 'TOKEN']):
                masked = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
                print(f"  • {key}: {masked}")

if __name__ == "__main__":
    import sys
    secrets = SimpleSecrets()

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "get" and len(sys.argv) > 2:
            value = secrets.get(sys.argv[2])
            if value:
                print(value)
        elif command == "list":
            secrets.list_all()
        else:
            print("Usage: python get-secrets.py <get|list> [key]")
    else:
        print("Simple AI Secrets Client")
        print("Usage: python get-secrets.py <command>")
        print("Commands:")
        print("  get <key>    Get a secret value")
        print("  list         List all secrets")
