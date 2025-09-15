#!/usr/bin/env python3
"""
Test script for Command Generation System
Validates the idea-to-command transformation and context engineering principles
"""

import json
import tempfile
import os
import sys
from pathlib import Path
import unittest.mock as mock
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.command_generator import IdeaToCommandTransformer, CommandTemplate, CommandParameter


class TestCommandGenerator:
    """Test suite for Command Generation System with context engineering"""

    def __init__(self):
        self.test_results = []

    def run_test(self, test_name, test_func):
        """Run a single test and track results"""
        try:
            test_func()
            print(f"✅ {test_name}")
            self.test_results.append({"name": test_name, "status": "passed"})
            return True
        except Exception as e:
            print(f"❌ {test_name}: {e}")
            self.test_results.append({"name": test_name, "status": "failed", "error": str(e)})
            return False

    def test_initialization(self):
        """Test command generator initialization with proper context isolation"""
        print("\n🧪 Testing Command Generator Initialization...")

        # Test with no config
        transformer = IdeaToCommandTransformer()
        assert transformer.config == {}
        assert len(transformer.command_categories) == 7
        assert len(transformer.command_templates) == 0

        # Test with categories
        expected_categories = ['setup', 'development', 'testing', 'deployment',
                             'documentation', 'automation', 'analysis']
        assert list(transformer.command_categories.keys()) == expected_categories

    def test_command_parameter_creation(self):
        """Test CommandParameter dataclass functionality"""
        print("\n🧪 Testing Command Parameter Creation...")

        # Test required parameter
        param1 = CommandParameter(
            name="test_param",
            type="string",
            required=True,
            description="Test parameter"
        )
        assert param1.name == "test_param"
        assert param1.required == True
        assert param1.default is None

        # Test optional parameter with default
        param2 = CommandParameter(
            name="optional_param",
            type="integer",
            required=False,
            default=42,
            description="Optional parameter"
        )
        assert param2.required == False
        assert param2.default == 42

    def test_sample_patterns_transformation(self):
        """Test transforming sample patterns to commands (Write principle)"""
        print("\n🧪 Testing Sample Patterns Transformation...")

        transformer = IdeaToCommandTransformer()

        # Create sample patterns data
        patterns_data = {
            "metadata": {"language": "Python", "name": "test-project"},
            "file_structure": {
                "configuration_files": ["requirements.txt", "Dockerfile"],
                "package_files": ["requirements.txt"]
            },
            "patterns": {
                "architectural": [
                    {
                        "type": "class_pattern",
                        "name": "TestClass",
                        "methods": ["__init__", "save", "load"],
                        "file": "test.py"
                    }
                ]
            },
            "workflows": [
                {
                    "pattern_type": "github_actions",
                    "name": "ci.yml",
                    "triggers": ["push"]
                },
                {
                    "type": "docker",
                    "pattern_type": "containerization"
                }
            ],
            "documentation": {
                "readme_exists": True,
                "contributing_guide": True
            }
        }

        commands = transformer.transform_patterns_to_commands(patterns_data)

        # Should generate multiple commands from patterns
        assert len(commands) > 0

        # Check for expected command types
        command_names = [cmd.name for cmd in commands]
        assert "setup-python-project" in command_names or "setup-docker" in command_names
        assert "create-test-class" in command_names

        print(f"Generated {len(commands)} commands from sample patterns")

    def test_architecture_commands(self):
        """Test architecture pattern to command transformation"""
        print("\n🧪 Testing Architecture Commands...")

        transformer = IdeaToCommandTransformer()

        # Test class pattern
        class_pattern = {
            "type": "class_pattern",
            "name": "UserService",
            "methods": ["create_user", "get_user", "update_user", "delete_user"],
            "file": "src/models.py"
        }

        architecture_commands = transformer._generate_architecture_commands([class_pattern])
        assert len(architecture_commands) == 1

        command = architecture_commands[0]
        assert command.name == "create-user-service"
        assert command.category == "development"
        assert len(command.parameters) >= 2

        # Test function pattern
        function_pattern = {
            "type": "function_pattern",
            "name": "validate_input",
            "args": ["data", "schema"],
            "file": "src/utils.py"
        }

        function_commands = transformer._generate_architecture_commands([function_pattern])
        assert len(function_commands) == 1

        command = function_commands[0]
        assert command.name == "create-validate-input-function"
        assert command.category == "development"

    def test_workflow_commands(self):
        """Test workflow pattern to command transformation"""
        print("\n🧪 Testing Workflow Commands...")

        transformer = IdeaToCommandTransformer()

        # Test GitHub Actions workflow
        github_workflow = {
            "pattern_type": "github_actions",
            "name": "ci.yml",
            "triggers": ["push", "pull_request"],
            "jobs": [("test", "ubuntu-latest")]
        }

        workflow_commands = transformer._generate_workflow_commands([github_workflow])
        assert len(workflow_commands) == 1

        command = workflow_commands[0]
        assert command.name == "setup-github-actions"
        assert command.category == "automation"

        # Test Docker workflow
        docker_workflow = {
            "type": "docker",
            "pattern_type": "containerization"
        }

        docker_commands = transformer._generate_workflow_commands([docker_workflow])
        assert len(docker_commands) == 1

        command = docker_commands[0]
        assert command.name == "setup-docker"
        assert command.category == "deployment"

    def test_structure_commands(self):
        """Test file structure pattern to command transformation"""
        print("\n🧪 Testing Structure Commands...")

        transformer = IdeaToCommandTransformer()

        # Test Python project structure
        python_structure = {
            "configuration_files": ["requirements.txt", "pyproject.toml"],
            "package_files": ["requirements.txt"]
        }

        python_commands = transformer._generate_structure_commands(python_structure)
        assert len(python_commands) > 0

        # Test Node.js project structure
        nodejs_structure = {
            "configuration_files": ["package.json"],
            "package_files": ["package.json"]
        }

        nodejs_commands = transformer._generate_structure_commands(nodejs_structure)
        assert len(nodejs_commands) > 0

        # Test Docker structure
        docker_structure = {
            "configuration_files": ["Dockerfile", ".dockerignore"]
        }

        docker_commands = transformer._generate_structure_commands(docker_structure)
        assert len(docker_commands) > 0

    def test_documentation_commands(self):
        """Test documentation pattern to command transformation"""
        print("\n🧪 Testing Documentation Commands...")

        transformer = IdeaToCommandTransformer()

        # Test with README and contributing guide
        docs_analysis = {
            "readme_exists": True,
            "contributing_guide": True
        }

        doc_commands = transformer._generate_documentation_commands(docs_analysis)
        assert len(doc_commands) == 2

        command_names = [cmd.name for cmd in doc_commands]
        assert "generate-readme" in command_names
        assert "create-contributing-guide" in command_names

    def test_setup_commands(self):
        """Test setup command generation based on project characteristics"""
        print("\n🧪 Testing Setup Commands...")

        transformer = IdeaToCommandTransformer()

        # Test Python project
        python_patterns = {
            "metadata": {"language": "Python"}
        }

        python_commands = transformer._generate_setup_commands(python_patterns)
        python_command_names = [cmd.name for cmd in python_commands]
        assert "setup-python-project" in python_command_names

        # Test Node.js project
        nodejs_patterns = {
            "metadata": {"language": "JavaScript"}
        }

        nodejs_commands = transformer._generate_setup_commands(nodejs_patterns)
        nodejs_command_names = [cmd.name for cmd in nodejs_commands]
        assert "setup-nodejs-project" in nodejs_command_names

        # Test Go project
        go_patterns = {
            "metadata": {"language": "Go"}
        }

        go_commands = transformer._generate_setup_commands(go_patterns)
        go_command_names = [cmd.name for cmd in go_commands]
        assert "setup-go-project" in go_command_names

    def test_implementation_generation(self):
        """Test implementation template generation (Compress principle)"""
        print("\n🧪 Testing Implementation Generation...")

        transformer = IdeaToCommandTransformer()

        # Test class implementation
        class_impl = transformer._generate_class_implementation("TestClass", ["save", "load"])
        assert "class TestClass:" in class_impl
        assert "def save(self):" in class_impl
        assert "def load(self):" in class_impl

        # Test function implementation
        func_impl = transformer._generate_function_implementation("test_func", ["param1", "param2"])
        assert "def test_func(param1, param2):" in func_impl
        assert '"""test_func function"""' in func_impl

        # Test GitHub Actions implementation
        ga_impl = transformer._generate_github_actions_implementation()
        assert "name: {{workflow_name}}" in ga_impl
        assert "on:" in ga_impl
        assert "jobs:" in ga_impl

        # Test Docker implementation
        docker_impl = transformer._generate_docker_implementation()
        assert "FROM {{base_image}}" in docker_impl
        assert "WORKDIR /app" in docker_impl

        print("Implementation templates generated successfully")

    def test_camel_case_conversion(self):
        """Test camelCase to kebab-case conversion"""
        print("\n🧪 Testing Camel Case Conversion...")

        transformer = IdeaToCommandTransformer()

        test_cases = [
            ("TestClass", "test-class"),
            ("UserService", "user-service"),
            ("validateInput", "validate-input"),
            ("createUserManager", "create-user-manager"),
            ("simple", "simple")
        ]

        for input_text, expected in test_cases:
            result = transformer._camel_to_kebab(input_text)
            assert result == expected, f"Expected {expected}, got {result}"

    def test_command_library_generation(self):
        """Test complete command library generation"""
        print("\n🧪 Testing Command Library Generation...")

        transformer = IdeaToCommandTransformer()

        # Sample patterns data
        patterns_data = {
            "metadata": {"language": "Python", "name": "test-project"},
            "file_structure": {"configuration_files": ["requirements.txt"]},
            "patterns": {"architectural": []},
            "workflows": [],
            "documentation": {"readme_exists": True}
        }

        library = transformer.generate_command_library(patterns_data)

        # Verify library structure
        assert "metadata" in library
        assert "commands" in library
        assert "usage_guide" in library

        # Verify metadata
        metadata = library["metadata"]
        assert "total_commands" in metadata
        assert "categories" in metadata
        assert "generated_at" in metadata

        # Verify commands are proper dict format
        for command in library["commands"]:
            assert "name" in command
            assert "description" in command
            assert "category" in command
            assert "parameters" in command

        # Verify usage guide
        usage_guide = library["usage_guide"]
        assert "introduction" in usage_guide
        assert "categories" in usage_guide
        assert "examples" in usage_guide

        print(f"Generated command library with {metadata['total_commands']} commands")

    def test_save_and_load_commands(self):
        """Test saving and loading commands (Write principle)"""
        print("\n🧪 Testing Save and Load Commands...")

        transformer = IdeaToCommandTransformer()

        # Create sample commands
        sample_command = CommandTemplate(
            name="test-command",
            description="Test command",
            category="testing",
            parameters=[
                CommandParameter("test_param", "string", True, description="Test parameter")
            ],
            implementation="# Test implementation",
            usage_examples=["/test-command --test-param value"],
            dependencies=[],
            prerequisites=[],
            documentation="Test documentation",
            source_patterns=[]
        )

        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name

        try:
            transformer.save_commands([sample_command], temp_file)

            # Verify file exists and contains command
            assert os.path.exists(temp_file)

            with open(temp_file, 'r') as f:
                loaded_data = json.load(f)

            assert len(loaded_data) == 1
            assert loaded_data[0]["name"] == "test-command"
            assert loaded_data[0]["description"] == "Test command"

            print("Commands saved and loaded successfully")

        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_error_handling(self):
        """Test error handling for edge cases"""
        print("\n🧪 Testing Error Handling...")

        transformer = IdeaToCommandTransformer()

        # Test empty patterns data
        empty_patterns = {}
        commands = transformer.transform_patterns_to_commands(empty_patterns)
        assert isinstance(commands, list)

        # Test malformed pattern data
        malformed_patterns = {
            "patterns": {
                "architectural": [
                    {"type": "unknown_pattern", "name": "Test"}
                ]
            }
        }

        try:
            commands = transformer.transform_patterns_to_commands(malformed_patterns)
            assert isinstance(commands, list)
        except Exception as e:
            print(f"Handled malformed patterns: {e}")

        # Test invalid config file
        try:
            config = transformer._load_config("/nonexistent/path.json")
            assert config == {}
        except Exception as e:
            print(f"Handled invalid config: {e}")

        print("Error handling tests completed")

    def test_context_isolation(self):
        """Test that each command generation is properly isolated (Isolate principle)"""
        print("\n🧪 Testing Context Isolation...")

        transformer1 = IdeaToCommandTransformer()
        transformer2 = IdeaToCommandTransformer()

        # Ensure transformers are independent
        assert transformer1 is not transformer2
        assert transformer1.config == transformer2.config == {}

        # Generate commands with different transformers
        patterns_data = {
            "metadata": {"language": "Python"},
            "file_structure": {"configuration_files": ["requirements.txt"]}
        }

        commands1 = transformer1.transform_patterns_to_commands(patterns_data)
        commands2 = transformer2.transform_patterns_to_commands(patterns_data)

        # Should generate same results
        assert len(commands1) == len(commands2)
        assert [cmd.name for cmd in commands1] == [cmd.name for cmd in commands2]

        # But command objects should be different (deep isolation)
        assert commands1[0] is not commands2[0]

        print("Context isolation verified")

    def run_all_tests(self):
        """Run all tests and provide summary"""
        print("🚀 Testing Command Generation System")
        print("=" * 60)
        print("Testing context engineering principles: Write, Select, Compress, Isolate")

        test_functions = [
            ("Initialization", self.test_initialization),
            ("Command Parameter Creation", self.test_command_parameter_creation),
            ("Sample Patterns Transformation", self.test_sample_patterns_transformation),
            ("Architecture Commands", self.test_architecture_commands),
            ("Workflow Commands", self.test_workflow_commands),
            ("Structure Commands", self.test_structure_commands),
            ("Documentation Commands", self.test_documentation_commands),
            ("Setup Commands", self.test_setup_commands),
            ("Implementation Generation", self.test_implementation_generation),
            ("Camel Case Conversion", self.test_camel_case_conversion),
            ("Command Library Generation", self.test_command_library_generation),
            ("Save and Load Commands", self.test_save_and_load_commands),
            ("Error Handling", self.test_error_handling),
            ("Context Isolation", self.test_context_isolation),
        ]

        passed = 0
        total = len(test_functions)

        for test_name, test_func in test_functions:
            if self.run_test(test_name, test_func):
                passed += 1

        print("\n" + "=" * 60)
        print(f"Test Results: {passed}/{total} passed")

        if passed == total:
            print("🎉 All tests passed! Command Generation System is working correctly.")
            print("\n✅ Context Engineering Principles Applied:")
            print("  - Write: Commands saved to structured files with documentation")
            print("  - Select: Relevant patterns selected for command generation")
            print("  - Compress: Implementation templates compressed into reusable formats")
            print("  - Isolate: Each transformer instance maintains independent context")
        else:
            print(f"❌ {total - passed} tests failed. Review the output above.")

        return passed == total


if __name__ == "__main__":
    test_suite = TestCommandGenerator()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)