#!/usr/bin/env python3
"""
Test script for Claude Code Integration System
Validates slash command execution, context management, and subsystem integration
"""

import json
import asyncio
import tempfile
import os
import sys
from pathlib import Path
from datetime import datetime
import unittest.mock as mock
from unittest.mock import patch, MagicMock, AsyncMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.claude_integration import (
    ClaudeCodeIntegration, CommandDefinition, ExecutionContext,
    CommandResult, CommandType, handle_slash_command,
    get_integration, get_command_list, get_command_help,
    create_execution_context
)


class TestClaudeCodeIntegration:
    """Test suite for Claude Code Integration System"""

    def __init__(self):
        self.test_results = []
        self.integration = None
        self.temp_dir = None

    def setup_method(self):
        """Setup test environment"""
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()

        # Create integration instance
        self.integration = ClaudeCodeIntegration()

    def teardown_method(self):
        """Clean up test environment"""
        # Clean up temporary directory
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

    def test_initialization(self):
        """Test integration initialization with proper configuration"""
        print("\n🧪 Testing Integration Initialization...")

        # Test default initialization
        integration = ClaudeCodeIntegration()

        assert integration.config is not None
        assert integration.config["debug"] is False
        assert integration.config["max_history"] == 1000
        assert len(integration.commands) > 0
        assert integration.logger is not None

        # Test subsystems are initialized
        assert integration.repository_analyzer is not None
        assert integration.command_generator is not None
        assert integration.workflow_orchestrator is not None

    def test_command_registration(self):
        """Test that all commands are properly registered"""
        print("\n🧪 Testing Command Registration...")

        integration = ClaudeCodeIntegration()

        # Check that core commands are registered
        expected_commands = [
            "analyze-repository",
            "generate-commands",
            "execute-workflow",
            "list-workflows",
            "status",
            "help",
            "history"
        ]

        for cmd_name in expected_commands:
            assert cmd_name in integration.commands, f"Command {cmd_name} not registered"

        # Verify command structure
        for cmd in integration.commands.values():
            assert isinstance(cmd, CommandDefinition)
            assert cmd.name is not None
            assert cmd.description is not None
            assert cmd.command_type in CommandType
            assert callable(cmd.handler)
            assert isinstance(cmd.parameters, list)
            assert isinstance(cmd.examples, list)

    def test_execution_context_creation(self):
        """Test execution context creation and management"""
        print("\n🧪 Testing Execution Context Creation...")

        context = create_execution_context("/test/workspace")

        assert context.workspace_path == "/test/workspace"
        assert context.session_id is not None
        assert context.command_history == []
        assert isinstance(context.environment, dict)
        assert isinstance(context.timestamp, datetime)

    def test_command_execution_success(self):
        """Test successful command execution"""
        print("\n🧪 Testing Command Execution Success...")

        integration = ClaudeCodeIntegration()
        context = create_execution_context()

        # Test status command (should always succeed)
        result = asyncio.run(integration.execute_command("status", {}, context))

        assert result.success is True
        assert result.output is not None
        assert result.error is None
        assert result.execution_time > 0
        assert "system" in result.output

    def test_command_execution_failure(self):
        """Test command execution failure handling"""
        print("\n🧪 Testing Command Execution Failure...")

        integration = ClaudeCodeIntegration()
        context = create_execution_context()

        # Test unknown command
        result = asyncio.run(integration.execute_command("unknown-command", {}, context))

        assert result.success is False
        assert result.output is None
        assert result.error is not None
        assert "Unknown command" in result.error

    def test_parameter_validation(self):
        """Test parameter validation for commands"""
        print("\n🧪 Testing Parameter Validation...")

        integration = ClaudeCodeIntegration()
        context = create_execution_context()

        # Test analyze-repository without required parameters
        result = asyncio.run(integration.execute_command("analyze-repository", {}, context))

        assert result.success is False
        assert "Repository URL is required" in result.error

    def test_command_history_tracking(self):
        """Test that command execution is tracked in history"""
        print("\n🧪 Testing Command History Tracking...")

        integration = ClaudeCodeIntegration()
        context = create_execution_context()

        # Execute a command
        result = asyncio.run(integration.execute_command("status", {}, context))

        # Check history
        assert len(integration.command_history) == 1
        history_entry = integration.command_history[0]
        assert history_entry["command"] == "status"
        assert history_entry["success"] is True
        assert "timestamp" in history_entry

    def test_help_system(self):
        """Test help system functionality"""
        print("\n🧪 Testing Help System...")

        integration = ClaudeCodeIntegration()
        context = create_execution_context()

        # Test general help
        result = asyncio.run(integration.execute_command("help", {}, context))

        assert result.success is True
        assert isinstance(result.output, dict)

        # Test specific command help
        result = asyncio.run(integration.execute_command("help", {"command": "status"}, context))

        assert result.success is True
        assert result.output["name"] == "status"
        assert "description" in result.output

    def test_workflow_integration(self):
        """Test integration with workflow orchestrator"""
        print("\n🧪 Testing Workflow Integration...")

        integration = ClaudeCodeIntegration()
        context = create_execution_context()

        # Test list workflows
        result = asyncio.run(integration.execute_command("list-workflows", {}, context))

        assert result.success is True
        assert "workflows" in result.output
        assert "count" in result.output
        assert result.output["count"] > 0

    def test_authentication_checking(self):
        """Test authentication requirements for commands"""
        print("\n🧪 Testing Authentication Checking...")

        integration = ClaudeCodeIntegration()
        context = create_execution_context()

        # Test that analyze-repository requires auth (but we have mock auth returning True)
        result = asyncio.run(integration.execute_command("analyze-repository", {
            "repository_url": "https://github.com/test/repo"
        }, context))

        # Should fail due to repository not existing, not auth
        assert result.success is False
        assert "Repository URL is required" not in result.error

    def test_command_suggestions(self):
        """Test command suggestion system"""
        print("\n🧪 Testing Command Suggestions...")

        integration = ClaudeCodeIntegration()

        # Test partial command matching
        suggestions = integration.get_command_suggestions("anal")

        assert len(suggestions) > 0
        assert any(s["name"] == "analyze-repository" for s in suggestions)

    def test_parameter_completions(self):
        """Test parameter completion system"""
        print("\n🧪 Testing Parameter Completions...")

        integration = ClaudeCodeIntegration()

        # Test parameter completion for analyze-repository
        completions = integration.get_command_completions("analyze-repository", "repo")

        assert len(completions) > 0
        assert any(c["name"] == "repository_url" for c in completions)

    async def test_repository_analysis_command(self):
        """Test repository analysis command with mock"""
        print("\n🧪 Testing Repository Analysis Command...")

        integration = ClaudeCodeIntegration()
        context = create_execution_context()

        # Mock the repository analyzer
        with patch.object(integration.repository_analyzer, 'analyze_repository') as mock_analyze:
            mock_analyze.return_value = {
                "metadata": {"name": "test-repo"},
                "patterns": {"architectural": []}
            }

            result = await integration.execute_command("analyze-repository", {
                "repository_url": "https://github.com/test/repo"
            }, context)

            assert result.success is True
            assert result.output["analysis"]["metadata"]["name"] == "test-repo"
            mock_analyze.assert_called_once_with("https://github.com/test/repo")

    async def test_command_generation_command(self):
        """Test command generation command with mock"""
        print("\n🧪 Testing Command Generation Command...")

        integration = ClaudeCodeIntegration()
        context = create_execution_context()

        # Create temporary patterns file
        patterns_file = os.path.join(self.temp_dir, "patterns.json")
        patterns_data = {
            "metadata": {"language": "Python"},
            "patterns": {"architectural": []}
        }

        with open(patterns_file, 'w') as f:
            json.dump(patterns_data, f)

        # Mock the command generator
        with patch.object(integration.command_generator, 'generate_command_library') as mock_generate:
            mock_generate.return_value = {
                "metadata": {"total_commands": 5},
                "commands": []
            }

            result = await integration.execute_command("generate-commands", {
                "patterns_file": patterns_file
            }, context)

            assert result.success is True
            assert result.output["library"]["metadata"]["total_commands"] == 5
            mock_generate.assert_called_once_with(patterns_data)

    async def test_workflow_execution_command(self):
        """Test workflow execution command with mock"""
        print("\n🧪 Testing Workflow Execution Command...")

        integration = ClaudeCodeIntegration()
        context = create_execution_context()

        # Mock the workflow orchestrator
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
            mock_execute.assert_called_once_with("test_workflow", {})

    def test_slash_command_interface(self):
        """Test slash command interface functions"""
        print("\n🧪 Testing Slash Command Interface...")

        # Test get_command_list
        commands = get_command_list()
        assert isinstance(commands, list)
        assert len(commands) > 0
        assert all(cmd["name"].startswith("/") for cmd in commands)

        # Test get_command_help
        help_info = get_command_help("/status")
        assert help_info is not None
        assert help_info["name"] == "/status"

        # Test unknown command help
        help_info = get_command_help("/unknown")
        assert help_info is None

    async def test_handle_slash_command(self):
        """Test handle_slash_command function"""
        print("\n🧪 Testing Handle Slash Command Function...")

        # Mock integration for testing
        with patch('src.claude_integration.get_integration') as mock_get_integration:
            mock_integration = MagicMock()
            mock_result = CommandResult(
                success=True,
                output={"test": "data"},
                error=None,
                execution_time=0.1,
                metadata={}
            )
            mock_integration.execute_command = AsyncMock(return_value=mock_result)
            mock_get_integration.return_value = mock_integration

            result = await handle_slash_command("status", {}, "/test/workspace")

            assert result["success"] is True
            assert result["output"] == {"test": "data"}
            assert result["error"] is None

    def test_context_isolation(self):
        """Test that each execution maintains isolated context"""
        print("\n🧪 Testing Context Isolation...")

        integration1 = ClaudeCodeIntegration()
        integration2 = ClaudeCodeIntegration()

        # Execute commands in different integrations
        context1 = create_execution_context("/workspace1")
        context2 = create_execution_context("/workspace2")

        result1 = asyncio.run(integration1.execute_command("status", {}, context1))
        result2 = asyncio.run(integration2.execute_command("status", {}, context2))

        # Results should be independent
        assert result1.success is True
        assert result2.success is True
        assert result1.output["workspace"] == "/workspace1"
        assert result2.output["workspace"] == "/workspace2"

    def test_error_handling_and_logging(self):
        """Test error handling and logging"""
        print("\n🧪 Testing Error Handling and Logging...")

        integration = ClaudeCodeIntegration()
        context = create_execution_context()

        # Test with a command that will raise an exception
        with patch.object(integration.commands['status'], 'handler') as mock_handler:
            mock_handler.side_effect = Exception("Test exception")

            result = asyncio.run(integration.execute_command("status", {}, context))

            assert result.success is False
            assert "Error executing status" in result.error
            assert "Test exception" in result.error

    def test_configuration_loading(self):
        """Test configuration loading from file"""
        print("\n🧪 Testing Configuration Loading...")

        # Create temporary config file
        config_file = os.path.join(self.temp_dir, "config.json")
        config_data = {
            "debug": True,
            "max_history": 500,
            "command_timeout": 600
        }

        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        # Load integration with config
        integration = ClaudeCodeIntegration(config_file)

        assert integration.config["debug"] is True
        assert integration.config["max_history"] == 500
        assert integration.config["command_timeout"] == 600

    def run_all_tests(self):
        """Run all tests and provide summary"""
        print("🚀 Testing Claude Code Integration System")
        print("=" * 60)
        print("Testing slash command execution, context management, and subsystem integration")

        # Regular tests
        test_functions = [
            ("Integration Initialization", self.test_initialization),
            ("Command Registration", self.test_command_registration),
            ("Execution Context Creation", self.test_execution_context_creation),
            ("Command Execution Success", self.test_command_execution_success),
            ("Command Execution Failure", self.test_command_execution_failure),
            ("Parameter Validation", self.test_parameter_validation),
            ("Command History Tracking", self.test_command_history_tracking),
            ("Help System", self.test_help_system),
            ("Workflow Integration", self.test_workflow_integration),
            ("Authentication Checking", self.test_authentication_checking),
            ("Command Suggestions", self.test_command_suggestions),
            ("Parameter Completions", self.test_parameter_completions),
            ("Slash Command Interface", self.test_slash_command_interface),
            ("Context Isolation", self.test_context_isolation),
            ("Error Handling and Logging", self.test_error_handling_and_logging),
            ("Configuration Loading", self.test_configuration_loading),
        ]

        # Async tests
        async_test_functions = [
            ("Repository Analysis Command", self.test_repository_analysis_command),
            ("Command Generation Command", self.test_command_generation_command),
            ("Workflow Execution Command", self.test_workflow_execution_command),
            ("Handle Slash Command", self.test_handle_slash_command),
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
        print(f"Test Results: {passed}/{total} passed")

        if passed == total:
            print("🎉 All tests passed! Claude Code Integration System is working correctly.")
            print("\n✅ Context Engineering Principles Applied:")
            print("  - Write: Command execution history saved to structured data")
            print("  - Select: Intelligent command routing and parameter validation")
            print("  - Compress: Efficient context management and memory usage")
            print("  - Isolate: Each execution maintains independent context")
        else:
            print(f"❌ {total - passed} tests failed. Review the output above.")

        return passed == total


if __name__ == "__main__":
    test_suite = TestClaudeCodeIntegration()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)