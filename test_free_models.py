#!/usr/bin/env python3
"""
SOLO CREATOR MECHA SUIT - Free Model Compatibility Tester

Automated testing script to evaluate all free models from the cost table
for compatibility with our personal AI enhancement system.
"""

import asyncio
import csv
import json
import os
import time

import aiohttp


class FreeModelTester:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenRouter API key required. Set OPENROUTER_API_KEY environment variable.")

        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.test_prompts = self._load_test_prompts()
        self.results = []

    def _load_test_prompts(self) -> list[str]:
        """Load test prompts from the specification file"""
        return [
            # Test 1: Basic Compatibility
            """I'm building a personal productivity system called "SOLO CREATOR MECHA SUIT" that enhances my capabilities through coordinated AI assistance.

Before proceeding with detailed capability tests, I need to verify:

1. Are you willing to assist with personal productivity and project management tasks?
2. Do you have any restrictions on business, productivity, or project coordination use cases?
3. Can you help with task analysis, planning, and strategic thinking frameworks?
4. Are there any topics or tasks you cannot assist with?

Please respond with:
- "YES COMPATIBLE" if you can assist with personal productivity systems
- "RESTRICTED" followed by specific limitations
- "UNABLE TO ASSIST" if this use case is outside your capabilities

If compatible, please provide a brief example of how you might help organize a personal project workflow.""",

            # Test 2: Technical Architecture Understanding
            """Great! Now let's test technical understanding for a system that coordinates multiple AI agents in a personal productivity framework.

CONTEXT: The system uses these agent types:
- Executive Agent: Coordinates overall system and makes decisions
- Operations Agent: Handles task execution and file management
- Knowledge Agent: Manages learning, research, and documentation
- Planning Agent: Creates structured workflows and project plans
- Quality Agent: Reviews work and suggests improvements

SCENARIO: I need to analyze a complex project (building a web application) and create a structured approach.

TASK: Provide a brief analysis showing you understand:
1. How multiple agents might coordinate on this project
2. What information each agent would need
3. How decisions would flow between agents
4. What deliverables each agent would produce

RESPONSE FORMAT: Structured analysis with clear agent responsibilities and coordination patterns.

If you cannot assist with this type of system architecture analysis, please respond "TECHNICAL LIMITATION" and explain why.""",

            # Test 3: Practical Code & Cost Awareness
            """EXCELLENT! Final test - practical application with cost awareness.

SCENARIO: I need to write Python code to validate CSV data format and calculate costs. I have these requirements:
- Must work with CSV files containing ModelName, ModelID, InputCost, OutputCost, ContextTokens
- Must validate cost data and identify models under $1/M token threshold
- Must be cost-efficient to run (this is a test of your efficiency)

TASKS:
1. Write a Python function to validate the CSV structure
2. Write a function to filter models by cost threshold
3. Provide a quality score (1-10) for your solution
4. Estimate how many tokens your response used
5. Explain any limitations in your approach

CONSTRAINTS:
- Focus on practical, efficient code
- Consider real-world usage patterns
- Be honest about capabilities and limitations

If you cannot provide code execution assistance or cost-aware solutions, respond "EXECUTION LIMITATION" and explain.""",

            # Test 4: Privacy & Data Handling
            """IMPORTANT: Privacy and data handling verification.

For the SOLO CREATOR MECHA SUIT system, I need to verify your approach to:

1. Personal data processing (tasks, projects, files)
2. Local file system access requirements
3. Data retention and privacy policies
4. Any restrictions on processing personal or business information

TASK: Please confirm:
- Can you process personal project data?
- Do you have any data retention policies?
- Are there business/privacy topics you cannot discuss?
- Will you store any of my personal information?

RESPONSE: Clear acknowledgment of your privacy capabilities and any restrictions.

If you have significant restrictions on personal/business data processing, respond "PRIVACY RESTRICTED" with details."""
        ]

    def load_free_models(self) -> list[dict]:
        """Load all free models from the cost table CSV"""
        free_models = []

        try:
            with open('/home/ubuntu/dev/oos/model_costs.csv') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    input_cost = float(row['InputCost'])
                    output_cost = float(row['OutputCost'])

                    if input_cost == 0 and output_cost == 0:
                        free_models.append({
                            'ModelID': row['ModelID'],
                            'ModelName': row['ModelName'],
                            'InputCost': input_cost,
                            'OutputCost': output_cost,
                            'ContextTokens': int(row['ContextTokens'])
                        })
        except FileNotFoundError:
            print("Error: model_costs.csv not found. Run model selection pipeline first.")
            return []

        print(f"Found {len(free_models)} free models to test")
        return free_models

    async def call_model(self, model_id: str, prompt: str, timeout: int = 30) -> dict:
        """Make API call to test a model"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/Khamel83/oos",
            "X-Title": "SOLO CREATOR MECHA SUIT Compatibility Test"
        }

        data = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,
            "temperature": 0.1
        }

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.post(self.base_url, headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "response": result["choices"][0]["message"]["content"],
                            "usage": result.get("usage", {})
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "response": None
                        }

        except TimeoutError:
            return {
                "success": False,
                "error": "Request timeout",
                "response": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": None
            }

    def evaluate_response(self, test_num: int, response: str, model_name: str) -> dict:
        """Evaluate individual test responses"""
        if not response:
            return {
                "status": "ERROR",
                "response": response,
                "reason": "No response received"
            }

        response_lower = response.lower()

        # Test 1: Basic Compatibility
        if test_num == 1:
            if 'yes compatible' in response_lower:
                return {"status": "PASS", "response": response[:200] + "..."}
            elif 'unable to assist' in response_lower or 'cannot assist' in response_lower:
                return {"status": "FAIL", "response": response[:200] + "...", "reason": "Refuses productivity assistance"}
            elif 'restricted' in response_lower:
                return {"status": "FAIL", "response": response[:200] + "...", "reason": "Has policy restrictions"}

        # Test 2: Technical Architecture
        elif test_num == 2:
            if 'technical limitation' in response_lower or 'cannot discuss' in response_lower:
                return {"status": "FAIL", "response": response[:200] + "...", "reason": "Cannot discuss system architecture"}
            elif 'agent' in response_lower and ('coordinate' in response_lower or 'workflow' in response_lower):
                return {"status": "PASS", "response": response[:200] + "..."}

        # Test 3: Code Generation
        elif test_num == 3:
            if 'execution limitation' in response_lower or 'cannot provide code' in response_lower:
                return {"status": "FAIL", "response": response[:200] + "...", "reason": "Cannot provide code solutions"}
            elif 'def ' in response or 'python' in response_lower or 'function' in response_lower:
                return {"status": "PASS", "response": response[:200] + "..."}

        # Test 4: Privacy & Data
        elif test_num == 4:
            if 'privacy restricted' in response_lower or 'cannot process' in response_lower:
                return {"status": "FAIL", "response": response[:200] + "...", "reason": "Privacy policy restrictions"}
            elif 'can process' in response_lower or 'no restrictions' in response_lower:
                return {"status": "PASS", "response": response[:200] + "..."}

        # Default: Unclear response
        return {
            "status": "PARTIAL",
            "response": response[:200] + "...",
            "reason": "Unclear response pattern"
        }

    async def test_model(self, model_info: dict) -> dict:
        """Test a single model against all compatibility criteria"""
        model_id = model_info['ModelID']
        model_name = model_info['ModelName']

        print(f"Testing {model_name}...")

        result = {
            "model_id": model_id,
            "model_name": model_name,
            "tests": {},
            "overall_status": "UNKNOWN",
            "restrictions": [],
            "capabilities": [],
            "errors": []
        }

        # Run each test
        for i, prompt in enumerate(self.test_prompts, 1):
            test_key = f"test_{i}"

            try:
                api_result = await self.call_model(model_id, prompt)

                if api_result["success"]:
                    test_result = self.evaluate_response(i, api_result["response"], model_name)
                    result["tests"][test_key] = test_result

                    # Early termination on critical failure
                    if test_result["status"] == "FAIL":
                        result["restrictions"].append(test_result["reason"])
                        print(f"  ❌ Test {i} failed: {test_result['reason']}")
                        break
                    else:
                        print(f"  ✅ Test {i} passed")

                else:
                    result["tests"][test_key] = {
                        "status": "ERROR",
                        "response": None,
                        "reason": api_result["error"]
                    }
                    result["errors"].append(api_result["error"])
                    print(f"  ⚠️  Test {i} error: {api_result['error']}")
                    break

            except Exception as e:
                result["tests"][test_key] = {
                    "status": "ERROR",
                    "response": None,
                    "reason": str(e)
                }
                result["errors"].append(str(e))
                print(f"  💥 Test {i} exception: {e}")
                break

        # Determine overall status
        result["overall_status"] = self._determine_overall_status(result)

        return result

    def _determine_overall_status(self, result: dict) -> str:
        """Determine overall model compatibility status"""
        test_results = result["tests"]

        # Any error or FAIL on critical tests = incompatible
        for _test_key, test_result in test_results.items():
            if test_result.get("status") in ["FAIL", "ERROR"]:
                return "INCOMPATIBLE"

        # All PASS = compatible
        if all(tr.get("status") == "PASS" for tr in test_results.values()):
            return "COMPATIBLE"

        # Mixed results = limited
        return "LIMITED"

    async def test_all_free_models(self) -> dict:
        """Test all free models from the cost table"""
        print("=== SOLO CREATOR MECHA SUIT - Free Model Compatibility Testing ===\n")

        free_models = self.load_free_models()
        if not free_models:
            return {"error": "No free models found to test"}

        print(f"Starting compatibility tests for {len(free_models)} free models...\n")

        # Test models with concurrency limit to avoid overwhelming the API
        semaphore = asyncio.Semaphore(3)  # Max 3 concurrent requests

        async def test_with_semaphore(model_info):
            async with semaphore:
                await asyncio.sleep(0.5)  # Rate limiting
                return await self.test_model(model_info)

        # Run all tests
        start_time = time.time()
        tasks = [test_with_semaphore(model) for model in free_models]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        # Process results
        successful_results = [r for r in results if isinstance(r, dict)]
        failed_results = [r for r in results if not isinstance(r, dict)]

        # Generate summary
        summary = self._generate_summary(successful_results)

        final_results = {
            "timestamp": time.time(),
            "testing_duration": end_time - start_time,
            "total_models_tested": len(free_models),
            "successful_tests": len(successful_results),
            "failed_tests": len(failed_results),
            "results": successful_results,
            "summary": summary,
            "test_metadata": {
                "prompts_used": len(self.test_prompts),
                "api_base_url": self.base_url,
                "rate_limiting": "3 concurrent requests, 0.5s delay"
            }
        }

        return final_results

    def _generate_summary(self, results: list[dict]) -> dict:
        """Generate summary statistics from test results"""
        summary = {
            "compatible": 0,
            "limited": 0,
            "incompatible": 0,
            "common_restrictions": {},
            "recommended_models": []
        }

        # Count statuses
        for result in results:
            status = result.get("overall_status", "UNKNOWN")
            summary[status] = summary.get(status, 0) + 1

            # Track common restrictions
            for restriction in result.get("restrictions", []):
                summary["common_restrictions"][restriction] = summary["common_restrictions"].get(restriction, 0) + 1

        # Identify top recommended models
        compatible_models = [r for r in results if r.get("overall_status") == "COMPATIBLE"]
        summary["recommended_models"] = [
            {
                "model_id": m["model_id"],
                "model_name": m["model_name"]
            }
            for m in compatible_models[:5]
        ]

        return summary

    def save_results(self, results: dict, output_path: str):
        """Save test results to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nTest results saved to: {output_path}")

    def print_summary(self, results: dict):
        """Print summary of test results"""
        summary = results["summary"]

        print("\n=== COMPATIBILITY TEST SUMMARY ===")
        print(f"Models tested: {results['total_models_tested']}")
        print(f"Testing duration: {results['testing_duration']:.1f} seconds")
        print(f"Successful tests: {results['successful_tests']}")
        print(f"Failed tests: {results['failed_tests']}")

        print("\n=== COMPATIBILITY BREAKDOWN ===")
        print(f"✅ Fully Compatible: {summary['compatible']}")
        print(f"⚠️  Limited: {summary['limited']}")
        print(f"❌ Incompatible: {summary['incompatible']}")

        if summary["common_restrictions"]:
            print("\n=== COMMON RESTRICTIONS ===")
            for restriction, count in sorted(summary["common_restrictions"].items(), key=lambda x: x[1], reverse=True):
                print(f"• {restriction}: {count} models")

        if summary["recommended_models"]:
            print("\n=== TOP RECOMMENDED MODELS ===")
            for model in summary["recommended_models"]:
                print(f"• {model['model_name']}")

async def main():
    """Run the complete compatibility testing pipeline"""
    tester = FreeModelTester()

    # Test all free models
    results = await tester.test_all_free_models()

    # Save results
    tester.save_results(results, '/home/ubuntu/dev/oos/free_model_compatibility_results.json')

    # Print summary
    tester.print_summary(results)

    return results

if __name__ == "__main__":
    asyncio.run(main())
