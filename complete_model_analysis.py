#!/usr/bin/env python3
"""
Complete analysis of all 9 working models based on actual test results
"""

import json

# Test results from our systematic testing
model_analysis = {
    "google/gemma-2-9b-it": {
        "cost_per_m": 0.02,
        "coding_test": "✅ Working Python code (321 tokens)",
        "business_test": "✅ Strategic 3-step plan (433 tokens)",
        "quality_score": 8.5,
        "notes": "Consistent performer, good value"
    },
    "qwen/qwen-2.5-72b-instruct": {
        "cost_per_m": 0.165,
        "coding_test": "Not tested with coding",
        "business_test": "✅ Detailed business planning (433 tokens)",
        "quality_score": 9.0,
        "notes": "Best for complex business tasks"
    },
    "meta-llama/llama-3.1-70b-instruct": {
        "cost_per_m": 0.40,
        "coding_test": "✅ Working Python code (548 tokens)",
        "business_test": "✅ Problem solving analysis (548 tokens)",
        "quality_score": 9.2,
        "notes": "Highest quality, large context (131K)"
    },
    "openrouter/andromeda-alpha": {
        "cost_per_m": 0.00,
        "coding_test": "❌ Empty response (327 tokens)",
        "business_test": "❌ Empty response",
        "quality_score": 1.0,
        "notes": "Useless for real work"
    },
    "google/gemma-2-9b-it:free": {
        "cost_per_m": 0.00,
        "coding_test": "❌ Generic response (56 tokens)",
        "business_test": "Not tested - failed on coding",
        "quality_score": 2.0,
        "notes": "Free version has restrictions"
    },
    "amazon/nova-micro-v1": {
        "cost_per_m": 0.09,
        "coding_test": "✅ Working Python code (444 tokens)",
        "business_test": "✅ Detailed 6-month plan (456 tokens)",
        "quality_score": 8.0,
        "notes": "Consistent, Amazon reliability"
    },
    "meta-llama/llama-3.1-8b-instruct": {
        "cost_per_m": 0.025,
        "coding_test": "✅ Working Python code (453 tokens)",
        "business_test": "✅ Structured 6-month plan (465 tokens)",
        "quality_score": 8.2,
        "notes": "Great value for the price"
    },
    "mistralai/mistral-nemo": {
        "cost_per_m": 0.03,
        "coding_test": "✅ Working Python code (451 tokens)",
        "business_test": "✅ Comprehensive 6-month plan (464 tokens)",
        "quality_score": 8.3,
        "notes": "Strong multilingual capabilities"
    },
    "openai/gpt-4o-mini": {
        "cost_per_m": 0.375,
        "coding_test": "✅ Working Python code (451 tokens)",
        "business_test": "✅ Comprehensive 6-month plan (462 tokens)",
        "quality_score": 8.8,
        "notes": "Industry standard, reliable"
    }
}

def calculate_value_scores():
    """Calculate value scores (quality ÷ cost)"""

    for model_id, data in model_analysis.items():
        cost = data["cost_per_m"] + 0.01  # Avoid division by zero
        quality = data["quality_score"]

        # Value score: quality adjusted for cost
        value_score = quality / cost

        model_analysis[model_id]["value_score"] = value_score

def rank_models_by_category():
    """Rank models by different criteria"""

    working_models = {k: v for k, v in model_analysis.items()
                     if v["quality_score"] > 2.0}  # Exclude useless models

    # By value (quality per dollar)
    by_value = sorted(working_models.items(),
                     key=lambda x: x[1]["value_score"], reverse=True)

    # By quality (best overall performance)
    by_quality = sorted(working_models.items(),
                       key=lambda x: x[1]["quality_score"], reverse=True)

    # By cost (cheapest first)
    by_cost = sorted(working_models.items(),
                    key=lambda x: x[1]["cost_per_m"])

    return by_value, by_quality, by_cost

def create_optimal_selection():
    """Create optimal model selection based on systematic analysis"""

    by_value, by_quality, by_cost = rank_models_by_category()

    # Best value model (quality per dollar)
    best_value = by_value[0]

    # Best quality model regardless of cost
    best_quality = by_quality[0]

    # Best free/cheap model for backup
    budget_options = [m for m in by_cost if m[1]["cost_per_m"] <= 0.03]
    best_budget = budget_options[0] if budget_options else by_cost[0]

    # Best coding model (large context + high quality)
    coding_candidates = [m for m in by_quality
                        if "70b" in m[0] or "large" in m[0] or m[1]["quality_score"] >= 8.5]
    best_coding = coding_candidates[0] if coding_candidates else by_quality[0]

    return {
        "DEFAULT": best_value[0],  # Best value for money
        "MAXIMUM": best_quality[0],  # Best overall quality
        "BUDGET": best_budget[0],  # Cheapest usable option
        "CODING": best_coding[0]  # Best for complex tasks
    }

def main():
    """Generate complete model analysis"""

    print("🔍 COMPLETE MODEL ANALYSIS - Based on Real Testing")
    print("=" * 60)

    # Calculate value scores
    calculate_value_scores()

    # Show analysis for each working model
    working_models = {k: v for k, v in model_analysis.items()
                     if v["quality_score"] > 2.0}

    print(f"\n📊 ANALYSIS OF {len(working_models)} WORKING MODELS:\n")

    for model_id, data in sorted(working_models.items(),
                                 key=lambda x: x[1]["value_score"], reverse=True):
        print(f"🎯 {model_id}")
        print(f"   Cost: ${data['cost_per_m']}/M | Quality: {data['quality_score']}/10 | Value: {data['value_score']:.1f}")
        print(f"   Coding: {data['coding_test']}")
        print(f"   Business: {data['business_test']}")
        print(f"   Notes: {data['notes']}")
        print()

    # Rankings
    by_value, by_quality, by_cost = rank_models_by_category()

    print("🏆 RANKINGS:")
    print(f"   Best Value: {by_value[0][0]} ({by_value[0][1]['value_score']:.1f} value score)")
    print(f"   Best Quality: {by_quality[0][0]} ({by_quality[0][1]['quality_score']}/10)")
    print(f"   Cheapest: {by_cost[0][0]} (${by_cost[0][1]['cost_per_m']}/M)")

    # Optimal selection
    optimal = create_optimal_selection()

    print(f"\n🎯 OPTIMAL MODEL SELECTION:")
    for category, model_id in optimal.items():
        model = model_analysis[model_id]
        print(f"   {category}: {model_id}")
        print(f"           Cost: ${model['cost_per_m']}/M | Quality: {model['quality_score']}/10")

    # Save results
    results = {
        "analysis": model_analysis,
        "rankings": {
            "by_value": [(m[0], m[1]["value_score"]) for m in by_value],
            "by_quality": [(m[0], m[1]["quality_score"]) for m in by_quality],
            "by_cost": [(m[0], m[1]["cost_per_m"]) for m in by_cost]
        },
        "optimal_selection": optimal
    }

    with open('/home/ubuntu/dev/oos/complete_model_analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Complete analysis saved to: complete_model_analysis_results.json")

    return results

if __name__ == "__main__":
    main()