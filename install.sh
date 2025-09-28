#!/bin/bash
# OOS Universal Installer - Works with any project
# Usage: curl -sSL install.oos.dev | bash
# Or: curl -sSL https://raw.githubusercontent.com/your-org/oos/main/install.sh | bash

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

TARGET_DIR=${OOS_INSTALL_DIR:-$(pwd)}
TEMP_DIR=$(mktemp -d)

echo -e "${CYAN}
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🚀 OOS Universal Installer                                ║
║   curl -sSL install.oos.dev | bash                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
${NC}"

echo -e "${BLUE}📦 Downloading OOS...${NC}"

# In production, download from GitHub
# For now, use local development version
OOS_SOURCE="/home/ubuntu/dev/oos"

if [[ ! -d "$OOS_SOURCE" ]]; then
    echo -e "${YELLOW}📥 Downloading from GitHub...${NC}"
    # git clone https://github.com/your-org/oos.git "$TEMP_DIR/oos"
    # OOS_SOURCE="$TEMP_DIR/oos"
    echo -e "${RED}❌ OOS source not found. This is a development version.${NC}"
    exit 1
fi

echo -e "${BLUE}🔍 Analyzing project: $TARGET_DIR${NC}"

# Smart project detection
detect_project() {
    local project_features=()

    [[ -f "package.json" ]] && project_features+=("Node.js")
    [[ -f "requirements.txt" || -f "pyproject.toml" || -f "setup.py" ]] && project_features+=("Python")
    [[ -f "Cargo.toml" ]] && project_features+=("Rust")
    [[ -f "go.mod" ]] && project_features+=("Go")
    [[ -f "composer.json" ]] && project_features+=("PHP")
    [[ -f "Gemfile" ]] && project_features+=("Ruby")
    [[ -f "pom.xml" ]] && project_features+=("Java/Maven")
    [[ -f "build.gradle" ]] && project_features+=("Java/Gradle")
    [[ -f "Dockerfile" ]] && project_features+=("Docker")
    [[ -d ".git" ]] && project_features+=("Git")
    [[ -d ".claude" ]] && project_features+=("Claude Code")

    echo "${project_features[@]}"
}

FEATURES=($(detect_project))

echo -e "${GREEN}📋 Detected:${NC}"
for feature in "${FEATURES[@]}"; do
    echo "   • $feature"
done
[[ ${#FEATURES[@]} -eq 0 ]] && echo "   • Generic project"
echo ""

# Install core components
echo -e "${BLUE}🔧 Installing OOS components...${NC}"

# Core structure (always)
mkdir -p .claude/{commands,constraints}
mkdir -p bin src config data

# Slash commands (always)
echo -e "${YELLOW}Installing slash commands...${NC}"
cp "$OOS_SOURCE/.claude/commands/"*.md .claude/commands/ 2>/dev/null || true
cp "$OOS_SOURCE/.claude/constraints/"*.md .claude/constraints/ 2>/dev/null || true

# Executable scripts (always)
echo -e "${YELLOW}Installing scripts...${NC}"
cp "$OOS_SOURCE/bin/"claude-*.sh bin/ 2>/dev/null || true
chmod +x bin/*.sh 2>/dev/null || true

# Python modules (if Python project or existing setup)
if [[ " ${FEATURES[*]} " =~ " Python " ]] || [[ " ${FEATURES[*]} " =~ " Claude Code " ]]; then
    echo -e "${YELLOW}Installing Python modules...${NC}"

    # Essential modules
    for module in oos_cli.py free_search_alternatives.py perplexity_usage_manager.py simple_command_handler.py capability_router.py knowledge_resolver.py renderers.py; do
        cp "$OOS_SOURCE/src/$module" src/ 2>/dev/null || true
    done

    # Command modules
    mkdir -p src/commands
    cp -r "$OOS_SOURCE/src/commands/"* src/commands/ 2>/dev/null || true
fi

# Config files
cp "$OOS_SOURCE/config/"*.yaml config/ 2>/dev/null || true

# Environment setup
if [[ ! -f ".env" ]]; then
    cat > .env << 'EOF'
# OOS Configuration - Add your API keys here
PERPLEXITY_API_KEY=
OPENROUTER_API_KEY=

# Cost Management
DAILY_COST_LIMIT=1.00
MONTHLY_COST_LIMIT=30.00
EOF
fi

# Universal OOS command (handle name conflicts)
OOS_COMMAND="oos"
if [[ -d "oos" ]]; then
    OOS_COMMAND="oos-cli"
    echo -e "${YELLOW}⚠️  Found existing 'oos' directory. Creating command as 'oos-cli'${NC}"
fi

cat > "$OOS_COMMAND" << 'EOF'
#!/usr/bin/env python3
"""Universal OOS command - works in any project"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def main():
    if len(sys.argv) < 2:
        print("🚀 OOS - Open Operating System")
        print("Usage:")
        print("  ./oos search \"query\"    - Search the web")
        print("  ./oos help              - Show help")
        print("")
        print("Slash commands (in Claude Code):")
        print("  /smart-commit           - Generate commit messages")
        print("  /optimize               - Optimize context")
        print("  /help-me                - Get help")
        return

    command = sys.argv[1]

    if command == "search":
        if len(sys.argv) < 3:
            print("Usage: ./oos search \"your query\"")
            return

        query = " ".join(sys.argv[2:])
        run_search(query)

    elif command == "help":
        show_help()

    else:
        print(f"Unknown command: {command}")
        print("Try: ./oos help")

def run_search(query):
    try:
        import asyncio
        from free_search_alternatives import search_free

        async def search():
            print(f"🔍 Searching for: {query}")
            results = await search_free(query, max_results=5)

            if results:
                print(f"✅ Found {len(results)} results\n")
                for i, result in enumerate(results, 1):
                    print(f"{i}. {result.title}")
                    print(f"   [{result.source}] {result.snippet[:100]}...")
                    if result.url:
                        print(f"   🔗 {result.url}")
                    print()
            else:
                print("❌ No results found")

        asyncio.run(search())

    except ImportError:
        print("❌ Search functionality requires Python modules")
        print("Run the installer again to add Python support")

def show_help():
    print("🚀 OOS - Open Operating System")
    print("")
    print("Commands:")
    print("  search \"query\"    - Search the web (free + Perplexity Pro)")
    print("  help              - Show this help")
    print("")
    print("Slash Commands (in Claude Code):")
    print("  /smart-commit     - Generate intelligent commit messages")
    print("  /optimize         - Optimize context for token efficiency")
    print("  /auto-fix         - Fix code consistency issues")
    print("  /help-me          - Smart context engineering help")
    print("  /clarify          - Clarify vague requests")
    print("  /workflow         - Start structured workflows")
    print("")
    print("Configuration:")
    print("  Edit .env file to add API keys")
    print("  Perplexity Pro gives you $5/month free credits")

if __name__ == "__main__":
    main()
EOF

chmod +x "$OOS_COMMAND"

# Success summary
echo -e "${GREEN}✅ OOS installed successfully!${NC}"
echo ""
echo -e "${CYAN}🎯 What you can do now:${NC}"
echo "   ./$OOS_COMMAND search \"python tutorials\""
echo "   ./$OOS_COMMAND help"
echo ""

if [[ " ${FEATURES[*]} " =~ " Claude Code " ]]; then
    echo -e "${CYAN}📱 In Claude Code:${NC}"
    echo "   /smart-commit"
    echo "   /optimize"
    echo "   /help-me"
    echo ""
fi

echo -e "${BLUE}⚙️  Next steps:${NC}"
echo "1. Add your Perplexity API key to .env (optional, for Pro search)"
echo "2. Try: ./$OOS_COMMAND search \"your favorite topic\""
echo ""
echo -e "${GREEN}🎉 OOS is ready to use in your project!${NC}"

# Cleanup
rm -rf "$TEMP_DIR" 2>/dev/null || true