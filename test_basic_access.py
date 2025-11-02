#!/usr/bin/env python3
"""
Test basic OpenRouter API access
"""

import os
import requests
import json

def test_basic_api():
    api_key = os.getenv('OPENROUTER_API_KEY', 'sk-or-v1-7b8edf6b7c8e4b9c8e7b6c5d4e3f2a1b')

    print(f"Testing API with key ending in: {api_key[-10:]}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/Khamel83/oos",
        "X-Title": "Basic Access Test"
    }

    # Test with a standard paid model first
    data = {
        "model": "openai/gpt-4o-mini",
        "messages": [{"role": "user", "content": "Say 'API_TEST_SUCCESS'"}],
        "max_tokens": 20
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: {result['choices'][0]['message']['content']}")
            return True
        else:
            print(f"❌ FAILED: {response.text}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    test_basic_api()