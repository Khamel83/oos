#!/usr/bin/env python3
"""
Access Archon vault secrets using direct API calls
"""

import json

import requests


def get_vault_secrets(password: str) -> dict:
    """Access Archon vault and retrieve secrets"""

    # Try direct vault API access
    vault_url = "https://archon.khamel.com"

    # First login to get session
    login_data = {
        "password": password
    }

    try:
        # Login to vault
        login_response = requests.post(f"{vault_url}/api/login", json=login_data, timeout=10)

        if login_response.status_code == 200:
            session_data = login_response.json()
            token = session_data.get("token")

            if token:
                # Get secrets with token
                headers = {"Authorization": f"Bearer {token}"}
                secrets_response = requests.get(f"{vault_url}/api/secrets", headers=headers, timeout=10)

                if secrets_response.status_code == 200:
                    secrets = secrets_response.json()
                    return {"status": "success", "secrets": secrets}

    except Exception:
        pass

    # Fallback: try common API patterns
    api_patterns = [
        f"{vault_url}/vault/api/secrets",
        f"{vault_url}/api/v1/secrets",
        f"{vault_url}/api/credentials"
    ]

    for pattern in api_patterns:
        try:
            response = requests.get(pattern, timeout=5)
            if response.status_code == 200:
                return {"status": "success", "secrets": response.json()}
        except:
            continue

    return {"status": "failed", "error": "Could not access vault API"}

def main():
    """Get secrets from Archon vault"""
    password = "vMbzKLi68ENeK9vRzBKH"

    print("🔐 Accessing Archon vault...")

    result = get_vault_secrets(password)

    if result["status"] == "success":
        secrets = result["secrets"]

        # Look for AI-related secrets
        ai_keys = {}
        for key, value in secrets.items() if isinstance(secrets, dict) else []:
            if any(keyword in key.lower() for keyword in [
                "openrouter", "anthropic", "openai", "claude", "gpt", "api_key"
            ]):
                ai_keys[key] = value

        print(f"✅ Found {len(ai_keys)} AI-related secrets:")
        for key, value in ai_keys.items():
            print(f"  • {key}: {'*' * 20}...{value[-10:] if value else 'None'}")

        # Save for system use
        with open('/home/ubuntu/dev/oos/archon_secrets.json', 'w') as f:
            json.dump(ai_keys, f, indent=2)

        print("\n📁 Secrets saved to: archon_secrets.json")

        return ai_keys

    else:
        print(f"❌ Failed to access vault: {result.get('error', 'Unknown error')}")
        return {}

if __name__ == "__main__":
    main()
