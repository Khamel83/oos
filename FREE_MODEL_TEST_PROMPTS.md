# SOLO CREATOR MECHA SUIT - Free Model Compatibility Test Suite

## Purpose
This test suite evaluates free AI models for compatibility with the SOLO CREATOR MECHA SUIT system, specifically identifying privacy policy restrictions, capability limitations, and willingness to engage with our use case.

## Test Prompts

### Test 1: System Role & Compatibility Assessment
```
I'm building a personal productivity system called "SOLO CREATOR MECHA SUIT" that enhances my capabilities through coordinated AI assistance.

Before proceeding with detailed capability tests, I need to verify:

1. Are you willing to assist with personal productivity and project management tasks?
2. Do you have any restrictions on business, productivity, or project coordination use cases?
3. Can you help with task analysis, planning, and strategic thinking frameworks?
4. Are there any topics or tasks you cannot assist with?

Please respond with:
- "YES COMPATIBLE" if you can assist with personal productivity systems
- "RESTRICTED" followed by specific limitations
- "UNABLE TO ASSIST" if this use case is outside your capabilities

If compatible, please provide a brief example of how you might help organize a personal project workflow.
```

### Test 2: Technical Understanding & Architecture
```
Great! Now let's test technical understanding for a system that coordinates multiple AI agents in a personal productivity framework.

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

If you cannot assist with this type of system architecture analysis, please respond "TECHNICAL LIMITATION" and explain why.
```

### Test 3: Cost-Aware Execution & Quality Scoring
```
EXCELLENT! Final test - practical application with cost awareness.

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

If you cannot provide code execution assistance or cost-aware solutions, respond "EXECUTION LIMITATION" and explain.
```

### Test 4: Privacy & Data Handling Acknowledgment
```
IMPORTANT: Privacy and data handling verification.

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

If you have significant restrictions on personal/business data processing, respond "PRIVACY RESTRICTED" with details.
```

## Evaluation Criteria

### PASS Conditions (Model is Compatible):
- Responds "YES COMPATIBLE" to Test 1
- Provides coherent agent coordination analysis in Test 2
- Delivers working code solution in Test 3
- Acknowledges privacy capabilities in Test 4
- No policy restrictions on personal/business productivity use

### FAIL Conditions (Model is Incompatible):
- Responds "UNABLE TO ASSIST" or "RESTRICTED" to Test 1
- Refuses to discuss system architecture or agent coordination
- Cannot provide code examples or technical solutions
- Has significant privacy policy restrictions
- States inability to assist with business/productivity contexts

### PARTIAL Conditions (Model is Limited):
- Passes some tests but has limitations in others
- Provides partial solutions with clear capability boundaries
- Has specific topic restrictions that don't prevent core functionality

## Implementation Script

```python
import asyncio
import openai
import json
import time
from typing import Dict, List, Tuple

class FreeModelTester:
    def __init__(self):
        self.test_prompts = [
            self.get_test1_prompt(),
            self.get_test2_prompt(),
            self.get_test3_prompt(),
            self.get_test4_prompt()
        ]
        self.results = {}

    async def test_model(self, model_id: str, model_name: str) -> Dict:
        """Test a single model against all compatibility criteria"""
        results = {
            'model_id': model_id,
            'model_name': model_name,
            'tests': {},
            'overall_status': 'UNKNOWN',
            'restrictions': [],
            'capabilities': []
        }

        for i, prompt in enumerate(self.test_prompts, 1):
            try:
                response = await self.call_model(model_id, prompt)
                test_result = self.evaluate_response(i, response)
                results['tests'][f'test_{i}'] = test_result

                if test_result['status'] == 'FAIL':
                    results['restrictions'].append(test_result['reason'])
                    break  # Early termination on critical failure

            except Exception as e:
                results['tests'][f'test_{i}'] = {
                    'status': 'ERROR',
                    'response': str(e),
                    'reason': f'API Error: {e}'
                }
                break

        # Determine overall status
        results['overall_status'] = self.determine_overall_status(results)

        return results

    def evaluate_response(self, test_num: int, response: str) -> Dict:
        """Evaluate individual test responses"""
        response_lower = response.lower()

        if test_num == 1:
            if 'yes compatible' in response_lower:
                return {'status': 'PASS', 'response': response}
            elif 'unable to assist' in response_lower or 'restricted' in response_lower:
                return {'status': 'FAIL', 'response': response, 'reason': 'Policy restriction on productivity use case'}

        elif test_num == 2:
            if 'technical limitation' in response_lower:
                return {'status': 'FAIL', 'response': response, 'reason': 'Cannot discuss system architecture'}
            elif 'agent' in response_lower and 'coordinate' in response_lower:
                return {'status': 'PASS', 'response': response}

        elif test_num == 3:
            if 'execution limitation' in response_lower:
                return {'status': 'FAIL', 'response': response, 'reason': 'Cannot provide code solutions'}
            elif 'def ' in response or 'python' in response_lower:
                return {'status': 'PASS', 'response': response}

        elif test_num == 4:
            if 'privacy restricted' in response_lower:
                return {'status': 'FAIL', 'response': response, 'reason': 'Privacy policy restrictions on personal data'}
            elif 'can process' in response_lower or 'no restrictions' in response_lower:
                return {'status': 'PASS', 'response': response}

        return {'status': 'PARTIAL', 'response': response, 'reason': 'Unclear response pattern'}

    def determine_overall_status(self, results: Dict) -> str:
        """Determine overall model compatibility status"""
        test_results = results['tests']

        # Any FAIL on critical tests = incompatible
        for test_key, test_result in test_results.items():
            if test_result.get('status') == 'FAIL':
                return 'INCOMPATIBLE'

        # All PASS = compatible
        if all(tr.get('status') == 'PASS' for tr in test_results.values()):
            return 'COMPATIBLE'

        # Mixed results = limited
        return 'LIMITED'

    async def test_all_free_models(self) -> Dict:
        """Test all free models from the cost table"""
        free_models = self.load_free_models()

        tasks = []
        for model in free_models:
            task = asyncio.create_task(self.test_model(model['ModelID'], model['ModelName']))
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            'timestamp': time.time(),
            'total_models_tested': len(free_models),
            'results': results,
            'summary': self.generate_summary(results)
        }

    def load_free_models(self) -> List[Dict]:
        """Load free models from CSV"""
        import csv
        free_models = []

        with open('/home/ubuntu/dev/oos/model_costs.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if float(row['InputCost']) == 0 and float(row['OutputCost']) == 0:
                    free_models.append(row)

        return free_models

# Usage
tester = FreeModelTester()
results = await tester.test_all_free_models()

# Save results
with open('/home/ubuntu/dev/oos/free_model_compatibility_results.json', 'w') as f:
    json.dump(results, f, indent=2)
```

## Expected Output Format

```json
{
  "timestamp": 1698765432.1,
  "total_models_tested": 15,
  "results": [
    {
      "model_id": "meta-llama/llama-3.1-8b-instruct:free",
      "model_name": "Meta Llama 3.1 8B Instruct free",
      "overall_status": "COMPATIBLE",
      "capabilities": ["Productivity assistance", "System architecture", "Code generation", "Privacy compliance"],
      "restrictions": [],
      "tests": {
        "test_1": {"status": "PASS", "response": "YES COMPATIBLE..."},
        "test_2": {"status": "PASS", "response": "Here's how agents would coordinate..."},
        "test_3": {"status": "PASS", "response": "def validate_csv(..."},
        "test_4": {"status": "PASS", "response": "I can process personal project data..."}
      }
    }
  ],
  "summary": {
    "compatible": 8,
    "limited": 4,
    "incompatible": 3,
    "errors": 0
  }
}
```

## Next Steps

1. Run the compatibility test suite on all free models
2. Create approved models list for SOLO CREATOR MECHA SUIT
3. Document specific limitations for partial-compatibility models
4. Implement model selection logic based on task requirements
5. Create fallback chains for when primary models fail