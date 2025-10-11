#!/bin/bash
# Convert JSON slash commands to markdown format
set -euo pipefail

JSON_FILE=".claude/slash_commands.json"
COMMANDS_DIR=".claude/commands"

if [[ ! -f "$JSON_FILE" ]]; then
    echo "❌ JSON commands file not found"
    exit 1
fi

echo "🔄 Converting JSON commands to markdown..."

# Ensure commands directory exists
mkdir -p "$COMMANDS_DIR"

# Read JSON and convert each command
jq -r '.commands[] | @base64' "$JSON_FILE" | while read -r command; do
    _jq() {
        echo "${command}" | base64 -d | jq -r "${1}"
    }

    name=$(_jq '.name')
    description=$(_jq '.description')
    script=$(_jq '.script // empty')

    md_file="$COMMANDS_DIR/${name}.md"

    # Skip if markdown already exists
    if [[ -f "$md_file" ]]; then
        echo "⏭️  Skipping existing: $name"
        continue
    fi

    # Create markdown file
    if [[ -n "$script" && "$script" != "null" ]]; then
        cat > "$md_file" << EOF
---
description: "$description"
tools: ["Bash"]
---

$description

\`\`\`bash
./bin/$script "\$ARGUMENTS"
\`\`\`
EOF
    else
        cat > "$md_file" << EOF
---
description: "$description"
---

$description
EOF
    fi

    echo "✅ Created: $md_file"
done

echo "🎯 Conversion complete!"
echo "💡 Restart Claude Code to see new commands"
echo "🗑️  Consider removing $JSON_FILE after verification"