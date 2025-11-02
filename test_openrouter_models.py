#!/usr/bin/env python3
"""
Comprehensive OpenRouter model testing with fallback keys
"""

import json
import os

import requests


# Load credentials
def load_credentials():
    """Load OpenRouter credentials from environment"""
    keys = [
        os.getenv('OPENROUTER_PROJECT_KEY'),  # New project key first
        os.getenv('OPENROUTER_API_KEY'),
        os.getenv('OPENROUTER_FALLBACK_KEY')
    ]
    return [k for k in keys if k and k.strip()]

def test_api_key(api_key: str) -> tuple[bool, str]:
    """Test if an API key works"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/Khamel83/oos",
        "X-Title": "SOLO CREATOR MECHA SUIT"
    }

    data = {
        "model": "openai/gpt-4o-mini",
        "messages": [{"role": "user", "content": "Say 'API_WORKING'"}],
        "max_tokens": 20
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )

        if response.status_code == 200:
            return True, "API key works"
        else:
            return False, f"HTTP {response.status_code}: {response.json().get('error', {}).get('message', 'Unknown error')}"

    except Exception as e:
        return False, f"Exception: {str(e)}"

def get_working_api_key() -> str:
    """Find a working API key"""
    keys = load_credentials()

    print(f"🔑 Testing {len(keys)} OpenRouter API keys...")

    for i, key in enumerate(keys, 1):
        print(f"Testing key {i} ending in {key[-10:]}...")
        works, message = test_api_key(key)

        if works:
            print(f"✅ Key {i} works: {message}")
            return key
        else:
            print(f"❌ Key {i} failed: {message}")

    return None

def test_model_access(api_key: str, model_id: str, model_name: str) -> dict:
    """Test access to a specific model"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/Khamel83/oos",
        "X-Title": "SOLO CREATOR MECHA SUIT Model Test"
    }

    # Simple test prompt
    data = {
        "model": model_id,
        "messages": [{"role": "user", "content": "Respond with 'MODEL_ACCESS_CONFIRMED' if you can receive this."}],
        "max_tokens": 30
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=15
        )

        if response.status_code == 200:
            result = response.json()
            return {
                "status": "SUCCESS",
                "response": result["choices"][0]["message"]["content"][:100],
                "usage": result.get("usage", {}),
                "model": result.get("model", model_id)
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

def test_key_models():
    """Test key models under $1/M cost ceiling"""

    # Load working API key
    working_key = get_working_api_key()

    if not working_key:
        print("❌ No working OpenRouter API keys found!")
        return {}

    print(f"\n🎯 Using working key ending in {working_key[-10:]}")
    print("📊 Testing models under $1/M cost ceiling...\n")

    # Key models to test (from your cost table under $1/M)
    test_models = [
        # Free models
        ("openrouter/andromeda-alpha", "Andromeda Alpha (Free)"),
        ("google/gemma-2-9b-it:free", "Gemma-2-9B Free"),
        ("meta-llama/llama-3.1-8b-instruct:free", "Llama-3.1-8B Free"),

        # Ultra cheap models under $0.10/M
        ("agentica-org/deepcoder-14b-preview", "Deepcoder 14B - $0.015/M"),
        ("arliai/qwq-32b-arliai-rpr-v1", "QwQ 32B - $0.07/M"),
        ("amazon/nova-micro-v1", "Amazon Nova Micro - $0.09/M"),

        # Good value models under $0.50/M
        ("google/gemma-2-9b-it", "Gemma-2-9B - $0.02/M"),
        ("meta-llama/llama-3.1-8b-instruct", "Llama-3.1-8B - $0.025/M"),
        ("mistralai/mistral-nemo", "Mistral Nemo - $0.03/M"),

        # Premium models under $1.00/M
        ("qwen/qwen-2.5-72b-instruct", "Qwen2.5-72B - $0.165/M"),
        ("openai/gpt-4o-mini", "GPT-4o-mini - $0.375/M"),
        ("meta-llama/llama-3.1-70b-instruct", "Llama-3.1-70B - $0.40/M"),
    ]

    results = {}
    successful_tests = 0

    for model_id, model_name in test_models:
        print(f"Testing {model_name}...")
        result = test_model_access(working_key, model_id, model_name)
        results[model_id] = result

        if result["status"] == "SUCCESS":
            successful_tests += 1
            print(f"  ✅ SUCCESS - {result['response'][:50]}...")

            # Show usage if available
            usage = result.get('usage', {})
            if usage:
                print(f"  📊 Tokens: {usage.get('total_tokens', 'N/A')} (Input: {usage.get('prompt_tokens', 'N/A')}, Output: {usage.get('completion_tokens', 'N/A')})")
        else:
            print(f"  ❌ {result['error']}")

        print()

    # Summary
    print(f"📊 SUMMARY: {successful_tests}/{len(test_models)} models accessible")

    # Save results
    with open('/home/ubuntu/dev/oos/openrouter_model_test_results.json', 'w') as f:
        json.dump({
            "working_api_key": working_key[-10:] + "...",
            "total_tested": len(test_models),
            "successful": successful_tests,
            "results": results
        }, f, indent=2)

    print("💾 Results saved to: openrouter_model_test_results.json")

    return results

def main():
    """Run comprehensive OpenRouter model testing"""
    print("🚀 SOLO CREATOR MECHA SUIT - OpenRouter Model Testing")
    print("=" * 60)

    # Load environment
    from dotenv import load_dotenv
    load_dotenv('/home/ubuntu/dev/oos/.env')

    results = test_key_models()

    if results:
        working_models = [model_id for model_id, result in results.items() if result["status"] == "SUCCESS"]

        if working_models:
            print("\n🎯 RECOMMENDED MODEL STRATEGY:")
            print(f"• DEFAULT: {working_models[0]} (first working model)")
            print(f"• ALTERNATIVES: {len(working_models)-1} other working models")
            print("• COST ESTIMATE: ~$0.02-$0.40 per 1M tokens depending on selection")
        else:
            print("\n❌ No working models found. Check API key or model availability.")

if __name__ == "__main__":
    main()
