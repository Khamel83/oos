#!/usr/bin/env python3
"""
Test if these models can actually do REAL work
"""

import json
import os

import requests
from dotenv import load_dotenv

load_dotenv('/home/ubuntu/dev/oos/.env')
api_key = os.getenv('OPENROUTER_PROJECT_KEY')

def test_real_task(model_id, task_name, prompt):
    """Test model with actual work task"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/Khamel83/oos",
        "X-Title": "SOLO CREATOR MECHA SUIT Real Test"
    }

    data = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.1
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            response_text = result["choices"][0]["message"]["content"]
            usage = result.get("usage", {})

            return {
                "status": "SUCCESS",
                "response": response_text,
                "tokens_used": usage.get("total_tokens", 0),
                "cost_estimate": usage.get("total_tokens", 0) * 0.00002  # Rough estimate
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
    """Test models with real work tasks"""

    print("🧪 TESTING MODELS WITH REAL WORK TASKS")
    print("=" * 60)

    # Test the top working models
    models_to_test = [
        ("google/gemma-2-9b-it", "Gemma-2-9B (Default)"),
        ("qwen/qwen-2.5-72b-instruct", "Qwen2.5-72B (Maximum)"),
        ("meta-llama/llama-3.1-70b-instruct", "Llama-3.1-70B (Coding)"),
        ("openrouter/andromeda-alpha", "Andromeda Alpha (Free)")
    ]

    # Real work tasks to test
    test_tasks = [
        {
            "name": "Task Planning",
            "prompt": """Create a step-by-step plan to build a simple todo list application. Include:
1. Technology stack recommendations
2. Core features to implement
3. Step-by-step development roadmap
4. Testing strategy
Keep it practical and actionable."""
        },
        {
            "name": "Code Generation",
            "prompt": """Write a Python function that validates CSV data and calculates statistics. The function should:
1. Take a CSV file path as input
2. Validate the CSV format
3. Calculate basic statistics (row count, column count, data types)
4. Handle errors gracefully
Provide working code with documentation."""
        },
        {
            "name": "Business Analysis",
            "prompt": """Analyze this business situation:
A solo creator wants to launch a digital product but has limited budget ($500) and time (10 hours/week).

Provide specific recommendations for:
1. Product type selection (high value, low time investment)
2. Marketing strategy (free/low-cost channels)
3. Monetization approach
4. Timeline and milestones
Be specific and actionable."""
        },
        {
            "name": "Problem Solving",
            "prompt": """Solve this step-by-step:
A user needs to organize 1000+ files into categories. Files have names like:
- "Project_Report_2024_Q3.pdf"
- "Meeting_Notes_ClientA.docx"
- "Invoice_123_Sept2024.xlsx"

Create an automated file organization system that:
1. Extracts key information from filenames
2. Categorizes files intelligently
3. Creates appropriate folder structure
4. Provides Python code to implement the solution"""
        }
    ]

    results = {}

    for model_id, model_name in models_to_test:
        print(f"\n🎯 TESTING {model_name}")
        print("-" * 40)

        model_results = {}

        for task in test_tasks:
            print(f"\n📋 Task: {task['name']}")

            result = test_real_task(model_id, task['name'], task['prompt'])
            model_results[task['name']] = result

            if result['status'] == 'SUCCESS':
                response_length = len(result['response'])
                print(f"✅ SUCCESS - {response_length} chars, {result['tokens_used']} tokens")

                # Quick quality check
                if 'def ' in result['response'] or '1.' in result['response'] or 'Python' in result['response']:
                    print("   📝 Appears to be substantive content")
                else:
                    print("   ⚠️  May be low-quality or generic response")

            else:
                print(f"❌ FAILED: {result['error']}")

        results[model_id] = {
            "model_name": model_name,
            "tasks": model_results,
            "summary": {
                "total_tasks": len(test_tasks),
                "successful": sum(1 for t in model_results.values() if t['status'] == 'SUCCESS'),
                "failed": sum(1 for t in model_results.values() if t['status'] != 'SUCCESS')
            }
        }

    # Save results
    with open('/home/ubuntu/dev/oos/real_model_capability_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n📊 SUMMARY")
    print("=" * 60)

    for model_id, data in results.items():
        summary = data['summary']
        success_rate = (summary['successful'] / summary['total_tasks']) * 100
        print(f"{data['model_name']}: {summary['successful']}/{summary['total_tasks']} tasks ({success_rate:.0f}%)")

    print("\n💾 Detailed results saved to: real_model_capability_test_results.json")

    return results

if __name__ == "__main__":
    main()
