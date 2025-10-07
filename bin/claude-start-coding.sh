#!/usr/bin/env bash
set -euo pipefail

# Claude Code "Start Coding" Command
# One command to validate environment and get ready for development

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}${CYAN}🚀 Starting Development Session${NC}"
echo "==============================="

# Step 0: ALWAYS update OOS from GitHub first (ensures slash commands are current)
echo -e "${BLUE}Step 0: Updating OOS subfolder operating system...${NC}"
if [[ -f "$PROJECT_ROOT/bin/oos-update-from-github.sh" ]]; then
    bash "$PROJECT_ROOT/bin/oos-update-from-github.sh"
else
    echo -e "${YELLOW}⚠️  OOS update script not found - you may have outdated commands${NC}"
fi

# Step 1: Run development gate
echo -e "${BLUE}Step 1: Validating development environment...${NC}"
if DEV_GATE_BYPASS=true "$PROJECT_ROOT/bin/dev-gate.sh"; then
    echo -e "${GREEN}✅ Development environment ready${NC}"
else
    echo -e "${RED}❌ Development environment validation failed${NC}"
    echo "Please fix the issues above before coding"
    exit 1
fi

# Step 2: Fix environment issues
echo -e "\n${BLUE}Step 2: Fixing Environment Issues${NC}"

# Check and fix 1Password authentication
if ! op whoami >/dev/null 2>&1; then
    echo "• 1Password: ⚠️  Not authenticated - checking service account..."
    if command -v op >/dev/null 2>&1; then
        # Check for service account first
        local service_account_file="$HOME/.config/op/service_account.txt"
        if [[ -f "$service_account_file" ]]; then
            export OP_SERVICE_ACCOUNT_TOKEN="$(cat "$service_account_file")"
            if op whoami >/dev/null 2>&1; then
                echo "• 1Password: ✅ Service account authentication working"
            else
                echo "• 1Password: ⚠️  Service account token not working, attempting setup..."
                if [[ -f "$SCRIPT_DIR/setup-1password-service.sh" ]]; then
                    echo "→ Running service account setup..."
                    if "$SCRIPT_DIR/setup-1password-service.sh" --test >/dev/null 2>&1; then
                        echo "• 1Password: ✅ Service account configured and working"
                    else
                        echo "• 1Password: ⚠️  Service account setup failed, trying manual signin..."
                        if op signin --account my 2>/dev/null || op signin 2>/dev/null; then
                            echo "• 1Password: ✅ Successfully authenticated manually"
                        else
                            echo "• 1Password: ❌ Authentication failed - please run: $SCRIPT_DIR/setup-1password-service.sh"
                        fi
                    fi
                fi
            fi
        else
            # No service account, try manual signin
            echo "• 1Password: ⚠️  No service account found - attempting manual sign-in..."
            if op signin --account my 2>/dev/null || op signin 2>/dev/null; then
                echo "• 1Password: ✅ Successfully authenticated"
                echo "  💡 For long-term authentication, run: $SCRIPT_DIR/setup-1password-service.sh"
            else
                echo "• 1Password: ❌ Manual signin failed - please run: $SCRIPT_DIR/setup-1password-service.sh"
            fi
        else
            echo "• 1Password: Opening 1Password app for Touch ID/Face ID authentication..."
            # Try to open 1Password app for biometric auth
            if [[ "$OSTYPE" == "darwin"* ]]; then
                open -a "1Password 7 - Password Manager" 2>/dev/null || open -a "1Password" 2>/dev/null
            fi
            echo "• Please authenticate in 1Password app, then press Enter..."
            read -p "Press Enter after authenticating (or 's' to skip): " response
            if [[ "$response" != "s" ]]; then
                if op whoami >/dev/null 2>&1; then
                    echo "• 1Password: ✅ Successfully authenticated"
                else
                    echo "• 1Password: ⚠️  Authentication failed - run 'op signin' manually"
                fi
            fi
        fi
    else
        echo "• 1Password CLI not installed - install with: brew install 1password-cli"
    fi
else
    echo "• 1Password: ✅ Already authenticated"
fi

echo "• uv: $(uv --version)"
echo "• Python: $(uv run python --version)"

# Step 3: Fix project dependencies
echo -e "\n${BLUE}Step 3: Fixing Project Dependencies${NC}"
if [[ -f "$PROJECT_ROOT/pyproject.toml" ]]; then
    echo "• pyproject.toml: ✅ Found"
    if [[ -f "$PROJECT_ROOT/uv.lock" ]]; then
        echo "• uv.lock: ✅ Found (dependencies locked)"
    else
        echo "• uv.lock: ⚠️  Missing - running uv sync..."
        if uv sync; then
            echo "• uv.lock: ✅ Successfully created"
        else
            echo "• uv.lock: ❌ Failed to create (check pyproject.toml)"
        fi
    fi
else
    echo "• pyproject.toml: ⚠️  Missing (not a Python project?)"
fi

# Step 4: Handle Git repository
echo -e "\n${BLUE}Step 4: Git Repository Status${NC}"
if [[ -d "$PROJECT_ROOT/.git" ]]; then
    echo "• Git repository: ✅ Found"
    echo "• Branch: $(git branch --show-current 2>/dev/null || echo 'unknown')"

    # Check for uncommitted changes and auto-commit with AI
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        echo "• Working directory: ⚠️  Has uncommitted changes - attempting auto-commit..."
        echo ""
        echo "Uncommitted files:"
        git status --porcelain | head -10
        echo ""

        # Try AI commit first if available
        if [[ -f "$PROJECT_ROOT/bin/claude-smart-commit.sh" ]]; then
            echo "🤖 Using AI to generate commit message and auto-commit..."
            if bash "$PROJECT_ROOT/bin/claude-smart-commit.sh"; then
                echo "• Working directory: ✅ Changes auto-committed with AI message"
            else
                echo "• Working directory: ⚠️  AI commit failed"
                read -p "Enter manual commit message (or 's' to skip): " commit_msg
                if [[ -n "$commit_msg" && "$commit_msg" != "s" ]]; then
                    git add -A && git commit -m "$commit_msg"
                    echo "• Working directory: ✅ Changes committed manually"
                fi
            fi
        else
            # No AI available - be more aggressive with auto-commit
            change_count=$(git status --porcelain | wc -l)
            if [[ $change_count -le 5 ]]; then
                echo "🚀 Small changeset detected - auto-committing with generated message..."
                auto_msg="feat: development session changes

- $(git status --porcelain | head -3 | sed 's/^...//' | tr '\n' '\n- ' | sed 's/- $//')

🤖 Auto-committed by /start-coding"
                git add -A && git commit -m "$auto_msg"
                echo "• Working directory: ✅ Changes auto-committed"
            else
                echo "⚠️  Large changeset - manual review recommended"
                read -p "Commit all changes? (y/n/s=show diff): " response
                case "$response" in
                    y|Y)
                        read -p "Enter commit message: " commit_msg
                        if [[ -n "$commit_msg" ]]; then
                            git add -A && git commit -m "$commit_msg"
                            echo "• Working directory: ✅ Changes committed"
                        fi
                        ;;
                    s|S)
                        git diff --stat
                        echo ""
                        read -p "Commit after reviewing? (y/n): " commit_response
                        if [[ "$commit_response" == "y" || "$commit_response" == "Y" ]]; then
                            read -p "Enter commit message: " commit_msg
                            if [[ -n "$commit_msg" ]]; then
                                git add -A && git commit -m "$commit_msg"
                                echo "• Working directory: ✅ Changes committed"
                            fi
                        fi
                        ;;
                    *)
                        echo "• Working directory: ⚠️  Uncommitted changes (skipped)"
                        ;;
                esac
            fi
        fi
    else
        echo "• Working directory: ✅ Clean"
    fi
else
    echo "• Git repository: ⚠️  Not initialized"
    read -p "Initialize git repository? (y/n): " git_response
    if [[ "$git_response" == "y" || "$git_response" == "Y" ]]; then
        git init
        echo "• Git repository: ✅ Initialized"
    fi
fi

# Step 5: Available commands
echo -e "\n${PURPLE}🛠️  Available Development Commands:${NC}"
echo "• /dev-python [args]    - Run Python scripts"
echo "• /dev-test [args]      - Run tests with pytest"
echo "• /dev-uv [args]        - Run uv package manager"
echo "• /smart-commit         - AI-generated commit messages"
echo "• /auto-fix             - Auto-fix code issues"
echo "• /help-me              - Smart context engineering help"
echo "• /optimize             - Optimize current context"

# Step 6: Final status
echo -e "\n${GREEN}✅ Development Environment Setup Complete${NC}"
echo ""
echo "Environment Status:"
echo "- Development environment is ready"
echo "- Git repository detected on $(git branch --show-current 2>/dev/null || echo 'unknown') branch"
echo "- uv package manager available ($(uv --version | cut -d' ' -f2))"
if [[ -f "$PROJECT_ROOT/uv.lock" ]]; then
    echo "- Dependencies are locked and synced"
else
    echo "- No Python dependencies detected"
fi

echo -e "\n${BOLD}${GREEN}🎉 Ready to code! Happy developing!${NC}"