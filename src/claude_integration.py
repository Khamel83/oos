#!/usr/bin/env python3
"""
Claude Code Integration Layer

Seamless integration with Claude Code interface for custom slash commands,
command execution, and system management.
"""

import json
import asyncio
import sys
import os
import uuid
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from datetime import datetime
import traceback

# Import our modules
from .repository_analyzer import RepositoryAnalyzer
from .command_generator import IdeaToCommandTransformer
from .orchestrator import WorkflowOrchestrator, create_default_workflows


class CommandType(Enum):
    """Types of commands supported by the integration"""
    SYSTEM = "system"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    ORCHESTRATION = "orchestration"
    UTILITY = "utility"


@dataclass
class CommandDefinition:
    """Definition of a custom slash command"""
    name: str
    description: str
    command_type: CommandType
    handler: Callable
    parameters: List[Dict[str, Any]]
    examples: List[str]
    category: str
    requires_auth: bool = False


@dataclass
class ExecutionContext:
    """Context for command execution"""
    user_id: Optional[str]
    session_id: str
    workspace_path: str
    command_history: List[Dict[str, Any]]
    environment: Dict[str, Any]
    timestamp: datetime


@dataclass
class CommandResult:
    """Result of command execution"""
    success: bool
    output: Any
    error: Optional[str]
    execution_time: float
    metadata: Dict[str, Any]


class ClaudeCodeIntegration:
    """Main integration class for Claude Code"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.commands = {}
        self.execution_contexts = {}
        self.command_history = []
        self.logger = self._setup_logger()

        # Initialize subsystems
        self.repository_analyzer = RepositoryAnalyzer()
        self.command_generator = IdeaToCommandTransformer()
        self.workflow_orchestrator = WorkflowOrchestrator()
        create_default_workflows(self.workflow_orchestrator)

        # Register commands
        self._register_commands()

    def _setup_logger(self) -> logging.Logger:
        """Setup logging for the integration"""
        logger = logging.getLogger('claude_integration')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            "debug": False,
            "max_history": 1000,
            "session_timeout": 3600,
            "command_timeout": 300,
            "enable_analytics": True,
            "workspace_root": os.getcwd()
        }

        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    default_config.update(config)
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")

        return default_config

    def _register_commands(self):
        """Register all available commands"""
        commands = [
            # Analysis commands
            CommandDefinition(
                name="analyze-repository",
                description="Analyze a GitHub repository for patterns",
                command_type=CommandType.ANALYSIS,
                handler=self._handle_analyze_repository,
                parameters=[
                    {"name": "repository_url", "type": "string", "required": True, "description": "GitHub repository URL"},
                    {"name": "output_file", "type": "string", "required": False, "description": "Output file path"}
                ],
                examples=[
                    "/analyze-repository https://github.com/user/repo",
                    "/analyze-repository https://github.com/user/repo --output-file analysis.json"
                ],
                category="Analysis",
                requires_auth=True
            ),

            # Generation commands
            CommandDefinition(
                name="generate-commands",
                description="Generate slash commands from repository analysis",
                command_type=CommandType.GENERATION,
                handler=self._handle_generate_commands,
                parameters=[
                    {"name": "patterns_file", "type": "string", "required": True, "description": "Patterns analysis file"},
                    {"name": "output_file", "type": "string", "required": False, "description": "Output commands file"}
                ],
                examples=[
                    "/generate-commands patterns.json",
                    "/generate-commands patterns.json --output-file commands.json"
                ],
                category="Generation"
            ),

            # Orchestration commands
            CommandDefinition(
                name="execute-workflow",
                description="Execute a predefined workflow",
                command_type=CommandType.ORCHESTRATION,
                handler=self._handle_execute_workflow,
                parameters=[
                    {"name": "workflow_id", "type": "string", "required": True, "description": "Workflow ID to execute"},
                    {"name": "variables", "type": "object", "required": False, "description": "Workflow variables as JSON"}
                ],
                examples=[
                    "/execute-workflow project_setup",
                    "/execute-workflow project_setup --variables '{\"project_name\": \"my-app\"}'"
                ],
                category="Orchestration"
            ),

            CommandDefinition(
                name="list-workflows",
                description="List available workflows",
                command_type=CommandType.ORCHESTRATION,
                handler=self._handle_list_workflows,
                parameters=[],
                examples=["/list-workflows"],
                category="Orchestration"
            ),

            # System commands
            CommandDefinition(
                name="status",
                description="Show system status and information",
                command_type=CommandType.SYSTEM,
                handler=self._handle_status,
                parameters=[],
                examples=["/status"],
                category="System"
            ),

            CommandDefinition(
                name="help",
                description="Show help information",
                command_type=CommandType.SYSTEM,
                handler=self._handle_help,
                parameters=[
                    {"name": "command", "type": "string", "required": False, "description": "Specific command to get help for"}
                ],
                examples=[
                    "/help",
                    "/help analyze-repository"
                ],
                category="System"
            ),

            # Utility commands
            CommandDefinition(
                name="history",
                description="Show command execution history",
                command_type=CommandType.UTILITY,
                handler=self._handle_history,
                parameters=[
                    {"name": "limit", "type": "integer", "required": False, "description": "Number of history entries to show"}
                ],
                examples=[
                    "/history",
                    "/history --limit 10"
                ],
                category="Utility"
            )
        ]

        for command in commands:
            self.commands[command.name] = command

    async def execute_command(self, command_name: str, parameters: Dict[str, Any],
                            context: ExecutionContext) -> CommandResult:
        """Execute a command with given parameters and context"""
        start_time = datetime.now()

        try:
            if command_name not in self.commands:
                return CommandResult(
                    success=False,
                    output=None,
                    error=f"Unknown command: {command_name}",
                    execution_time=0.0,
                    metadata={}
                )

            command = self.commands[command_name]

            # Check authentication if required
            if command.requires_auth and not self._check_auth(context):
                return CommandResult(
                    success=False,
                    output=None,
                    error="Authentication required",
                    execution_time=0.0,
                    metadata={}
                )

            # Execute command handler
            result = await command.handler(parameters, context)

            execution_time = (datetime.now() - start_time).total_seconds()

            # Create CommandResult
            command_result = CommandResult(
                success=True,
                output=result,
                error=None,
                execution_time=execution_time,
                metadata={"command_type": command.command_type.value}
            )

            # Record in history
            self._record_command(command_name, parameters, command_result, execution_time)

            return command_result

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Error executing {command_name}: {str(e)}"

            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())

            # Create CommandResult
            command_result = CommandResult(
                success=False,
                output=None,
                error=error_msg,
                execution_time=execution_time,
                metadata={}
            )

            # Record in history
            self._record_command(command_name, parameters, command_result, execution_time)

            return command_result

    def _check_auth(self, context: ExecutionContext) -> bool:
        """Check if user is authenticated"""
        # For now, we'll implement simple authentication checking
        # In a real implementation, this would check API keys, tokens, etc.
        return True

    def _record_command(self, command_name: str, parameters: Dict[str, Any],
                       result, execution_time: float):
        """Record command execution in history"""
        # Handle both CommandResult objects and dict results
        if hasattr(result, 'success'):
            success = result.success
        else:
            success = isinstance(result, dict) and result.get('success', False)

        history_entry = {
            "command": command_name,
            "parameters": parameters,
            "success": success,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        }

        self.command_history.append(history_entry)

        # Trim history if too long
        if len(self.command_history) > self.config["max_history"]:
            self.command_history = self.command_history[-self.config["max_history"]:]

    # Command handlers
    async def _handle_analyze_repository(self, params: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Handle repository analysis command"""
        repo_url = params.get("repository_url")
        output_file = params.get("output_file")

        if not repo_url:
            raise ValueError("Repository URL is required")

        # Analyze repository
        analysis = self.repository_analyzer.analyze_repository(repo_url)

        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(analysis, f, indent=2)

        return {
            "message": f"Repository analysis completed for {repo_url}",
            "analysis": analysis,
            "output_file": output_file
        }

    async def _handle_generate_commands(self, params: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Handle command generation"""
        patterns_file = params.get("patterns_file")
        output_file = params.get("output_file")

        if not patterns_file:
            raise ValueError("Patterns file is required")

        # Load patterns
        with open(patterns_file, 'r') as f:
            patterns_data = json.load(f)

        # Generate Claude Code compatible commands
        self.command_generator.generate_claude_code_commands(patterns_data)

        # Also generate library for backward compatibility
        library = self.command_generator.generate_command_library(patterns_data)

        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(library, f, indent=2)

        return {
            "message": f"Generated {library['metadata']['total_commands']} commands",
            "library": library,
            "output_file": output_file
        }

    async def _handle_execute_workflow(self, params: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Handle workflow execution"""
        workflow_id = params.get("workflow_id")
        variables = params.get("variables", {})

        if not workflow_id:
            raise ValueError("Workflow ID is required")

        # Execute workflow
        result = await self.workflow_orchestrator.execute_workflow(workflow_id, variables)

        return {
            "message": f"Workflow {workflow_id} executed",
            "result": result
        }

    async def _handle_list_workflows(self, params: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Handle workflow listing"""
        workflows = self.workflow_orchestrator.list_workflows()

        return {
            "workflows": workflows,
            "count": len(workflows)
        }

    async def _handle_status(self, params: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Handle status command"""
        status = {
            "system": "operational",
            "version": "1.0.0",
            "workspace": context.workspace_path,
            "commands_registered": len(self.commands),
            "workflows_available": len(self.workflow_orchestrator.workflows),
            "session_id": context.session_id,
            "uptime": "N/A"  # Could be calculated from start time
        }

        return status

    async def _handle_help(self, params: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Handle help command"""
        command_name = params.get("command")

        if command_name:
            if command_name in self.commands:
                cmd = self.commands[command_name]
                return {
                    "name": cmd.name,
                    "description": cmd.description,
                    "parameters": cmd.parameters,
                    "examples": cmd.examples,
                    "category": cmd.category
                }
            else:
                return {"error": f"Unknown command: {command_name}"}
        else:
            # Show all commands
            help_output = {}
            for category in set(cmd.category for cmd in self.commands.values()):
                category_commands = [
                    {
                        "name": cmd.name,
                        "description": cmd.description,
                        "examples": cmd.examples
                    }
                    for cmd in self.commands.values() if cmd.category == category
                ]
                help_output[category] = category_commands

            return help_output

    async def _handle_history(self, params: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Handle history command"""
        limit = params.get("limit", 10)

        history = self.command_history[-limit:] if self.command_history else []

        return {
            "history": history,
            "total_commands": len(self.command_history),
            "showing": len(history)
        }

    def get_command_suggestions(self, partial_command: str) -> List[Dict[str, Any]]:
        """Get command suggestions for partial input"""
        suggestions = []

        for cmd_name, cmd in self.commands.items():
            if cmd_name.startswith(partial_command):
                suggestions.append({
                    "name": cmd_name,
                    "description": cmd.description,
                    "parameters": [p["name"] for p in cmd.parameters if p.get("required")]
                })

        return suggestions

    def get_command_completions(self, command_name: str, partial_param: str) -> List[Dict[str, Any]]:
        """Get parameter completions for a command"""
        if command_name not in self.commands:
            return []

        command = self.commands[command_name]
        completions = []

        for param in command.parameters:
            if param["name"].startswith(partial_param):
                completions.append({
                    "name": param["name"],
                    "type": param["type"],
                    "description": param["description"],
                    "required": param.get("required", False)
                })

        return completions


# Claude Code interface functions
def create_execution_context(workspace_path: Optional[str] = None) -> ExecutionContext:
    """Create a new execution context"""
    return ExecutionContext(
        user_id=None,  # Would be populated from Claude Code
        session_id=str(uuid.uuid4()),
        workspace_path=workspace_path or os.getcwd(),
        command_history=[],
        environment=dict(os.environ),
        timestamp=datetime.now()
    )


# Global integration instance
_integration_instance = None


def get_integration() -> ClaudeCodeIntegration:
    """Get or create the global integration instance"""
    global _integration_instance
    if _integration_instance is None:
        _integration_instance = ClaudeCodeIntegration()
    return _integration_instance


# Claude Code slash command interface
async def handle_slash_command(command: str, parameters: Dict[str, Any],
                             workspace_path: Optional[str] = None) -> Dict[str, Any]:
    """Handle slash command execution from Claude Code"""
    integration = get_integration()
    context = create_execution_context(workspace_path)

    # Parse command (remove leading slash)
    command_name = command.lstrip('/')

    # Execute command
    result = await integration.execute_command(command_name, parameters, context)

    # Format result for Claude Code
    return {
        "success": result.success,
        "output": result.output,
        "error": result.error,
        "execution_time": result.execution_time,
        "metadata": result.metadata
    }


def get_command_list() -> List[Dict[str, Any]]:
    """Get list of available commands for Claude Code"""
    integration = get_integration()

    return [
        {
            "name": f"/{cmd.name}",
            "description": cmd.description,
            "category": cmd.category,
            "parameters": cmd.parameters,
            "examples": cmd.examples
        }
        for cmd in integration.commands.values()
    ]


def get_command_help(command_name: str) -> Optional[Dict[str, Any]]:
    """Get help for a specific command"""
    integration = get_integration()
    clean_name = command_name.lstrip('/')

    if clean_name in integration.commands:
        cmd = integration.commands[clean_name]
        return {
            "name": command_name,
            "description": cmd.description,
            "parameters": cmd.parameters,
            "examples": cmd.examples,
            "category": cmd.category
        }
    return None


# Main CLI interface for testing
async def main():
    """Main CLI interface for testing the integration"""
    import argparse

    parser = argparse.ArgumentParser(description='Claude Code Integration CLI')
    parser.add_argument('command', help='Command to execute')
    parser.add_argument('--params', '-p', help='Parameters as JSON string')
    parser.add_argument('--workspace', '-w', help='Workspace path')
    parser.add_argument('--list-commands', '-l', action='store_true', help='List available commands')

    args = parser.parse_args()

    if args.list_commands:
        commands = get_command_list()
        print("Available commands:")
        for cmd in commands:
            print(f"  {cmd['name']}: {cmd['description']}")
        return

    # Parse parameters
    params = json.loads(args.params) if args.params else {}

    # Execute command
    result = await handle_slash_command(args.command, params, args.workspace)

    # Print result
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    asyncio.run(main())