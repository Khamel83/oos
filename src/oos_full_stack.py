#!/usr/bin/env python3
"""
OOS Full Stack Demonstration
Shows AI SDK + OpenRouter, RelayQ Architecture, and Archon Sync working together
"""

import argparse
import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ai_provider import ask_ai, get_ai_manager
from archon_sync import get_sync_manager
from relayq_architecture import DeploymentTask, get_relayq_manager


class OOSFullStackDemo:
    """Demonstrates the complete OOS integrated stack"""

    def __init__(self):
        self.ai_manager = None
        self.relayq_manager = None
        self.sync_manager = None

    async def initialize(self):
        """Initialize all components"""
        print("🚀 Initializing OOS Full Stack...")

        # Initialize AI Manager
        print("   • AI Provider (OpenRouter)")
        self.ai_manager = get_ai_manager()

        # Initialize RelayQ Manager
        print("   • RelayQ Architecture")
        self.relayq_manager = get_relayq_manager()

        # Initialize Sync Manager
        print("   • Archon Synchronization")
        self.sync_manager = get_sync_manager()

        print("✅ Full stack initialized!\n")

    async def cleanup(self):
        """Cleanup resources"""
        if self.ai_manager:
            await self.ai_manager.close_all()

    async def demonstrate_ai_assistance(self, problem: str) -> dict[str, Any]:
        """Demonstrate AI-powered problem solving"""
        print("🤖 AI-Powered Analysis")
        print("=" * 50)

        start_time = time.time()

        try:
            # Generate solution with AI
            print(f"Problem: {problem}")
            print("🔍 Analyzing with AI...")

            ai_response = await ask_ai(
                f"""Analyze this problem and provide a structured solution:

Problem: {problem}

Please provide:
1. Brief analysis
2. Recommended approach
3. Key steps to implement
4. Potential challenges

Keep it concise and actionable.""",
                system_prompt="You are an expert technical assistant providing practical solutions."
            )

            duration = time.time() - start_time

            print(f"✅ AI Analysis completed in {duration:.2f}s")
            print(f"Response: {ai_response[:200]}{'...' if len(ai_response) > 200 else ''}")
            print()

            return {
                "success": True,
                "response": ai_response,
                "duration": duration,
                "tokens_used": getattr(ai_response, 'tokens_used', None)
            }

        except Exception as e:
            print(f"❌ AI analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time
            }

    async def demonstrate_distributed_execution(self, command: str, distributed: bool = False) -> dict[str, Any]:
        """Demonstrate distributed task execution"""
        print("🏗️ Distributed Task Execution")
        print("=" * 50)

        start_time = time.time()

        try:
            # Show topology
            topology = self.relayq_manager.get_topology_summary()
            print(f"Available nodes: {topology['online_nodes']}/{topology['total_nodes']} online")

            for node_type, info in topology["nodes_by_type"].items():
                print(f"   {node_type}: {info['online']}/{info['count']} online")

            print()

            # Create deployment task
            task = DeploymentTask(
                task_id=f"demo-{int(time.time())}",
                command=command,
                target_nodes=["ocivm-dev"],  # Use local node for demo
                distributed=distributed,
                requirements=["development"]
            )

            print(f"Executing: {command}")
            print("🚀 Deploying task...")

            # Execute task
            result = await self.relayq_manager.deploy_task(task)
            duration = time.time() - start_time

            if result["success"]:
                print("✅ Task executed successfully")
                for node, node_result in result["results"].items():
                    if node_result["success"]:
                        print(f"   {node}: {node_result['stdout']}")
                    else:
                        print(f"   {node}: ❌ {node_result.get('stderr', 'Unknown error')}")
            else:
                print(f"❌ Task execution failed: {result.get('error', 'Unknown error')}")

            print()

            return {
                "success": result["success"],
                "duration": duration,
                "results": result.get("results", {}),
                "error": result.get("error")
            }

        except Exception as e:
            print(f"❌ Distributed execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time
            }

    async def demonstrate_archon_sync(self, tasks: list, system_state: dict[str, Any]) -> dict[str, Any]:
        """Demonstrate Archon synchronization"""
        print("🔄 Archon Synchronization")
        print("=" * 50)

        start_time = time.time()

        try:
            # Show sync status
            sync_status = self.sync_manager.get_sync_status()
            print(f"Sync enabled: {sync_status['enabled']}")
            print(f"Project ID: {sync_status['project_id']}")
            print(f"Archon URL: {sync_status['archon_url']}")
            print()

            if not sync_status['enabled']:
                print("⚠️  Sync is disabled - no project configured")
                return {"success": False, "error": "Sync disabled"}

            print(f"Syncing {len(tasks)} tasks and system state...")
            print("📤 Uploading to Archon...")

            # Perform full sync
            oos_state = {
                "tasks": tasks,
                "system_state": system_state
            }

            sync_result = await self.sync_manager.full_sync(oos_state)
            duration = time.time() - start_time

            if sync_result["success"]:
                print("✅ Synchronization successful")
                print(f"   Tasks synced: {sync_result['synced_tasks']}")
                print(f"   State synced: {'Yes' if sync_result['synced_state'] else 'No'}")
                print(f"   Heartbeat: {'Yes' if sync_result['heartbeat_sent'] else 'No'}")
                print(f"   Duration: {sync_result['duration']:.2f}s")
            else:
                print(f"❌ Synchronization issues: {sync_result.get('errors', [])}")

            print()

            return {
                "success": sync_result["success"],
                "duration": duration,
                "synced_tasks": sync_result.get("synced_tasks", 0),
                "errors": sync_result.get("errors", [])
            }

        except Exception as e:
            print(f"❌ Archon sync failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time
            }

    async def run_full_demo(self, problem: str, command: str = None, distributed: bool = False):
        """Run complete full-stack demonstration"""
        print("🎯 OOS Full Stack Demonstration")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Problem: {problem}")
        if command:
            print(f"Command: {command}")
        print()

        results = {
            "ai_analysis": None,
            "distributed_execution": None,
            "archon_sync": None,
            "total_duration": 0
        }

        start_time = time.time()

        try:
            # 1. AI Analysis
            results["ai_analysis"] = await self.demonstrate_ai_assistance(problem)

            # 2. Distributed Execution (if command provided)
            if command:
                results["distributed_execution"] = await self.demonstrate_distributed_execution(command, distributed)

            # 3. Archon Sync
            # Create demo tasks based on analysis
            demo_tasks = []
            if results["ai_analysis"]["success"]:
                demo_tasks.append({
                    "id": f"ai-task-{int(time.time())}",
                    "title": f"AI Analysis: {problem[:50]}...",
                    "description": results["ai_analysis"]["response"][:500],
                    "status": "todo",
                    "priority": "medium",
                    "tags": ["ai-generated", "demo"]
                })

            if results["distributed_execution"] and results["distributed_execution"]["success"]:
                demo_tasks.append({
                    "id": f"execution-task-{int(time.time())}",
                    "title": f"Executed: {command[:50]}...",
                    "description": f"Command executed on {len(results['distributed_execution']['results'])} node(s)",
                    "status": "completed",
                    "priority": "low",
                    "tags": ["execution", "demo"]
                })

            # System state for sync
            system_state = {
                "version": "2.0-full-stack-demo",
                "node_count": self.relayq_manager.get_topology_summary()["total_nodes"],
                "tasks_active": len([t for t in demo_tasks if t["status"] == "todo"]),
                "tasks_completed": len([t for t in demo_tasks if t["status"] == "completed"]),
                "ai_requests_today": 1,
                "last_activity": datetime.now().isoformat(),
                "system_health": {
                    "ai_provider": "online" if results["ai_analysis"]["success"] else "offline",
                    "relayq_nodes": self.relayq_manager.get_topology_summary()["online_nodes"],
                    "archon_sync": "online" if self.sync_manager.get_sync_status()["enabled"] else "offline"
                }
            }

            results["archon_sync"] = await self.demonstrate_archon_sync(demo_tasks, system_state)

            # Summary
            results["total_duration"] = time.time() - start_time

            self.print_summary(results)

        except Exception as e:
            print(f"❌ Demo failed: {e}")
            results["error"] = str(e)

        return results

    def print_summary(self, results: dict[str, Any]):
        """Print demonstration summary"""
        print("📊 Demonstration Summary")
        print("=" * 50)

        print(f"Total Duration: {results['total_duration']:.2f}s")
        print()

        # AI Analysis
        ai_result = results.get("ai_analysis", {})
        ai_status = "✅" if ai_result.get("success") else "❌"
        print(f"AI Analysis: {ai_status}")
        if ai_result.get("success"):
            print(f"   Duration: {ai_result.get('duration', 0):.2f}s")
            print(f"   Tokens: {ai_result.get('tokens_used', 'N/A')}")
        elif ai_result.get("error"):
            print(f"   Error: {ai_result['error']}")
        print()

        # Distributed Execution
        exec_result = results.get("distributed_execution")
        if exec_result:
            exec_status = "✅" if exec_result.get("success") else "❌"
            print(f"Distributed Execution: {exec_status}")
            if exec_result.get("success"):
                print(f"   Duration: {exec_result.get('duration', 0):.2f}s")
                print(f"   Nodes: {len(exec_result.get('results', {}))}")
            elif exec_result.get("error"):
                print(f"   Error: {exec_result['error']}")
            print()

        # Archon Sync
        sync_result = results.get("archon_sync", {})
        sync_status = "✅" if sync_result.get("success") else "❌"
        print(f"Archon Sync: {sync_status}")
        if sync_result.get("success"):
            print(f"   Duration: {sync_result.get('duration', 0):.2f}s")
            print(f"   Tasks synced: {sync_result.get('synced_tasks', 0)}")
        elif sync_result.get("error"):
            print(f"   Error: {sync_result['error']}")
        print()

        # Overall
        success_count = sum(1 for r in [ai_result, exec_result, sync_result]
                           if r and r.get("success"))
        total_count = sum(1 for r in [ai_result, exec_result, sync_result] if r is not None)

        if success_count == total_count:
            print("🎉 Full stack demo completed successfully!")
        else:
            print(f"⚠️  Demo completed with {total_count - success_count} issue(s)")


async def main():
    """Main demonstration entry point"""
    parser = argparse.ArgumentParser(description="OOS Full Stack Demonstration")
    parser.add_argument("problem", help="Problem to solve with AI assistance")
    parser.add_argument("--command", help="Command to execute via RelayQ")
    parser.add_argument("--distributed", action="store_true", help="Use distributed execution")
    parser.add_argument("--test", action="store_true", help="Run with test scenario")

    args = parser.parse_args()

    # Use test scenario if requested
    if args.test:
        args.problem = "How can I improve my development workflow?"
        args.command = "echo 'OOS Full Stack Test!' && date"

    demo = OOSFullStackDemo()

    try:
        await demo.initialize()
        results = await demo.run_full_demo(
            problem=args.problem,
            command=args.command,
            distributed=args.distributed
        )

        # Save results if demo was successful
        if any(r and r.get("success") for r in [results.get("ai_analysis"),
                                               results.get("distributed_execution"),
                                               results.get("archon_sync")]):
            results_file = Path(f"demo_results_{int(time.time())}.json")
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n💾 Results saved to: {results_file}")

    finally:
        await demo.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
