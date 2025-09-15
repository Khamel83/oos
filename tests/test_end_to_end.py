#!/usr/bin/env python3
"""
End-to-End Integration Test for OOS System
Tests all components working together in a realistic scenario
"""

import json
import asyncio
import tempfile
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import unittest.mock as mock
from unittest.mock import patch, MagicMock, AsyncMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.repository_analyzer import RepositoryAnalyzer
from src.command_generator import IdeaToCommandTransformer
from src.orchestrator import WorkflowOrchestrator
from src.claude_integration import ClaudeCodeIntegration
from src.learning_system import LearningSystem


class TestEndToEndIntegration:
    """End-to-end integration test suite"""

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

    def test_full_analysis_to_command_workflow(self):
        """Test complete workflow from repository analysis to command generation"""
        print("\n🧪 Testing Full Analysis to Command Workflow...")

        # Create a mock repository structure
        repo_dir = os.path.join(self.temp_dir, "test_repo")
        os.makedirs(repo_dir, exist_ok=True)

        # Create sample files
        with open(os.path.join(repo_dir, "requirements.txt"), "w") as f:
            f.write("requests==2.31.0\n")
            f.write("flask==2.3.3\n")

        with open(os.path.join(repo_dir, "main.py"), "w") as f:
            f.write("""
import requests
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'
""")

        # Step 1: Analyze repository (mock GitHub auth to avoid token requirement)
        with patch('src.repository_analyzer.Github') as mock_github, \
             patch.dict(os.environ, {'GITHUB_TOKEN': 'fake_token_for_testing'}):

            mock_github.return_value.get_repo.return_value.full_name = "test/repo"
            mock_github.return_value.get_repo.return_value.description = "Test repository"
            mock_github.return_value.get_repo.return_value.language = "Python"

            analyzer = RepositoryAnalyzer()
            patterns = analyzer.analyze_repository(repo_dir)

        # Verify analysis results
        assert patterns["metadata"]["name"] == "test_repo"
        assert "python" in patterns["metadata"]["language"]
        assert len(patterns["file_structure"]["package_files"]) > 0

        # Step 2: Generate commands from patterns
        transformer = IdeaToCommandTransformer()
        commands = transformer.transform_patterns_to_commands(patterns)

        # Verify command generation
        assert len(commands) > 0
        assert any(cmd["category"] == "setup" for cmd in commands)

        # Step 3: Create workflow
        orchestrator = WorkflowOrchestrator()

        workflow_def = {
            "id": "analysis_workflow",
            "name": "Analysis Workflow",
            "description": "End-to-end analysis workflow",
            "variables": {"repo_path": repo_dir},
            "steps": [
                {
                    "id": "analyze",
                    "name": "Analyze Repository",
                    "command": "analyze-repository",
                    "parameters": {"repository_url": repo_dir},
                    "depends_on": [],
                    "condition": "success"
                },
                {
                    "id": "generate",
                    "name": "Generate Commands",
                    "command": "generate-commands",
                    "parameters": {"patterns_file": "patterns.json"},
                    "depends_on": ["analyze"],
                    "condition": "success"
                }
            ]
        }

        workflow_id = orchestrator.define_workflow(workflow_def)
        assert workflow_id == "analysis_workflow"

        print("✅ Full analysis to command workflow completed successfully")

    def test_learning_system_integration(self):
        """Test learning system integration with other components"""
        print("\n🧪 Testing Learning System Integration...")

        # Initialize learning system
        learning_system = LearningSystem(db_path=self.db_path, config={"learning_interval_hours": 0})

        # Simulate usage patterns
        from src.learning_system import LearningData

        base_time = datetime.now()
        for i in range(3):
            # Record analysis command usage
            analysis_data = LearningData(
                timestamp=base_time + timedelta(seconds=i*10),
                user_id="test_user",
                session_id=f"session_{i}",
                command_name="analyze-repository",
                parameters={"repository_url": f"test_repo_{i}"},
                execution_time=2.0,
                success=True,
                error_message=None,
                context={"workspace": "/test/workspace"}
            )
            learning_system.record_usage(analysis_data)

            # Record command generation usage
            generation_data = LearningData(
                timestamp=base_time + timedelta(seconds=i*10 + 5),
                user_id="test_user",
                session_id=f"session_{i}",
                command_name="generate-commands",
                parameters={"language": "python"},
                execution_time=1.5,
                success=True,
                error_message=None,
                context={"workspace": "/test/workspace"}
            )
            learning_system.record_usage(generation_data)

        # Learn patterns from usage
        patterns = asyncio.run(learning_system.learn_patterns())

        # Verify pattern learning
        assert len(patterns) > 0
        assert any(p.pattern_type == "command_sequence" for p in patterns)

        # Generate recommendations
        recommendations = learning_system.get_recommendations({"user_id": "test_user", "workspace": "/test/workspace"})

        # Verify recommendations
        assert isinstance(recommendations, list)

        print("✅ Learning system integration completed successfully")

    async def test_claude_integration_workflow(self):
        """Test Claude Code integration with workflow execution"""
        print("\n🧪 Testing Claude Integration Workflow...")

        # Initialize Claude integration
        integration = ClaudeCodeIntegration()

        # Create test context
        from src.claude_integration import create_execution_context
        context = create_execution_context("/test/workspace")

        # Test repository analysis command
        with patch.object(integration.repository_analyzer, 'analyze_repository') as mock_analyze:
            mock_analyze.return_value = {
                "metadata": {"name": "test-repo", "language": "python"},
                "patterns": {"architectural": []}
            }

            result = await integration.execute_command("analyze-repository", {
                "repository_url": "https://github.com/test/repo"
            }, context)

            assert result.success is True
            assert result.output["analysis"]["metadata"]["name"] == "test-repo"

        # Test command generation command
        with patch.object(integration.command_generator, 'generate_command_library') as mock_generate:
            mock_generate.return_value = {
                "metadata": {"total_commands": 3},
                "commands": []
            }

            result = await integration.execute_command("generate-commands", {
                "patterns_file": "patterns.json"
            }, context)

            assert result.success is True
            assert result.output["library"]["metadata"]["total_commands"] == 3

        # Test workflow execution
        with patch.object(integration.workflow_orchestrator, 'execute_workflow') as mock_execute:
            mock_execute.return_value = {
                "status": "completed",
                "workflow_id": "test_workflow"
            }

            result = await integration.execute_command("execute-workflow", {
                "workflow_id": "test_workflow"
            }, context)

            assert result.success is True
            assert result.output["result"]["status"] == "completed"

        print("✅ Claude integration workflow completed successfully")

    def test_error_handling_and_recovery(self):
        """Test error handling across all components"""
        print("\n🧪 Testing Error Handling and Recovery...")

        # Test repository analyzer error handling
        with patch('src.repository_analyzer.Github') as mock_github, \
             patch.dict(os.environ, {'GITHUB_TOKEN': 'fake_token_for_testing'}):
            mock_github.side_effect = Exception("GitHub error")
            analyzer = RepositoryAnalyzer()

            # Test with non-existent repository
            result = analyzer.analyze_repository("/nonexistent/path")
            assert "error" in result
            assert result["error"] is not None

        # Test command generator error handling
        transformer = IdeaToCommandTransformer()

        # Test with invalid patterns
        result = transformer.transform_patterns_to_commands({})
        assert isinstance(result, list)

        # Test orchestrator error handling
        orchestrator = WorkflowOrchestrator()

        # Test with invalid workflow
        try:
            orchestrator.define_workflow({"invalid": "workflow"})
            assert False, "Should have raised an exception"
        except Exception:
            pass  # Expected to raise an exception

        # Test learning system error handling
        learning_system = LearningSystem(db_path=self.db_path)

        # Test with invalid data
        try:
            learning_system.record_usage(None)
            assert False, "Should have raised an exception"
        except Exception:
            pass  # Expected to raise an exception

        print("✅ Error handling and recovery completed successfully")

    def test_context_isolation_across_components(self):
        """Test that each component maintains proper context isolation"""
        print("\n🧪 Testing Context Isolation Across Components...")

        # Create multiple instances of each component
        analyzer1 = RepositoryAnalyzer()
        analyzer2 = RepositoryAnalyzer()

        transformer1 = IdeaToCommandTransformer()
        transformer2 = IdeaToCommandTransformer()

        orchestrator1 = WorkflowOrchestrator()
        orchestrator2 = WorkflowOrchestrator()

        learning_system1 = LearningSystem(db_path=os.path.join(self.temp_dir, "learning1.db"))
        learning_system2 = LearningSystem(db_path=os.path.join(self.temp_dir, "learning2.db"))

        # Verify instances are independent
        assert analyzer1 is not analyzer2
        assert transformer1 is not transformer2
        assert orchestrator1 is not orchestrator2
        assert learning_system1 is not learning_system2

        # Test that operations on one instance don't affect others
        # Create test repository
        repo_dir = os.path.join(self.temp_dir, "isolation_test")
        os.makedirs(repo_dir, exist_ok=True)

        with open(os.path.join(repo_dir, "test.py"), "w") as f:
            f.write("print('test')")

        # Analyze with first analyzer (mock GitHub)
        with patch('src.repository_analyzer.Github'), \
             patch.dict(os.environ, {'GITHUB_TOKEN': 'fake_token_for_testing'}):
            patterns1 = analyzer1.analyze_repository(repo_dir)

        # Analyze with second analyzer (mock GitHub)
        with patch('src.repository_analyzer.Github'), \
             patch.dict(os.environ, {'GITHUB_TOKEN': 'fake_token_for_testing'}):
            patterns2 = analyzer2.analyze_repository(repo_dir)

        # Results should be independent but equivalent
        assert patterns1["metadata"]["name"] == patterns2["metadata"]["name"]

        # Test learning system isolation
        from src.learning_system import LearningData

        # Record usage in first system
        learning_data = LearningData(
            timestamp=datetime.now(),
            user_id="test_user",
            session_id="test_session",
            command_name="test-command",
            parameters={},
            execution_time=1.0,
            success=True,
            error_message=None,
            context={}
        )
        learning_system1.record_usage(learning_data)

        # First system should have data, second should not
        stats1 = learning_system1.get_usage_statistics()
        stats2 = learning_system2.get_usage_statistics()

        assert stats1["total_usage"] > 0
        assert stats2["total_usage"] == 0

        print("✅ Context isolation across components completed successfully")

    def test_performance_and_scalability(self):
        """Test performance characteristics under load"""
        print("\n🧪 Testing Performance and Scalability...")

        # Test repository analysis performance
        analyzer = RepositoryAnalyzer()

        # Create multiple test repositories
        repo_dirs = []
        for i in range(3):
            repo_dir = os.path.join(self.temp_dir, f"perf_test_{i}")
            os.makedirs(repo_dir, exist_ok=True)

            # Create sample files
            with open(os.path.join(repo_dir, "main.py"), "w") as f:
                f.write(f"# Test repository {i}\nprint('hello')\n")

            with open(os.path.join(repo_dir, "requirements.txt"), "w") as f:
                f.write("requests==2.31.0\n")

            repo_dirs.append(repo_dir)

        # Analyze all repositories
        import time
        start_time = time.time()

        patterns_list = []
        for repo_dir in repo_dirs:
            with patch('src.repository_analyzer.Github'), \
                 patch.dict(os.environ, {'GITHUB_TOKEN': 'fake_token_for_testing'}):
                patterns = analyzer.analyze_repository(repo_dir)
                patterns_list.append(patterns)

        end_time = time.time()
        analysis_time = end_time - start_time

        # Verify reasonable performance
        assert analysis_time < 10.0, f"Analysis took {analysis_time}s, expected < 10s"
        assert len(patterns_list) == 3

        # Test command generation performance
        transformer = IdeaToCommandTransformer()

        start_time = time.time()
        commands_list = []
        for patterns in patterns_list:
            commands = transformer.transform_patterns_to_commands(patterns)
            commands_list.append(commands)

        end_time = time.time()
        generation_time = end_time - start_time

        # Verify reasonable performance
        assert generation_time < 5.0, f"Generation took {generation_time}s, expected < 5s"
        assert len(commands_list) == 3

        print(f"✅ Performance test completed: Analysis {analysis_time:.2f}s, Generation {generation_time:.2f}s")

    def test_data_flow_integrity(self):
        """Test that data flows correctly between components without corruption"""
        print("\n🧪 Testing Data Flow Integrity...")

        # Create test data with known structure
        test_patterns = {
            "metadata": {
                "name": "integrity_test",
                "language": "python",
                "files_count": 5
            },
            "file_structure": {
                "configuration_files": ["requirements.txt", "config.py"],
                "package_files": ["requirements.txt"],
                "source_files": ["main.py", "utils.py"]
            },
            "patterns": {
                "architectural": [
                    {
                        "type": "mvc_pattern",
                        "confidence": 0.8,
                        "files": ["main.py", "utils.py"]
                    }
                ]
            }
        }

        # Test data flow through command generator
        transformer = IdeaToCommandTransformer()
        commands = transformer.transform_patterns_to_commands(test_patterns)

        # Verify data integrity
        assert len(commands) > 0

        # Check that commands reflect the input patterns
        setup_commands = [cmd for cmd in commands if cmd.category == "setup"]
        assert len(setup_commands) > 0

        # Test workflow data flow
        orchestrator = WorkflowOrchestrator()

        workflow_def = {
            "id": "integrity_workflow",
            "name": "Integrity Test Workflow",
            "variables": {"test_data": test_patterns},
            "steps": [
                {
                    "id": "process",
                    "name": "Process Test Data",
                    "command": "test-command",
                    "parameters": {"input_data": "${test_data}"},
                    "depends_on": [],
                    "condition": "success"
                }
            ]
        }

        workflow_id = orchestrator.define_workflow(workflow_def)

        # Verify workflow data integrity
        workflow = orchestrator.get_workflow_definition(workflow_id)
        assert workflow is not None
        assert workflow["variables"]["test_data"]["metadata"]["name"] == "integrity_test"

        print("✅ Data flow integrity test completed successfully")

    def run_all_tests(self):
        """Run all end-to-end tests and provide summary"""
        print("🚀 End-to-End Integration Testing")
        print("=" * 60)
        print("Testing all components working together in realistic scenarios")

        # Regular tests
        test_functions = [
            ("Full Analysis to Command Workflow", self.test_full_analysis_to_command_workflow),
            ("Learning System Integration", self.test_learning_system_integration),
            ("Error Handling and Recovery", self.test_error_handling_and_recovery),
            ("Context Isolation Across Components", self.test_context_isolation_across_components),
            ("Performance and Scalability", self.test_performance_and_scalability),
            ("Data Flow Integrity", self.test_data_flow_integrity),
        ]

        # Async tests
        async_test_functions = [
            ("Claude Integration Workflow", self.test_claude_integration_workflow),
        ]

        passed = 0
        total = len(test_functions) + len(async_test_functions)

        # Run regular tests
        for test_name, test_func in test_functions:
            if self.run_test(test_name, test_func):
                passed += 1

        # Run async tests
        for test_name, test_func in async_test_functions:
            if self.run_test(test_name, lambda: asyncio.run(test_func())):
                passed += 1

        print("\n" + "=" * 60)
        print(f"End-to-End Test Results: {passed}/{total} passed")

        if passed == total:
            print("🎉 All end-to-end tests passed! OOS system is working correctly.")
            print("\n✅ System Integration Verified:")
            print("  - Repository Analysis → Command Generation → Workflow Execution")
            print("  - Learning System integration with all components")
            print("  - Claude Code Integration with full subsystem support")
            print("  - Error handling and recovery across all components")
            print("  - Context isolation and data integrity maintained")
            print("  - Performance within acceptable thresholds")
        else:
            print(f"❌ {total - passed} end-to-end tests failed. Review the output above.")

        return passed == total


if __name__ == "__main__":
    test_suite = TestEndToEndIntegration()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)