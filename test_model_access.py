#!/usr/bin/env python3
"""
Test which models we actually have access to with current OpenRouter setup
"""

import os
import requests
import json

def test_model_access(model_id, model_name):
    """Test if we can actually call this model"""
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        return {"error": "No API key found"}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/Khamel83/oos",
        "X-Title": "Access Test"
    }

    data = {
        "model": model_id,
        "messages": [{"role": "user", "content": "Say 'ACCESS TEST' if you can receive this"}],
        "max_tokens": 10
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            return {
                "status": "SUCCESS",
                "response": result["choices"][0]["message"]["content"],
                "usage": result.get("usage", {})
            }
        else:
            return {
                "status": "FAILED",
                "error": f"HTTP {response.status_code}: {response.text[:200]}"
            }

    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e)
        }

def main():
    """Test access to our recommended models"""
    print("🔍 TESTING ACTUAL MODEL ACCESS\n")

    # Models we recommended
    test_models = [
        ("google/gemma-2-9b-it", "Gemma-2-9B (DEFAULT)"),
        ("google/gemma-2-9b-it:free", "Gemma-2-9B Free"),
        ("qwen/qwen-2.5-coder-32b-instruct", "Qwen2.5-Coder-32B"),
        ("meta-llama/llama-3.1-70b-instruct", "Llama-3.1-70B"),
        ("deepseek/deepseek-r1:free", "DeepSeek R1 Free"),
        ("google/gemma-3-27b-it:free", "Gemma-3-27B Free")
    ]

    results = {}

    for model_id, model_name in test_models:
        print(f"Testing {model_name}...")
        result = test_model_access(model_id, model_name)
        results[model_id] = result

        if result.get("status") == "SUCCESS":
            print(f"  ✅ ACCESS CONFIRMED")
        else:
            print(f"  ❌ {result.get('error', 'Unknown error')}")
        print()

    # Save results
    with open('/home/ubuntu/dev/oos/model_access_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("Results saved to: model_access_test_results.json")

    # Summary
    successful = sum(1 for r in results.values() if r.get("status") == "SUCCESS")
    print(f"\n📊 SUMMARY: {successful}/{len(test_models)} models accessible")

if __name__ == "__main__":
    main()