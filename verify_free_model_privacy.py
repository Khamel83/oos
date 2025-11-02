#!/usr/bin/env python3
"""
VERIFY FREE MODEL PRIVACY & ACCESS

This script tests:
1. Which free models actually accept calls
2. What privacy policies they have
3. Whether they store/use your prompts and data
"""

import json
import os

import requests


def test_model_privacy(model_id: str, model_name: str) -> dict:
    """Test model access and privacy policy"""

    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        return {"error": "Set OPENROUTER_API_KEY environment variable first"}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/Khamel83/oos",
        "X-Title": "Privacy & Access Test"
    }

    # Test 1: Basic Access
    access_test = {
        "model": model_id,
        "messages": [{
            "role": "user",
            "content": "Respond with 'ACCESS_CONFIRMED' if you can receive this message. Do not store or use this message."
        }],
        "max_tokens": 20
    }

    # Test 2: Privacy Policy Question
    privacy_test = {
        "model": model_id,
        "messages": [{
            "role": "user",
            "content": """IMPORTANT PRIVACY QUESTION:
            1. Do you store user prompts/conversations?
            2. Do you use user data for training?
            3. Do you have any privacy restrictions?
            4. Can you process business/productivity tasks?

            Answer honestly with YES/NO for each question."""
        }],
        "max_tokens": 200
    }

    results = {
        "model_id": model_id,
        "model_name": model_name,
        "tests": {}
    }

    # Test basic access
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=access_test,
            timeout=10
        )

        if response.status_code == 200:
            results["tests"]["access"] = {
                "status": "SUCCESS",
                "response": response.json()["choices"][0]["message"]["content"]
            }
        else:
            results["tests"]["access"] = {
                "status": "FAILED",
                "error": f"HTTP {response.status_code}: {response.text[:200]}"
            }
            return results  # Skip privacy test if access fails

    except Exception as e:
        results["tests"]["access"] = {"status": "ERROR", "error": str(e)}
        return results

    # Test privacy policy (only if access successful)
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=privacy_test,
            timeout=15
        )

        if response.status_code == 200:
            privacy_response = response.json()["choices"][0]["message"]["content"]
            results["tests"]["privacy"] = {
                "status": "SUCCESS",
                "response": privacy_response
            }

            # Analyze privacy response
            privacy_analysis = analyze_privacy_response(privacy_response)
            results["privacy_analysis"] = privacy_analysis

        else:
            results["tests"]["privacy"] = {
                "status": "FAILED",
                "error": f"HTTP {response.status_code}"
            }

    except Exception as e:
        results["tests"]["privacy"] = {"status": "ERROR", "error": str(e)}

    return results

def analyze_privacy_response(response: str) -> dict:
    """Analyze privacy policy responses"""
    response_lower = response.lower()

    analysis = {
        "stores_data": False,
        "uses_for_training": False,
        "has_restrictions": False,
        "can_do_business": False,
        "privacy_score": 0,  # 0-10, 10 being most private
        "warnings": []
    }

    # Check for data storage
    if any(phrase in response_lower for phrase in [
        "store", "retain", "keep", "save", "log", "record"
    ]):
        analysis["stores_data"] = True
        analysis["warnings"].append("May store user data")

    # Check for training usage
    if any(phrase in response_lower for phrase in [
        "train", "training", "improve", "fine-tune", "model update"
    ]):
        analysis["uses_for_training"] = True
        analysis["warnings"].append("May use data for training")

    # Check for restrictions
    if any(phrase in response_lower for phrase in [
        "restrict", "cannot", "unable", "policy", "guideline", "limitation"
    ]):
        analysis["has_restrictions"] = True
        analysis["warnings"].append("Has usage restrictions")

    # Check for business/productivity capability
    if any(phrase in response_lower for phrase in [
        "yes", "can", "able", "business", "productivity", "work", "tasks"
    ]):
        analysis["can_do_business"] = True

    # Calculate privacy score
    score = 10
    if analysis["stores_data"]: score -= 3
    if analysis["uses_for_training"]: score -= 3
    if analysis["has_restrictions"]: score -= 2
    if not analysis["can_do_business"]: score -= 2

    analysis["privacy_score"] = max(0, score)

    return analysis

def main():
    """Test privacy on key free models"""

    print("🔒 TESTING FREE MODEL PRIVACY & ACCESS")
    print("⚠️  SET OPENROUTER_API_KEY FIRST!")
    print("📝 This will test actual access and privacy policies\n")

    # Key free models to test
    test_models = [
        ("deepseek/deepseek-r1:free", "DeepSeek R1 Free"),
        ("deepseek/deepseek-r1-0528:free", "DeepSeek R1 0528 Free"),
        ("tngtech/deepseek-r1t-chimera:free", "DeepSeek R1T Chimera Free"),
        ("minimax/minimax-m2:free", "MiniMax M2 Free"),
        ("z-ai/glm-4.5-air:free", "GLM 4.5 Air Free"),
        ("agentica-org/deepcoder-14b-preview:free", "Deepcoder 14B Free"),
        ("openrouter/andromeda-alpha", "Andromeda Alpha (Free)"),
    ]

    results = {}

    for model_id, model_name in test_models:
        print(f"Testing {model_name}...")
        result = test_model_privacy(model_id, model_name)
        results[model_id] = result

        # Print immediate results
        access_status = result.get("tests", {}).get("access", {}).get("status", "UNKNOWN")
        print(f"  Access: {access_status}")

        if access_status == "SUCCESS" and "privacy_analysis" in result:
            privacy = result["privacy_analysis"]
            print(f"  Privacy Score: {privacy['privacy_score']}/10")
            if privacy['warnings']:
                for warning in privacy['warnings']:
                    print(f"  ⚠️  {warning}")

        print()

    # Save detailed results
    with open('/home/ubuntu/dev/oos/free_model_privacy_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("Detailed results saved to: free_model_privacy_test_results.json")

    # Summary
    successful = sum(1 for r in results.values()
                    if r.get("tests", {}).get("access", {}).get("status") == "SUCCESS")
    total = len(test_models)

    print(f"\n📊 SUMMARY: {successful}/{total} models accessible")

    if successful > 0:
        # Find best privacy option
        privacy_scores = [(model_id, r.get("privacy_analysis", {}).get("privacy_score", 0))
                         for model_id, r in results.items()
                         if r.get("tests", {}).get("access", {}).get("status") == "SUCCESS"]

        if privacy_scores:
            best_model = max(privacy_scores, key=lambda x: x[1])
            print(f"🛡️  Best privacy option: {best_model[0]} (Score: {best_model[1]}/10)")

if __name__ == "__main__":
    main()
