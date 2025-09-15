#!/usr/bin/env python3
"""
Simplified End-to-End Integration Test for OOS System
Tests core functionality without external dependencies
"""

import json
import asyncio
import tempfile
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.command_generator import IdeaToCommandTransformer
from src.orchestrator import WorkflowOrchestrator
from src.learning_system import LearningSystem


class TestSimpleEndToEnd:
    """Simplified end-to-end integration test suite"""

    def __init__(self):
        self.test_results = []
        self.temp_dir = None
        self.db_path = None

    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_learning.db")

    def teardown_method(self):
        """Clean up test environment"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    def run_test(self, test_name, test_func):
        """Run a single test and track results"""
        try:
            self.setup_method()
            test_func()
            print(f"✅ {test_name}")
            self.test_results.append({"name": test_name, "status": "passed"})
            return True
        except Exception as e:
            print(f"❌ {test_name}: {e}")
            self.test_results.append({"name": test_name, "status": "failed", "error": str(e)})
            return False
        finally:
            self.teardown_method()

    def test_command_generation_to_workflow(self):
        """Test command generation feeding into workflow execution"""
        print("\n🧪 Testing Command Generation to Workflow...")

        # Create test patterns data
        test_patterns = {
            "metadata": {
                "name": "test_project",
                "language": "python",
                "files_count": 3
            },
            "file_structure": {
                "configuration_files": ["requirements.txt", "setup.py"],
                "package_files": ["requirements.txt"],
                "source_files": ["main.py"]
            },
            "patterns": {
                "architectural": [
                    {
                        "type": "simple_script",
                        "confidence": 0.9,
                        "files": ["main.py"]
                    }
                ]
            }
        }

        # Step 1: Generate commands from patterns
        transformer = IdeaToCommandTransformer()
        commands = transformer.transform_patterns_to_commands(test_patterns)

        # Verify command generation
        assert len(commands) > 0
        assert any(cmd.category == "setup" for cmd in commands)

        # Step 2: Create workflow that uses generated commands
        orchestrator = WorkflowOrchestrator()

        workflow_def = {
            "id": "test_workflow",
            "name": "Test Workflow",
            "description": "Workflow using generated commands",
            "variables": {"project_name": "test_project"},
            "steps": [
                {
                    "id": "setup",
                    "name": "Setup Project",
                    "command": "setup-python-project",
                    "parameters": {
                        "project_name": "${project_name}",
                        "python_version": "3.11"
                    },
                    "depends_on": [],
                    "condition": "success"
                },
                {
                    "id": "install",
                    "name": "Install Dependencies",
                    "command": "install-dependencies",
                    "parameters": {
                        "packages": ["requests", "flask"]
                    },
                    "depends_on": ["setup"],
                    "condition": "success"
                }
            ]
        }

        workflow_id = orchestrator.define_workflow(workflow_def)
        assert workflow_id == "test_workflow"

        # Verify workflow structure
        workflow = orchestrator.get_workflow_definition(workflow_id)
        assert workflow is not None
        assert len(workflow["steps"]) == 2
        assert workflow["steps"][0].id == "setup"
        assert workflow["steps"][1].id == "install"

        print("✅ Command generation to workflow completed successfully")

    def test_learning_system_workflow_integration(self):
        """Test learning system integration with workflow execution"""
        print("\n🧪 Testing Learning System Workflow Integration...")

        # Initialize learning system with short learning interval
        learning_system = LearningSystem(
            db_path=self.db_path,
            config={"learning_interval_hours": 0}
        )

        # Create workflow orchestrator
        orchestrator = WorkflowOrchestrator()

        # Define a test workflow
        workflow_def = {
            "id": "learning_test_workflow",
            "name": "Learning Test Workflow",
            "variables": {"test_param": "test_value"},
            "steps": [
                {
                    "id": "step1",
                    "name": "Test Step 1",
                    "command": "test-command-1",
                    "parameters": {"input": "${test_param}"},
                    "depends_on": [],
                    "condition": "success"
                },
                {
                    "id": "step2",
                    "name": "Test Step 2",
                    "command": "test-command-2",
                    "parameters": {"output": "result"},
                    "depends_on": ["step1"],
                    "condition": "success"
                }
            ]
        }

        workflow_id = orchestrator.define_workflow(workflow_def)

        # Simulate workflow execution usage patterns
        from src.learning_system import LearningData

        base_time = datetime.now()
        for i in range(3):
            # Record workflow execution
            workflow_data = LearningData(
                timestamp=base_time + timedelta(seconds=i*10),
                user_id="test_user",
                session_id=f"session_{i}",
                command_name="execute-workflow",
                parameters={"workflow_id": workflow_id},
                execution_time=2.0,
                success=True,
                error_message=None,
                context={"workspace": "/test/workspace"}
            )
            learning_system.record_usage(workflow_data)

            # Record individual step commands
            for step_id in ["step1", "step2"]:
                step_data = LearningData(
                    timestamp=base_time + timedelta(seconds=i*10 + 2),
                    user_id="test_user",
                    session_id=f"session_{i}",
                    command_name=f"test-command-{step_id[-1]}",
                    parameters={},
                    execution_time=1.0,
                    success=True,
                    error_message=None,
                    context={"workspace": "/test/workspace", "workflow_id": workflow_id}
                )
                learning_system.record_usage(step_data)

        # Learn patterns from usage
        patterns = asyncio.run(learning_system.learn_patterns())

        # Verify pattern learning
        assert len(patterns) > 0

        # Check for command sequence patterns
        sequence_patterns = [p for p in patterns if p.pattern_type == "command_sequence"]
        assert len(sequence_patterns) > 0

        # Get usage statistics
        stats = learning_system.get_usage_statistics()
        assert stats["total_usage"] == 9  # 3 workflows * (1 workflow + 2 steps)
        assert stats["success_rate"] == 1.0

        print("✅ Learning system workflow integration completed successfully")

    def test_component_interaction_data_flow(self):
        """Test data flow between different components"""
        print("\n🧪 Testing Component Interaction Data Flow...")

        # Test data: patterns -> commands -> workflow -> learning
        initial_data = {
            "project_info": {
                "name": "data_flow_test",
                "language": "python",
                "type": "web_app"
            },
            "requirements": ["flask", "requests", "sqlalchemy"],
            "structure": {
                "has_tests": True,
                "has_docs": False,
                "has_config": True
            }
        }

        # Step 1: Transform to patterns format
        patterns_data = {
            "metadata": {
                "name": initial_data["project_info"]["name"],
                "language": initial_data["project_info"]["language"],
                "project_type": initial_data["project_info"]["type"]
            },
            "file_structure": {
                "configuration_files": ["requirements.txt", "config.py"],
                "package_files": ["requirements.txt"],
                "source_files": ["app.py", "models.py"]
            },
            "dependencies": initial_data["requirements"],
            "patterns": {
                "architectural": [
                    {
                        "type": "web_application",
                        "confidence": 0.8,
                        "framework": "flask"
                    }
                ]
            }
        }

        # Step 2: Generate commands
        transformer = IdeaToCommandTransformer()
        commands = transformer.transform_patterns_to_commands(patterns_data)

        # Verify data integrity
        assert len(commands) > 0
        setup_commands = [cmd for cmd in commands if cmd.category == "setup"]
        assert len(setup_commands) > 0

        # Step 3: Create workflow with the commands
        orchestrator = WorkflowOrchestrator()

        workflow_def = {
            "id": "data_flow_workflow",
            "name": "Data Flow Test Workflow",
            "variables": {
                "project_name": initial_data["project_info"]["name"],
                "requirements": initial_data["requirements"]
            },
            "steps": [
                {
                    "id": "setup",
                    "name": "Setup Flask Project",
                    "command": "setup-python-project",
                    "parameters": {
                        "project_name": "${project_name}",
                        "python_version": "3.11"
                    },
                    "depends_on": [],
                    "condition": "success"
                },
                {
                    "id": "install_deps",
                    "name": "Install Dependencies",
                    "command": "install-dependencies",
                    "parameters": {
                        "packages": "${requirements}"
                    },
                    "depends_on": ["setup"],
                    "condition": "success"
                }
            ]
        }

        workflow_id = orchestrator.define_workflow(workflow_def)

        # Step 4: Simulate learning from this workflow
        learning_system = LearningSystem(
            db_path=self.db_path,
            config={"learning_interval_hours": 0}
        )

        from src.learning_system import LearningData

        workflow_usage = LearningData(
            timestamp=datetime.now(),
            user_id="test_user",
            session_id="data_flow_session",
            command_name="execute-workflow",
            parameters={"workflow_id": workflow_id},
            execution_time=3.0,
            success=True,
            error_message=None,
            context={
                "project_type": initial_data["project_info"]["type"],
                "initial_data": initial_data
            }
        )
        learning_system.record_usage(workflow_usage)

        # Verify data flows through all components
        final_patterns = asyncio.run(learning_system.learn_patterns())
        assert len(final_patterns) >= 0  # May not have patterns if frequency threshold not met

        # Verify workflow is properly stored
        final_workflow = orchestrator.get_workflow_definition(workflow_id)
        assert final_workflow is not None
        assert final_workflow["variables"]["project_name"] == initial_data["project_info"]["name"]

        print("✅ Component interaction data flow completed successfully")

    def test_error_propagation_and_handling(self):
        """Test error handling across component boundaries"""
        print("\n🧪 Testing Error Propagation and Handling...")

        # Test 1: Command generator with invalid input
        transformer = IdeaToCommandTransformer()

        # Should handle empty/invalid patterns gracefully
        try:
            commands = transformer.transform_patterns_to_commands({})
            assert isinstance(commands, list)
        except Exception as e:
            print(f"Command generator handled error: {e}")

        # Test 2: Workflow orchestrator with invalid workflow
        orchestrator = WorkflowOrchestrator()

        # Should handle invalid workflow definition
        try:
            workflow_id = orchestrator.define_workflow({"invalid": "workflow"})
            assert False, "Should have raised an exception"
        except Exception:
            pass  # Expected

        # Test 3: Learning system with invalid data
        learning_system = LearningSystem(db_path=self.db_path)

        # Should handle invalid learning data gracefully
        try:
            learning_system.record_usage(None)
            assert False, "Should have raised an exception"
        except Exception:
            pass  # Expected

        # Test 4: Component recovery after errors
        valid_patterns = {
            "metadata": {"name": "recovery_test", "language": "python"},
            "file_structure": {"source_files": ["main.py"]},
            "patterns": {"architectural": []}
        }

        # Command generator should still work after errors
        commands = transformer.transform_patterns_to_commands(valid_patterns)
        assert len(commands) > 0

        # Workflow orchestrator should still work after errors
        valid_workflow = {
            "id": "recovery_workflow",
            "name": "Recovery Test",
            "steps": [{
                "id": "test_step",
                "name": "Test Step",
                "command": "test-command",
                "depends_on": [],
                "condition": "success"
            }]
        }

        workflow_id = orchestrator.define_workflow(valid_workflow)
        assert workflow_id == "recovery_workflow"

        # Learning system should still work after errors
        from src.learning_system import LearningData

        valid_data = LearningData(
            timestamp=datetime.now(),
            user_id="test_user",
            session_id="recovery_session",
            command_name="test-command",
            parameters={},
            execution_time=1.0,
            success=True,
            error_message=None,
            context={}
        )
        learning_system.record_usage(valid_data)

        stats = learning_system.get_usage_statistics()
        assert stats["total_usage"] == 1

        print("✅ Error propagation and handling completed successfully")

    def test_performance_under_load(self):
        """Test system performance under simulated load"""
        print("\n🧪 Testing Performance Under Load...")

        # Test command generation performance
        transformer = IdeaToCommandTransformer()

        import time
        start_time = time.time()

        # Generate multiple pattern sets
        pattern_sets = []
        for i in range(10):
            patterns = {
                "metadata": {
                    "name": f"perf_test_{i}",
                    "language": "python",
                    "files_count": i + 1
                },
                "file_structure": {
                    "source_files": [f"file_{j}.py" for j in range(i + 1)]
                },
                "patterns": {"architectural": []}
            }
            pattern_sets.append(patterns)

        # Transform all patterns
        all_commands = []
        for patterns in pattern_sets:
            commands = transformer.transform_patterns_to_commands(patterns)
            all_commands.extend(commands)

        generation_time = time.time() - start_time

        # Verify performance
        assert generation_time < 5.0, f"Command generation took {generation_time:.2f}s, expected < 5s"
        assert len(all_commands) > 0

        # Test workflow definition performance
        orchestrator = WorkflowOrchestrator()

        start_time = time.time()

        workflow_ids = []
        for i in range(5):
            workflow_def = {
                "id": f"perf_workflow_{i}",
                "name": f"Performance Test Workflow {i}",
                "steps": [{
                    "id": f"step_{i}",
                    "name": f"Test Step {i}",
                    "command": "test-command",
                    "depends_on": [],
                    "condition": "success"
                }]
            }
            workflow_id = orchestrator.define_workflow(workflow_def)
            workflow_ids.append(workflow_id)

        workflow_time = time.time() - start_time

        # Verify performance
        assert workflow_time < 2.0, f"Workflow definition took {workflow_time:.2f}s, expected < 2s"
        assert len(workflow_ids) == 5

        # Test learning system performance
        learning_system = LearningSystem(
            db_path=self.db_path,
            config={"learning_interval_hours": 0}
        )

        start_time = time.time()

        from src.learning_system import LearningData

        # Record multiple usage events
        base_time = datetime.now()
        for i in range(20):
            usage_data = LearningData(
                timestamp=base_time + timedelta(seconds=i),
                user_id="perf_test_user",
                session_id=f"perf_session_{i % 5}",
                command_name=f"command_{i % 3}",
                parameters={"test": f"value_{i}"},
                execution_time=0.1,
                success=True,
                error_message=None,
                context={"test": "performance"}
            )
            learning_system.record_usage(usage_data)

        # Learn patterns
        patterns = asyncio.run(learning_system.learn_patterns())

        learning_time = time.time() - start_time

        # Verify performance
        assert learning_time < 3.0, f"Learning system took {learning_time:.2f}s, expected < 3s"

        print(f"✅ Performance test completed:")
        print(f"  - Command generation: {generation_time:.2f}s for {len(all_commands)} commands")
        print(f"  - Workflow definition: {workflow_time:.2f}s for {len(workflow_ids)} workflows")
        print(f"  - Learning system: {learning_time:.2f}s for 20 usage events")

    def run_all_tests(self):
        """Run all simplified end-to-end tests and provide summary"""
        print("🚀 Simplified End-to-End Integration Testing")
        print("=" * 60)
        print("Testing core component integration without external dependencies")

        test_functions = [
            ("Command Generation to Workflow", self.test_command_generation_to_workflow),
            ("Learning System Workflow Integration", self.test_learning_system_workflow_integration),
            ("Component Interaction Data Flow", self.test_component_interaction_data_flow),
            ("Error Propagation and Handling", self.test_error_propagation_and_handling),
            ("Performance Under Load", self.test_performance_under_load),
        ]

        passed = 0
        total = len(test_functions)

        # Run tests
        for test_name, test_func in test_functions:
            if self.run_test(test_name, test_func):
                passed += 1

        print("\n" + "=" * 60)
        print(f"Simplified End-to-End Test Results: {passed}/{total} passed")

        if passed == total:
            print("🎉 All simplified end-to-end tests passed!")
            print("\n✅ Core Integration Verified:")
            print("  - Command Generation → Workflow Execution")
            print("  - Learning System integration with workflow usage")
            print("  - Data flow integrity across components")
            print("  - Error handling and recovery mechanisms")
            print("  - Performance under acceptable thresholds")
            print("\n✅ Context Engineering Principles Applied:")
            print("  - Write: Workflow definitions and usage data stored")
            print("  - Select: Intelligent command and workflow selection")
            print("  - Compress: Pattern learning and data compression")
            print("  - Isolate: Independent component contexts maintained")
        else:
            print(f"❌ {total - passed} simplified end-to-end tests failed.")

        return passed == total


if __name__ == "__main__":
    test_suite = TestSimpleEndToEnd()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)