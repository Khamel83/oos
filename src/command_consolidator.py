#!/usr/bin/env python3
"""
OOS Command Consolidator

Creates unified commands that replace multiple single-purpose commands.
Designed for clear Archon MCP integration and reduced cognitive overhead.
"""

import os
import sys
from pathlib import Path

class CommandConsolidator:
    def __init__(self, commands_dir=".claude/commands"):
        self.commands_dir = Path(commands_dir)
        self.consolidated_commands = {
            "dev": {
                "description": "🔧 Complete development environment management",
                "subcommands": ["setup", "check", "modules", "refresh"],
                "consolidates": ["dev-setup", "startup-check", "modules", "reload-commands"],
                "script": "./bin/claude-dev.sh"
            },
            "test": {
                "description": "🧪 Testing and debugging utilities",
                "subcommands": ["debug", "connection", "scenarios", "all"],
                "consolidates": ["test-debug", "test-connection", "test-user-scenarios"],
                "script": "./bin/claude-test.sh"
            },
            "fix": {
                "description": "🔧 Code fixes and optimization",
                "subcommands": ["auto", "optimize", "docs", "all"],
                "consolidates": ["auto-fix", "optimize", "doc-check"],
                "script": "./bin/claude-fix.sh"
            },
            "think": {
                "description": "🧠 AI-powered problem solving and analysis",
                "subcommands": ["dump", "clarify", "solve", "meta"],
                "consolidates": ["brain-dump", "clarify", "solve", "meta-ai"],
                "script": "./bin/claude-think.sh"
            },
            "workflow": {
                "description": "🔄 Complete structured workflows",
                "subcommands": ["agentic", "complete", "idea-to-done"],
                "consolidates": ["agentic-workflow", "complete-workflow", "idea-to-done"],
                "script": "./bin/claude-workflow.sh"
            },
            "project": {
                "description": "🏗️ Project creation and management",
                "subcommands": ["create", "provision", "update"],
                "consolidates": ["create-project", "provision", "update-oos", "oos-refresh"],
                "script": "./bin/claude-project.sh"
            },
            "op": {
                "description": "🔐 1Password operations and authentication",
                "subcommands": ["signin", "status", "setup", "get", "secret", "session"],
                "consolidates": ["op-signin", "op-status", "op-setup", "op-get", "op-secret", "op-session", "op-session-automated"],
                "script": "./bin/claude-op.sh"
            },
            "archon": {
                "description": "📊 Archon knowledge base and project management",
                "subcommands": ["research", "status", "search"],
                "consolidates": ["archon-research", "archon-status"],
                "script": "./bin/claude-archon.sh",
                "mcp_tools": ["mcp__archon__rag_search_knowledge_base", "mcp__archon__find_projects", "mcp__archon__find_tasks"]
            },
            "task": {
                "description": "📋 Task management and execution",
                "subcommands": ["start", "complete", "list", "update"],
                "consolidates": ["archon-task-start", "archon-complete"],
                "script": "./bin/claude-task.sh",
                "mcp_tools": ["mcp__archon__manage_task", "mcp__archon__find_tasks"]
            },
            "check": {
                "description": "🔍 Comprehensive validation and security",
                "subcommands": ["security", "context", "all"],
                "consolidates": ["security-review", "context-stats"],
                "script": "./bin/claude-check.sh"
            }
        }

    def create_consolidated_command(self, name, config):
        """Create a new consolidated command file."""

        # Build allowed-tools list
        allowed_tools = ["Bash"]
        if "mcp_tools" in config:
            allowed_tools.extend(config["mcp_tools"])

        # Build argument hint
        subcommands = " | ".join(config["subcommands"])
        arg_hint = f"[{subcommands}] [additional-args]"

        # Create command content
        content = f"""---
description: "{config['description']}"
argument-hint: {arg_hint}
allowed-tools: {", ".join(allowed_tools)}
model: claude-3-5-sonnet-20241022
---

# /{name}

{config['description']}

Consolidates: {', '.join([f'/{cmd}' for cmd in config['consolidates']])}

## Usage

```bash
{config['script']} "$ARGUMENTS"
```

## Subcommands

{self._format_subcommands(config['subcommands'])}

## What It Does

This unified command replaces multiple single-purpose commands with a clean,
organized interface that reduces cognitive overhead while maintaining full functionality.

### Archon Integration
"""

        if "mcp_tools" in config:
            content += f"""
This command integrates with Archon MCP server using:
{self._format_mcp_tools(config['mcp_tools'])}
"""
        else:
            content += """
This command works independently but can be enhanced with Archon integration.
"""

        content += f"""
## Examples

```bash
/{name} {config['subcommands'][0]}
/{name} {config['subcommands'][1]} --verbose
/{name} help
```

## Migration Notes

This command replaces the following deprecated commands:
{self._format_deprecated_commands(config['consolidates'])}
"""

        return content

    def _format_subcommands(self, subcommands):
        """Format subcommands as bullet points."""
        return "\n".join([f"- `{cmd}` - {cmd.title()} operation" for cmd in subcommands])

    def _format_mcp_tools(self, tools):
        """Format MCP tools as bullet points."""
        return "\n".join([f"- `{tool}`" for tool in tools])

    def _format_deprecated_commands(self, commands):
        """Format deprecated commands as bullet points."""
        return "\n".join([f"- `/{cmd}` → Use appropriate subcommand instead" for cmd in commands])

    def create_all_consolidated_commands(self):
        """Create all consolidated command files."""
        print("🔧 Creating consolidated slash commands...")
        print(f"Target: Reduce from 45 to ~{len(self.consolidated_commands) + 10} commands")
        print()

        created_count = 0
        for name, config in self.consolidated_commands.items():
            print(f"📝 Creating /{name} (consolidates {len(config['consolidates'])} commands)")

            # Create command file
            command_file = self.commands_dir / f"{name}.md"
            content = self.create_consolidated_command(name, config)

            # Write file
            command_file.write_text(content)
            created_count += 1

            print(f"   ✅ {command_file}")
            for old_cmd in config['consolidates']:
                print(f"   📦 Consolidates: /{old_cmd}")
            print()

        print("=" * 60)
        print(f"✅ Created {created_count} consolidated commands")
        print(f"🎯 Reduced command count by ~{len([cmd for config in self.consolidated_commands.values() for cmd in config['consolidates']])} commands")
        print()
        print("📋 Essential commands to keep unchanged:")
        essential = [
            "start-coding", "morning", "evening", "do",
            "validate", "smart-commit", "ruat", "help-me", "screenshot"
        ]
        for cmd in essential:
            print(f"   ✅ /{cmd}")

        print()
        print("🔄 Next steps:")
        print("1. Test consolidated commands")
        print("2. Update documentation")
        print("3. Add deprecation warnings to old commands")
        print("4. Migrate users to new commands")
        print("5. Remove deprecated commands")

    def generate_migration_script(self):
        """Generate a script to help users migrate to new commands."""
        script_content = """#!/bin/bash
# OOS Command Migration Helper
# Helps users transition from old commands to new consolidated ones

echo "🔄 OOS Command Migration Guide"
echo "============================="
echo

declare -A migration_map=(
"""

        for config in self.consolidated_commands.values():
            for old_cmd in config['consolidates']:
                # Simple mapping - could be more sophisticated
                new_cmd = list(self.consolidated_commands.keys())[
                    list(self.consolidated_commands.values()).index(config)
                ]
                script_content += f'    ["{old_cmd}"]="Use /{new_cmd} instead"\n'

        script_content += """)

# Show migration suggestions
for old_cmd in "${!migration_map[@]}"; do
    echo "❌ /$old_cmd → ✅ ${migration_map[$old_cmd]}"
done

echo
echo "📚 See slash-command-analysis.md for complete migration guide"
"""

        migration_file = Path("bin/migrate-commands.sh")
        migration_file.write_text(script_content)
        migration_file.chmod(0o755)

        print(f"📜 Created migration script: {migration_file}")

if __name__ == "__main__":
    consolidator = CommandConsolidator()
    consolidator.create_all_consolidated_commands()
    consolidator.generate_migration_script()