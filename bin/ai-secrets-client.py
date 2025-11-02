#!/usr/bin/env python3
"""
AI Agent Secrets Client
Simple, non-interactive secrets access for any AI agent
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

class AISecretsClient:
    """Simple secrets client for AI agents"""

    def __init__(self, env_file=None):
        """Initialize with path to .env file"""
        if env_file is None:
            # Try to find .env in common locations
            self.env_file = self._find_env_file()
        else:
            self.env_file = Path(env_file)

        self.loaded = False

    def _find_env_file(self):
        """Find .env file in project directory"""
        current_dir = Path.cwd()

        # Look up the directory tree for .env
        while current_dir != current_dir.parent:
            env_file = current_dir / '.env'
            if env_file.exists():
                return env_file
            current_dir = current_dir.parent

        # Try current directory as last resort
        if (Path.cwd() / '.env').exists():
            return Path.cwd() / '.env'

        raise FileNotFoundError("No .env file found in current directory or parent directories")

    def load_secrets(self):
        """Load secrets from .env file"""
        if not self.loaded:
            load_dotenv(self.env_file)
            self.loaded = True
            print(f"✅ Loaded secrets from {self.env_file}")

    def get_secret(self, key_name):
        """Get a specific secret value"""
        if not self.loaded:
            self.load_secrets()

        value = os.getenv(key_name)
        if value:
            # Return masked value for logging
            masked = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            print(f"🔑 Retrieved {key_name}: {masked}")
            return value
        else:
            print(f"❌ Secret not found: {key_name}")
            return None

    def list_secrets(self):
        """List all available secrets"""
        if not self.loaded:
            self.load_secrets()

        print("🔑 Available secrets:")
        for key, value in os.environ.items():
            if any(secret_type in key.upper() for secret_type in ['API', 'KEY', 'SECRET', 'TOKEN', 'PASSWORD']):
                masked = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
                print(f"  • {key}: {masked}")

    def test_access(self):
        """Test access to common secrets"""
        if not self.loaded:
            self.load_secrets()

        test_keys = ['OPENROUTER_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY']

        print("🧪 Testing secret access:")
        for key in test_keys:
            value = os.getenv(key)
            if value:
                print(f"  ✅ {key}: Available")
            else:
                print(f"  ❌ {key}: Not found")

    def create_env_backup(self):
        """Create a backup of the current .env file"""
        backup_path = self.env_file.with_suffix('.env.backup')

        if self.env_file.exists():
            import shutil
            shutil.copy2(self.env_file, backup_path)
            print(f"💾 Backup created: {backup_path}")
            return backup_path
        else:
            print("❌ No .env file to backup")
            return None

    def get_project_info(self):
        """Get project information from .env"""
        if not self.loaded:
            self.load_secrets()

        project_info = {
            'name': os.getenv('PROJECT_NAME', 'Unknown'),
            'description': os.getenv('PROJECT_DESCRIPTION', 'No description'),
            'env_file': str(self.env_file),
            'loaded_secrets': len([k for k in os.environ.keys()
                                 if any(secret_type in k.upper() for secret_type in ['API', 'KEY', 'SECRET', 'TOKEN'])])
        }

        print("📋 Project Information:")
        for key, value in project_info.items():
            print(f"  • {key}: {value}")

        return project_info


def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("AI Agent Secrets Client")
        print("")
        print("Usage: python ai-secrets-client.py <command> [options]")
        print("")
        print("Commands:")
        print("  get <key>     Get a specific secret value")
        print("  list          List all available secrets")
        print("  test          Test access to common secrets")
        print("  info          Show project information")
        print("  backup        Create backup of .env file")
        print("  help          Show this help")
        print("")
        print("Example:")
        print("  python ai-secrets-client.py get OPENROUTER_API_KEY")
        return

    try:
        client = AISecretsClient()
        command = sys.argv[1]

        if command == "get":
            if len(sys.argv) != 3:
                print("❌ Usage: get <key_name>")
                return
            key_name = sys.argv[2]
            value = client.get_secret(key_name)
            if value:
                print(value)

        elif command == "list":
            client.list_secrets()

        elif command == "test":
            client.test_access()

        elif command == "info":
            client.get_project_info()

        elif command == "backup":
            client.create_env_backup()

        elif command == "help":
            print("AI Agent Secrets Client Help")
            print("")
            print("This tool provides simple, non-interactive access to secrets stored in .env")
            print("Perfect for AI agents that need credentials without complex interfaces.")
            print("")
            print("Commands:")
            print("  get <key>     Get a specific secret value")
            print("  list          List all available secrets")
            print("  test          Test access to common secrets")
            print("  info          Show project information")
            print("  backup        Create backup of .env file")
            print("")

        else:
            print(f"❌ Unknown command: {command}")
            print("Run 'help' for available commands")

    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("Make sure you have a .env file in your project directory.")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()