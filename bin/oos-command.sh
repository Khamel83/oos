#!/usr/bin/env python3
"""
OOS Command Handler

Entry point for all OOS slash commands.
Handles both capability commands and traditional commands.
"""

import sys
import asyncio
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from simple_command_handler import SimpleCommandHandler

async def main():
    """Main command execution"""
    # Get command name and args
    if len(sys.argv) < 2:
        print("Usage: oos-command.sh <command> [args...]")
        print("Available commands: capabilities, actions, act, consultant, capability-help")
        return

    command_name = sys.argv[1]
    command_args = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""

    # Execute command
    handler = SimpleCommandHandler()
    result = await handler.execute_command(command_name, command_args)

    if "error" in result:
        print(f"Error: {result['error']}")
    elif "output" in result:
        print(result['output'])
    elif "command" in result:
        # For traditional commands, show execution info
        print(f"Command: {result['command']}")
        print(f"Description: {result['description']}")
        print(f"Execute: {result['execution']}")

if __name__ == "__main__":
    asyncio.run(main())