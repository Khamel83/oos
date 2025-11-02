#!/usr/bin/env python3
"""
SOLO CREATOR MECHA SUIT - Implementation Ready System
Based on systematic testing of 7 working models
"""

import os
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv('/home/ubuntu/dev/oos/.env')

# PROVEN WORKING MODELS from systematic testing
MODELS = {
    "DEFAULT": {
        "model_id": "google/gemma-2-9b-it",
        "cost_per_m": 0.02,
        "quality_score": 8.5,
        "value_score": 283.3,
        "best_for": ["general", "draft", "planning", "research"]
    },
    "MAXIMUM": {
        "model_id": "meta-llama/llama-3.1-70b-instruct",
        "cost_per_m": 0.40,
        "quality_score": 9.2,
        "value_score": 22.4,
        "best_for": ["critical", "complex", "coding", "analysis"]
    },
    "BUDGET": {
        "model_id": "google/gemma-2-9b-it",  # Same as DEFAULT - it's already cheapest good option
        "cost_per_m": 0.02,
        "quality_score": 8.5,
        "value_score": 283.3,
        "best_for": ["simple", "testing", "backup"]
    },
    "CODING": {
        "model_id": "meta-llama/llama-3.1-70b-instruct",  # Same as MAXIMUM - best for complex tasks
        "cost_per_m": 0.40,
        "quality_score": 9.2,
        "value_score": 22.4,
        "best_for": ["programming", "debugging", "architecture"]
    }
}

@dataclass
class TaskResult:
    """Result of an AI task execution"""
    agent: str
    model_used: str
    task_type: str
    response: str
    tokens_used: int
    cost: float
    quality_score: int
    execution_time: float
    timestamp: datetime

class SoloCreatorMechaSuit:
    """SOLO CREATOR MECHA SUIT - AI Assistant System"""

    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_PROJECT_KEY')
        self.session_id = f"scms_{int(time.time())}"
        self.task_history: List[TaskResult] = []
        self.total_cost = 0.0

    def call_model(self, model_id: str, prompt: str, task_type: str) -> Dict:
        """Make API call to OpenRouter model"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/Khamel83/oos",
            "X-Title": f"SOLO CREATOR MECHA SUIT - {task_type}"
        }

        data = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,
            "temperature": 0.1 if "coding" in task_type else 0.3
        }

        try:
            start_time = time.time()
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            execution_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "SUCCESS",
                    "response": result["choices"][0]["message"]["content"],
                    "usage": result.get("usage", {}),
                    "execution_time": execution_time
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

    def select_optimal_model(self, task_type: str, importance: str = "normal") -> str:
        """Intelligently select model based on task requirements"""

        # Use DEFAULT for most tasks
        if importance == "normal":
            return MODELS["DEFAULT"]["model_id"]

        # Use MAXIMUM for critical tasks
        elif importance == "critical":
            return MODELS["MAXIMUM"]["model_id"]

        # Use CODING for programming tasks
        elif task_type in ["coding", "programming", "debugging"]:
            return MODELS["CODING"]["model_id"]

        # Use BUDGET for simple/testing tasks
        elif importance == "low" or task_type in ["simple", "test"]:
            return MODELS["BUDGET"]["model_id"]

        # Default fallback
        return MODELS["DEFAULT"]["model_id"]

    def calculate_cost(self, tokens_used: int, model_id: str) -> float:
        """Calculate cost for token usage"""

        # Find model cost
        cost_per_m = None
        for model_info in MODELS.values():
            if model_info["model_id"] == model_id:
                cost_per_m = model_info["cost_per_m"]
                break

        if cost_per_m is None:
            cost_per_m = 0.02  # Default assumption

        return (tokens_used / 1000000) * cost_per_m

    def score_response_quality(self, response: str, task_type: str) -> int:
        """Score response quality from 1-10"""

        if not response or len(response) < 50:
            return 1

        score = 5  # Base score

        # Length and substance
        if len(response) > 200:
            score += 1
        if len(response) > 500:
            score += 1

        # Task-specific quality indicators
        if task_type in ["coding", "programming"]:
            if "def " in response and "import" in response:
                score += 2
            if "```python" in response or "```" in response:
                score += 1

        elif task_type in ["planning", "business", "strategy"]:
            if any(word in response.lower() for word in ["step", "timeline", "budget", "strategy"]):
                score += 2
            if any(word in response.lower() for word in ["month", "week", "quarter"]):
                score += 1

        elif task_type in ["analysis", "research"]:
            if any(word in response.lower() for word in ["analysis", "research", "data", "conclusion"]):
                score += 2

        # Cap at 10
        return min(score, 10)

    def execute_agent_task(self, agent: str, task: str, task_type: str, importance: str = "normal") -> TaskResult:
        """Execute task using specific agent with optimal model selection"""

        # Select model based on task
        model_id = self.select_optimal_model(task_type, importance)

        # Add agent-specific context
        agent_context = self.get_agent_context(agent, task)
        full_prompt = f"{agent_context}\n\nTASK: {task}"

        # Execute the task
        result = self.call_model(model_id, full_prompt, task_type)

        if result["status"] == "SUCCESS":
            tokens_used = result["usage"].get("total_tokens", 0)
            cost = self.calculate_cost(tokens_used, model_id)
            quality_score = self.score_response_quality(result["response"], task_type)

            task_result = TaskResult(
                agent=agent,
                model_used=model_id,
                task_type=task_type,
                response=result["response"],
                tokens_used=tokens_used,
                cost=cost,
                quality_score=quality_score,
                execution_time=result["execution_time"],
                timestamp=datetime.now()
            )

            self.task_history.append(task_result)
            self.total_cost += cost

            return task_result
        else:
            # Return failed task result
            return TaskResult(
                agent=agent,
                model_used=model_id,
                task_type=task_type,
                response=f"ERROR: {result['error']}",
                tokens_used=0,
                cost=0.0,
                quality_score=1,
                execution_time=0.0,
                timestamp=datetime.now()
            )

    def get_agent_context(self, agent: str, task: str) -> str:
        """Get agent-specific context and instructions"""

        contexts = {
            "Executive": """You are the Executive Agent of the SOLO CREATOR MECHA SUIT.
Your role: Strategic planning, decision making, and coordinating other agents.
Focus on: High-level strategy, business decisions, project oversight.
Provide: Clear direction, prioritized action items, strategic frameworks.""",

            "Operations": """You are the Operations Agent of the SOLO CREATOR MECHA SUIT.
Your role: Task execution, file management, workflow implementation.
Focus on: Practical execution, step-by-step processes, efficient workflows.
Provide: Actionable steps, clear instructions, implementation guidance.""",

            "Knowledge": """You are the Knowledge Agent of the SOLO CREATOR MECHA SUIT.
Your role: Research, information gathering, knowledge synthesis.
Focus on: Finding relevant information, organizing data, providing insights.
Provide: Well-researched information, organized summaries, key insights.""",

            "Planning": """You are the Planning Agent of the SOLO CREATOR MECHA SUIT.
Your role: Creating structured plans, timelines, and roadmaps.
Focus on: Project planning, timeline creation, milestone setting.
Provide: Detailed plans, realistic timelines, clear milestones.""",

            "Quality": """You are the Quality Agent of the SOLO CREATOR MECHA SUIT.
Your role: Review, validation, quality assurance, and improvement suggestions.
Focus on: Quality assessment, gap identification, improvement recommendations.
Provide: Constructive feedback, quality scores, improvement suggestions."""
        }

        return contexts.get(agent, "You are a helpful AI assistant.")

    def coordinate_agents(self, main_task: str, task_type: str, importance: str = "normal") -> Dict:
        """Coordinate multiple agents for complex tasks"""

        print(f"🎯 Coordinating agents for: {main_task}")
        print("=" * 50)

        # Step 1: Executive Agent plans the approach
        print("\n🧠 Executive Agent: Planning approach...")
        executive_prompt = f"Analyze this task and create a coordination strategy: {main_task}"
        executive_result = self.execute_agent_task("Executive", executive_prompt, "planning", importance)

        if executive_result.quality_score < 7:
            print(f"⚠️  Executive planning quality: {executive_result.quality_score}/10")

        # Step 2: Operations Agent executes main task
        print("\n⚙️  Operations Agent: Executing task...")
        operations_result = self.execute_agent_task("Operations", main_task, task_type, importance)

        # Step 3: Quality Agent reviews and validates
        print("\n🔍 Quality Agent: Reviewing results...")
        quality_prompt = f"Review this task execution and provide quality assessment: {operations_result.response}"
        quality_result = self.execute_agent_task("Quality", quality_prompt, "review", importance)

        # Compile results
        coordination_result = {
            "main_task": main_task,
            "task_type": task_type,
            "importance": importance,
            "executive_plan": executive_result.response,
            "operations_result": operations_result.response,
            "quality_review": quality_result.response,
            "cost_breakdown": {
                "executive": executive_result.cost,
                "operations": operations_result.cost,
                "quality": quality_result.cost,
                "total": executive_result.cost + operations_result.cost + quality_result.cost
            },
            "quality_scores": {
                "executive": executive_result.quality_score,
                "operations": operations_result.quality_score,
                "quality": quality_result.quality_score
            },
            "total_tokens": executive_result.tokens_used + operations_result.tokens_used + quality_result.tokens_used
        }

        print(f"\n✅ Task coordination complete")
        print(f"💰 Total cost: ${coordination_result['cost_breakdown']['total']:.4f}")
        print(f"📊 Average quality: {sum(coordination_result['quality_scores'].values())/3:.1f}/10")

        return coordination_result

    def get_usage_summary(self) -> Dict:
        """Get summary of usage and costs"""

        if not self.task_history:
            return {"message": "No tasks executed yet"}

        # Calculate statistics
        total_tasks = len(self.task_history)
        total_cost = sum(task.cost for task in self.task_history)
        total_tokens = sum(task.tokens_used for task in self.task_history)
        avg_quality = sum(task.quality_score for task in self.task_history) / total_tasks

        # Cost by model
        model_costs = {}
        for task in self.task_history:
            if task.model_used not in model_costs:
                model_costs[task.model_used] = {"cost": 0, "tasks": 0}
            model_costs[task.model_used]["cost"] += task.cost
            model_costs[task.model_used]["tasks"] += 1

        return {
            "session_id": self.session_id,
            "total_tasks": total_tasks,
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "average_quality": avg_quality,
            "model_breakdown": model_costs,
            "recent_tasks": [
                {
                    "agent": task.agent,
                    "task_type": task.task_type,
                    "cost": task.cost,
                    "quality": task.quality_score,
                    "timestamp": task.timestamp.isoformat()
                }
                for task in self.task_history[-5:]
            ]
        }

def main():
    """Demo the SOLO CREATOR MECHA SUIT system"""

    print("🚀 SOLO CREATOR MECHA SUIT - Implementation Ready")
    print("=" * 60)
    print("Based on systematic testing of 7 working AI models")
    print("Cost-optimized with intelligent model selection")
    print()

    # Initialize the system
    scms = SoloCreatorMechaSuit()

    # Example task coordination
    result = scms.coordinate_agents(
        main_task="Create a project plan for developing a todo list application",
        task_type="planning",
        importance="normal"
    )

    print("\n" + "=" * 60)
    print("📊 USAGE SUMMARY")
    print("=" * 60)

    summary = scms.get_usage_summary()
    print(json.dumps(summary, indent=2))

    return scms

if __name__ == "__main__":
    main()