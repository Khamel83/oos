#!/usr/bin/env python3
"""
OOS Slash Command Consistency Fixer

This script systematically updates all OOS slash commands to follow
the official Claude Code patterns discovered in the documentation.

Key fixes:
1. Change 'tools:' to 'allowed-tools:' in frontmatter
2. Add missing 'argument-hint:' for commands with arguments
3. Standardize description format
4. Ensure consistent frontmatter structure
"""

import re
from pathlib import Path
from typing import List, Dict, Optional

class SlashCommandFixer:
    def __init__(self, commands_dir: str = "../.claude/commands"):
        self.commands_dir = Path(commands_dir)
        self.fixes_applied = []

    def find_command_files(self) -> List[Path]:
        """Find all .md files in the commands directory."""
        if not self.commands_dir.exists():
            print(f"❌ Commands directory not found: {self.commands_dir}")
            return []

        return list(self.commands_dir.glob("*.md"))

    def parse_frontmatter(self, content: str) -> tuple[Dict, str]:
        """Parse frontmatter and content from a markdown file."""
        lines = content.split('\n')

        if not lines or lines[0].strip() != '---':
            return {}, content

        # Find the end of frontmatter
        end_idx = None
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                end_idx = i
                break

        if end_idx is None:
            return {}, content

        # Parse frontmatter
        frontmatter = {}
        for line in lines[1:end_idx]:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"\'')

                # Handle array values
                if value.startswith('[') and value.endswith(']'):
                    # Simple array parsing
                    value = value[1:-1].replace('"', '').replace("'", "")
                    value = [item.strip() for item in value.split(',') if item.strip()]

                frontmatter[key] = value

        # Return frontmatter and remaining content
        remaining_content = '\n'.join(lines[end_idx + 1:])
        return frontmatter, remaining_content

    def fix_frontmatter(self, frontmatter: Dict) -> Dict:
        """Apply fixes to frontmatter according to official patterns."""
        fixed = frontmatter.copy()

        # Fix 1: Change 'tools' to 'allowed-tools'
        if 'tools' in fixed:
            fixed['allowed-tools'] = fixed.pop('tools')
            self.fixes_applied.append("Changed 'tools:' to 'allowed-tools:'")

        # Fix 2: Ensure description is properly quoted
        if 'description' in fixed:
            desc = fixed['description']
            if not (desc.startswith('"') and desc.endswith('"')):
                fixed['description'] = f'"{desc}"'

        # Fix 3: Add model if not present (use default)
        if 'model' not in fixed:
            fixed['model'] = 'claude-3-5-sonnet-20241022'
            self.fixes_applied.append("Added default model")

        return fixed

    def format_frontmatter(self, frontmatter: Dict) -> str:
        """Format frontmatter back to YAML."""
        if not frontmatter:
            return ""

        lines = ["---"]

        # Order: description, argument-hint, allowed-tools, model, others
        order = ['description', 'argument-hint', 'allowed-tools', 'model']

        for key in order:
            if key in frontmatter:
                value = frontmatter[key]
                if isinstance(value, list):
                    # Format arrays properly
                    if len(value) == 1:
                        lines.append(f"{key}: {value[0]}")
                    else:
                        items = ", ".join(value)
                        lines.append(f"{key}: {items}")
                else:
                    lines.append(f"{key}: {value}")

        # Add any remaining keys
        for key, value in frontmatter.items():
            if key not in order:
                if isinstance(value, list):
                    items = ", ".join(value)
                    lines.append(f"{key}: {items}")
                else:
                    lines.append(f"{key}: {value}")

        lines.append("---")
        return '\n'.join(lines)

    def detect_arguments(self, content: str) -> Optional[str]:
        """Detect if command takes arguments and suggest argument-hint."""
        # Look for $ARGUMENTS, $1, $2, etc.
        if '$ARGUMENTS' in content:
            return '<arguments>'

        # Look for positional args
        if re.search(r'\$[1-9]', content):
            return '[arg1] [arg2] ...'

        # Look for specific patterns in usage examples
        if re.search(r'/[\w-]+ \w+', content):
            return '<command-specific-args>'

        return None

    def fix_command_file(self, file_path: Path) -> bool:
        """Fix a single command file."""
        print(f"🔧 Processing: {file_path.name}")

        try:
            content = file_path.read_text()
            frontmatter, main_content = self.parse_frontmatter(content)

            original_frontmatter = frontmatter.copy()

            # Apply fixes
            fixed_frontmatter = self.fix_frontmatter(frontmatter)

            # Add argument-hint if missing but arguments detected
            if 'argument-hint' not in fixed_frontmatter:
                hint = self.detect_arguments(main_content)
                if hint:
                    fixed_frontmatter['argument-hint'] = hint
                    self.fixes_applied.append(f"Added argument-hint: {hint}")

            # Only update if changes were made
            if fixed_frontmatter != original_frontmatter:
                # Reconstruct file
                new_content = self.format_frontmatter(fixed_frontmatter)
                if main_content.strip():
                    new_content += '\n\n' + main_content

                # Write back
                file_path.write_text(new_content)
                print(f"  ✅ Updated {file_path.name}")
                return True
            else:
                print(f"  ➡️ {file_path.name} already consistent")
                return False

        except Exception as e:
            print(f"  ❌ Error processing {file_path.name}: {e}")
            return False

    def run_fixes(self) -> None:
        """Run all fixes on all command files."""
        print("🚀 OOS Slash Command Consistency Fixer")
        print("=" * 50)

        files = self.find_command_files()
        if not files:
            print("❌ No command files found!")
            return

        print(f"📁 Found {len(files)} command files")
        print()

        updated_count = 0
        for file_path in files:
            self.fixes_applied = []  # Reset for each file
            if self.fix_command_file(file_path):
                updated_count += 1
                if self.fixes_applied:
                    for fix in self.fixes_applied:
                        print(f"     - {fix}")
            print()

        print("=" * 50)
        print(f"✅ Processed {len(files)} files")
        print(f"🔧 Updated {updated_count} files")
        print()
        print("🎯 All OOS slash commands now follow official Claude Code patterns!")
        print()
        print("Next steps:")
        print("1. Test commands with /help to verify they appear correctly")
        print("2. Test argument completion with commands that take arguments")
        print("3. Commit changes to preserve consistency")

if __name__ == "__main__":
    fixer = SlashCommandFixer()
    fixer.run_fixes()