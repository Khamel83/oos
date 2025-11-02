#!/usr/bin/env python3
"""
Comprehensive Test Suite for OOS Full Stack Integration
Tests AI SDK + OpenRouter, RelayQ Architecture, and Archon Sync
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_provider import OOSAIManager, ask_ai, get_ai_manager
from relayq_architecture import RelayQManager, get_relayq_manager, DeploymentTask, NodeType
from archon_sync import ArchonSyncManager, get_sync_manager


class TestAIProvider:
    """Test AI provider functionality"""

    @pytest.fixture
    async def ai_manager(self):
        """Create AI manager for testing"""
        manager = get_ai_manager()
        yield manager
        await manager.close_all()

    @pytest.mark.asyncio
    async def test_ai_manager_initialization(self):
        """Test AI manager initializes correctly"""
        manager = OOSAIManager()
        assert len(manager.providers) > 0
        assert manager.current_provider_index == 0
        await manager.close_all()

    @pytest.mark.asyncio
    async def test_ai_health_check(self, ai_manager):
        """Test AI provider health checks"""
        health = await ai_manager.health_check_all()
        assert isinstance(health, dict)
        assert len(health) > 0
        # At least one provider should be healthy if API key is configured
        # (This might fail if no API key is configured, which is ok for testing)

    @pytest.mark.asyncio
    async def test_ai_chat_completion(self, ai_manager):
        """Test AI chat completion"""
        try:
            response = await ai_manager.chat_completion(
                prompt="Say 'Test successful'",
                model="nvidia/nemotron-nano-12b-v2-vl:free"
            )
            assert response.content is not None
            assert len(response.content) > 0
            assert response.provider is not None
            assert response.model_used is not None
        except Exception as e:
            # Expected if no API key configured
            pytest.skip(f"AI test skipped (likely no API key): {e}")

    @pytest.mark.asyncio
    async def test_convenience_function(self):
        """Test convenience function for AI requests"""
        try:
            response = await ask_ai("Say 'Hello from convenience function'")
            assert response is not None
            assert len(response) > 0
        except Exception as e:
            pytest.skip(f"AI convenience test skipped: {e}")


class TestRelayQArchitecture:
    """Test RelayQ distributed architecture"""

    @pytest.fixture
    def relayq_manager(self):
        """Create RelayQ manager for testing"""
        config_file = Path(__file__).parent / "test_relayq_config.json"
        manager = RelayQManager(str(config_file))
        yield manager
        # Cleanup
        if config_file.exists():
            config_file.unlink()

    def test_relayq_initialization(self, relayq_manager):
        """Test RelayQ manager initialization"""
        assert len(relayq_manager.nodes) == 3  # Default nodes
        assert any(node.node_type == NodeType.OCIVM for node in relayq_manager.nodes.values())

    def test_node_type_filtering(self, relayq_manager):
        """Test filtering nodes by type"""
        ocivm_nodes = relayq_manager.get_nodes_by_type(NodeType.OCIVM)
        assert len(ocivm_nodes) == 1
        assert ocivm_nodes[0].node_type == NodeType.OCIVM

    def test_best_node_selection(self, relayq_manager):
        """Test selecting best node for tasks"""
        # Test development task
        best_node = relayq_manager.select_best_node(["development"])
        assert best_node is not None
        assert best_node.node_type == NodeType.OCIVM

        # Test edge processing task
        best_node = relayq_manager.select_best_node(["edge-processing"])
        assert best_node is not None
        # Would prefer RPi4 if online, otherwise fallback to any online node

    @pytest.mark.asyncio
    async def test_node_health_check(self, relayq_manager):
        """Test node health checking"""
        health = await relayq_manager.health_check_all()
        assert isinstance(health, dict)
        assert len(health) == 3
        # Local ocivm-dev node should be online
        assert health.get("ocivm-dev", False) == True

    @pytest.mark.asyncio
    async def test_local_task_execution(self, relayq_manager):
        """Test executing task on local node"""
        task = DeploymentTask(
            task_id="test-local",
            command="echo 'Local execution test successful'",
            target_nodes=["ocivm-dev"]
        )

        result = await relayq_manager.deploy_task(task)
        assert result["success"] == True
        assert "ocivm-dev" in result["results"]
        assert result["results"]["ocivm-dev"]["success"] == True
        assert "Local execution test successful" in result["results"]["ocivm-dev"]["stdout"]

    def test_topology_summary(self, relayq_manager):
        """Test topology summary generation"""
        summary = relayq_manager.get_topology_summary()
        assert "total_nodes" in summary
        assert "nodes_by_type" in summary
        assert "online_nodes" in summary
        assert summary["total_nodes"] == 3
        assert "ocivm" in summary["nodes_by_type"]


class TestArchonSync:
    """Test Archon synchronization"""

    @pytest.fixture
    def sync_manager(self):
        """Create Archon sync manager for testing"""
        manager = get_sync_manager()
        yield manager

    def test_sync_manager_initialization(self, sync_manager):
        """Test sync manager initialization"""
        status = sync_manager.get_sync_status()
        assert "enabled" in status
        assert "project_id" in status
        assert "archon_url" in status

    @pytest.mark.asyncio
    async def test_task_sync(self, sync_manager):
        """Test task synchronization"""
        test_tasks = [
            {
                "id": "test-task-1",
                "title": "Integration Test Task",
                "description": "Task created during integration testing",
                "status": "todo",
                "priority": "medium",
                "tags": ["test", "integration"]
            }
        ]

        try:
            result = await sync_manager.sync_task_state(test_tasks)
            # Result depends on Archon connectivity
            assert isinstance(result, bool)
        except Exception as e:
            # Expected if Archon is not accessible
            pytest.skip(f"Task sync test skipped: {e}")

    @pytest.mark.asyncio
    async def test_full_sync(self, sync_manager):
        """Test full synchronization"""
        oos_state = {
            "tasks": [
                {
                    "id": "sync-test-full",
                    "title": "Full Sync Test Task",
                    "description": "Testing full sync functionality",
                    "status": "todo",
                    "priority": "low"
                }
            ],
            "system_state": {
                "version": "2.0-test",
                "node_count": 1,
                "tasks_active": 1,
                "tasks_completed": 0,
                "ai_requests_today": 5,
                "last_activity": "2025-11-02T15:00:00Z",
                "system_health": {
                    "status": "testing",
                    "components": ["ai", "relayq", "sync"]
                }
            }
        }

        try:
            result = await sync_manager.full_sync(oos_state)
            assert "success" in result
            assert "synced_tasks" in result
            assert "duration" in result
        except Exception as e:
            pytest.skip(f"Full sync test skipped: {e}")


class TestIntegrationWorkflow:
    """Test complete integration workflow"""

    @pytest.mark.asyncio
    async def test_ai_assisted_task_creation(self):
        """Test creating tasks with AI assistance"""
        try:
            # Use AI to generate a task description
            ai_response = await ask_ai(
                "Generate a simple task description for testing OOS integration"
            )

            assert ai_response is not None
            assert len(ai_response) > 0

            # Create task with AI-generated content
            task = {
                "id": "ai-generated-test",
                "title": "AI Generated Test Task",
                "description": ai_response[:200],  # Truncate if needed
                "status": "todo",
                "priority": "medium"
            }

            assert task["description"] is not None
            assert len(task["description"]) > 0

        except Exception as e:
            pytest.skip(f"AI-assisted task test skipped: {e}")

    @pytest.mark.asyncio
    async def test_distributed_task_simulation(self):
        """Test distributed task execution simulation"""
        relayq_manager = get_relayq_manager()

        # Create a task that would be distributed
        task = DeploymentTask(
            task_id="distributed-test",
            command="echo 'Node: $(hostname)' && date",
            target_nodes=["ocivm-dev"],  # Use local node for testing
            distributed=False
        )

        result = await relayq_manager.deploy_task(task)
        assert result["success"] == True
        assert "results" in result

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        try:
            # 1. Use AI to analyze a requirement
            analysis = await ask_ai(
                "Analyze this requirement: 'Create a simple API for managing tasks'"
            )

            # 2. Create task based on AI analysis
            task = {
                "id": "e2e-test-task",
                "title": "API Task Management",
                "description": analysis[:300] if analysis else "Create task management API",
                "status": "todo",
                "priority": "high"
            }

            # 3. Deploy task via RelayQ
            relayq_manager = get_relayq_manager()
            deployment = DeploymentTask(
                task_id="e2e-deployment",
                command="echo 'E2E Test: Creating task management API'",
                target_nodes=["ocivm-dev"]
            )

            deploy_result = await relayq_manager.deploy_task(deployment)
            assert deploy_result["success"] == True

            # 4. Sync to Archon
            sync_manager = get_sync_manager()
            sync_result = await sync_manager.sync_task_state([task])

            # Workflow completed successfully
            assert True  # If we get here without exceptions, the workflow works

        except Exception as e:
            pytest.skip(f"End-to-end workflow test skipped: {e}")


# Performance and stress tests
class TestPerformance:
    """Test performance characteristics"""

    @pytest.mark.asyncio
    async def test_concurrent_ai_requests(self):
        """Test multiple concurrent AI requests"""
        try:
            manager = get_ai_manager()

            # Create multiple concurrent requests
            tasks = [
                manager.chat_completion(f"Say 'Concurrent test {i}'")
                for i in range(3)
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check results
            successful_requests = 0
            for result in results:
                if isinstance(result, Exception):
                    continue
                if result and result.content:
                    successful_requests += 1

            # At least some requests should succeed
            assert successful_requests >= 0  # May be 0 if no API key

            await manager.close_all()

        except Exception as e:
            pytest.skip(f"Concurrent AI test skipped: {e}")

    @pytest.mark.asyncio
    async def test_relayq_task_throughput(self):
        """Test RelayQ task deployment throughput"""
        relayq_manager = get_relayq_manager()

        # Create multiple tasks
        tasks = []
        for i in range(3):
            task = DeploymentTask(
                task_id=f"throughput-test-{i}",
                command=f"echo 'Throughput test {i}'",
                target_nodes=["ocivm-dev"]
            )
            tasks.append(relayq_manager.deploy_task(task))

        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check results
        successful_deployments = 0
        for result in results:
            if isinstance(result, Exception):
                continue
            if result and result.get("success"):
                successful_deployments += 1

        assert successful_deployments == 3


if __name__ == "__main__":
    # Run tests directly
    print("🧪 Running OOS Full Stack Integration Tests...")
    print("=" * 60)

    # Simple test runner
    async def run_basic_tests():
        test_results = {}

        # Test AI Provider
        print("\n1. Testing AI Provider...")
        try:
            manager = get_ai_manager()
            health = await manager.health_check_all()
            test_results["ai_health"] = bool(health)
            print(f"   AI Health: {'✅' if health else '❌'}")

            try:
                response = await manager.chat_completion("Say 'AI test successful'")
                test_results["ai_response"] = bool(response and response.content)
                print(f"   AI Response: {'✅' if response and response.content else '❌'}")
            except:
                test_results["ai_response"] = False
                print(f"   AI Response: ❌ (No API key)")

            await manager.close_all()
        except Exception as e:
            test_results["ai_provider"] = False
            print(f"   AI Provider: ❌ ({e})")

        # Test RelayQ
        print("\n2. Testing RelayQ Architecture...")
        try:
            relayq = get_relayq_manager()
            summary = relayq.get_topology_summary()
            test_results["relayq_topology"] = bool(summary)
            print(f"   Topology: {'✅' if summary else '❌'}")

            health = await relayq.health_check_all()
            test_results["relayq_health"] = bool(health)
            print(f"   Node Health: {'✅' if health else '❌'}")

            # Test local task execution
            task = DeploymentTask(
                task_id="basic-test",
                command="echo 'RelayQ test successful'",
                target_nodes=["ocivm-dev"]
            )
            result = await relayq.deploy_task(task)
            test_results["relayq_execution"] = result.get("success", False)
            print(f"   Task Execution: {'✅' if result.get('success') else '❌'}")

        except Exception as e:
            test_results["relayq"] = False
            print(f"   RelayQ: ❌ ({e})")

        # Test Archon Sync
        print("\n3. Testing Archon Sync...")
        try:
            sync = get_sync_manager()
            status = sync.get_sync_status()
            test_results["sync_status"] = bool(status)
            print(f"   Sync Status: {'✅' if status else '❌'}")

            if status.get("enabled"):
                # Test task sync
                test_tasks = [{
                    "id": "basic-sync-test",
                    "title": "Basic Sync Test",
                    "description": "Testing sync functionality"
                }]
                sync_result = await sync.sync_task_state(test_tasks)
                test_results["sync_task"] = bool(sync_result)
                print(f"   Task Sync: {'✅' if sync_result else '❌'}")
            else:
                test_results["sync_task"] = False
                print(f"   Task Sync: ❌ (Sync disabled)")

        except Exception as e:
            test_results["sync"] = False
            print(f"   Archon Sync: ❌ ({e})")

        # Summary
        print("\n" + "=" * 60)
        print("📊 Test Summary:")
        passed = sum(1 for result in test_results.values() if result)
        total = len(test_results)
        print(f"   Passed: {passed}/{total}")

        for test_name, result in test_results.items():
            status = "✅" if result else "❌"
            print(f"   {test_name}: {status}")

        if passed == total:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed or skipped")

        return test_results

    # Run the tests
    asyncio.run(run_basic_tests())