#!/usr/bin/env bash
set -euo pipefail

# Bulletproof API Key Detection and Prevention
# This script prevents ANY meaningful API key from being committed to Git
# 
# Usage: 
#   ./bin/prevent_api_key_commits.sh --check-staged  # Check staged files
#   ./bin/prevent_api_key_commits.sh --check-all     # Check all tracked files
#   ./bin/prevent_api_key_commits.sh --install       # Install as pre-commit hook

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

error() { echo -e "${RED}[SECURITY BLOCK]${NC} $*" >&2; }
warn() { echo -e "${YELLOW}[WARNING]${NC} $*"; }
success() { echo -e "${GREEN}[PASS]${NC} $*"; }
info() { echo -e "${BLUE}[INFO]${NC} $*"; }

# Known safe/example API keys that are OK to commit
SAFE_KEYS=(
    "your_api_key_here"
    "your_openai_key_here"
    "your_context7_key_here"
    "sk-proj-example"
    "sk-test-example"
    "demo_key_12345"
    "example_key"
    "placeholder_key"
    "REPLACE_WITH_YOUR_KEY"
    "INSERT_YOUR_KEY_HERE"
    # URL patterns that are safe
    "https://"
    "http://"
    "dbreunig.com"
    "rlancemartin.github.io"
    "manus.im"
    "trychroma.com"
    "docs.google.com"
    "anthropic.com"
    "cognition.ai"
    "github.com"
    "langchain.com"
    "x.com"
    "youtube.com"
    "lexfridman.com"
    # Specific URLs from research
    "how-contexts-fail-and-how-to-fix-them.html"
    "why-the-term-context-engineering-matters.html"
    "context_engineering"
    "Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus"
    "16aaXLu40GugY-kOpqDU4e-S0hD1FmHcNyF0rRRnb1OU"
    "_generate_clarification_questions"
)

# Dangerous API key patterns - these should NEVER be committed
DANGEROUS_PATTERNS=(
    # OpenAI API keys (real ones start with sk- and are long)
    'sk-[A-Za-z0-9]{32,}'
    'sk-proj-[A-Za-z0-9_-]{32,}'
    
    # Anthropic Claude keys
    'sk-ant-[A-Za-z0-9_-]{95,}'
    
    # Google/Gemini API keys
    'AIza[A-Za-z0-9_-]{35}'
    
    # GitHub tokens
    'ghp_[A-Za-z0-9]{36}'
    'gho_[A-Za-z0-9]{36}'
    'ghu_[A-Za-z0-9]{36}'
    'ghs_[A-Za-z0-9]{36}'
    'ghr_[A-Za-z0-9]{36}'
    
    # AWS keys
    'AKIA[0-9A-Z]{16}'
    'ASIA[0-9A-Z]{16}'
    
    # Generic long keys that look real
    '[A-Za-z0-9+/]{40,}={0,2}'  # Base64-like strings 40+ chars
    '[A-Fa-f0-9]{64}'           # 64 char hex strings
    '[A-Za-z0-9_-]{32,128}'     # Long alphanumeric strings
)

# Check if a key looks like a safe placeholder
is_safe_key() {
    local key="$1"
    
    # Check against known safe patterns
    for safe in "${SAFE_KEYS[@]}"; do
        if [[ "$key" == "$safe" ]]; then
            return 0  # Safe
        fi
    done
    
    # Additional heuristics for safe keys
    if [[ "$key" =~ (example|placeholder|demo|test|fake|dummy|YOUR_KEY|REPLACE) ]]; then
        return 0  # Safe
    fi
    
    # If it's obviously too short to be a real API key
    if [[ ${#key} -lt 20 ]]; then
        return 0  # Safe
    fi
    
    return 1  # Potentially dangerous
}

# Scan a single file for API keys
scan_file() {
    local file="$1"
    local found_dangerous=0
    
    # Skip binary files
    if ! [[ -f "$file" && -r "$file" ]] || file "$file" | grep -q binary; then
        return 0
    fi
    
    # Skip files that are obviously safe
    case "$file" in
        *.png|*.jpg|*.jpeg|*.gif|*.pdf|*.zip|*.tar.gz|*.bin|*.exe) return 0 ;;
        *node_modules/*|*/.git/*|*/venv/*|*/__pycache__/*) return 0 ;;
    esac
    
    info "Scanning: $file"
    
    # Look for dangerous patterns
    for pattern in "${DANGEROUS_PATTERNS[@]}"; do
        while IFS=':' read -r line_num line_content; do
            if [[ -n "$line_content" ]]; then
                # Extract the potential key
                potential_key=$(echo "$line_content" | grep -oE "$pattern" | head -1)
                
                if [[ -n "$potential_key" ]] && ! is_safe_key "$potential_key"; then
                    error "🚨 DANGEROUS API KEY DETECTED!"
                    error "File: $file:$line_num"
                    error "Pattern: $pattern"
                    error "Key: ${potential_key:0:20}... [REDACTED]"
                    error "Line: $line_content"
                    echo
                    found_dangerous=1
                fi
            fi
        done < <(grep -n -E "$pattern" "$file" 2>/dev/null || true)
    done
    
    # Also look for suspicious variable assignments
    while IFS=':' read -r line_num line_content; do
        if [[ -n "$line_content" ]]; then
            # Extract the value after the equals sign
            potential_key=$(echo "$line_content" | sed -n 's/.*[Kk][Ee][Yy][^=]*=\s*["\047]\?\([^"'\'' ]*\)["\047]\?.*/\1/p')
            
            if [[ -n "$potential_key" ]] && [[ ${#potential_key} -ge 20 ]] && ! is_safe_key "$potential_key"; then
                error "🚨 SUSPICIOUS API KEY ASSIGNMENT!"
                error "File: $file:$line_num" 
                error "Key: ${potential_key:0:20}... [REDACTED]"
                error "Line: $line_content"
                echo
                found_dangerous=1
            fi
        fi
    done < <(grep -n -i -E '(api_?key|access_?key|secret_?key|auth_?key|token).*=' "$file" 2>/dev/null || true)
    
    return $found_dangerous
}

# Check staged files (for pre-commit hook)
check_staged() {
    info "Checking staged files for API keys..."
    local found_any=0
    
    # Get list of staged files
    while IFS= read -r file; do
        if [[ -n "$file" ]]; then
            if scan_file "$file"; then
                found_any=1
            fi
        fi
    done < <(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || true)
    
    return $found_any
}

# Check all tracked files
check_all() {
    info "Checking all tracked files for API keys..."
    local found_any=0
    
    while IFS= read -r file; do
        if [[ -n "$file" ]]; then
            if scan_file "$file"; then
                found_any=1
            fi
        fi
    done < <(git ls-files 2>/dev/null || find . -type f -name "*.sh" -o -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.md" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" | grep -v node_modules | head -100)
    
    return $found_any
}

# Install as pre-commit hook
install_hook() {
    local git_hooks_dir="$PROJECT_ROOT/.git/hooks"
    local pre_commit_hook="$git_hooks_dir/pre-commit"
    
    if [[ ! -d "$git_hooks_dir" ]]; then
        error "Not in a git repository or .git/hooks directory not found"
        return 1
    fi
    
    info "Installing pre-commit hook..."
    
    # Create or update pre-commit hook
    cat > "$pre_commit_hook" <<EOF
#!/usr/bin/env bash
# Auto-generated API Key Prevention Hook
# DO NOT EDIT - This file is managed by bin/prevent_api_key_commits.sh

echo "🔒 Scanning for API keys before commit..."

if ! "$PROJECT_ROOT/bin/prevent_api_key_commits.sh" --check-staged; then
    echo ""
    echo "❌ COMMIT BLOCKED - API KEYS DETECTED"
    echo ""
    echo "To fix this:"
    echo "1. Remove the API keys from your files"
    echo "2. Use environment variables or .env files (add to .gitignore)"
    echo "3. Use placeholder values like 'your_api_key_here'"
    echo ""
    echo "If you believe this is a false positive:"
    echo "1. Review the detected patterns carefully"
    echo "2. Add safe patterns to SAFE_KEYS in bin/prevent_api_key_commits.sh"
    echo "3. Re-run: git commit"
    echo ""
    exit 1
else
    echo "✅ No API keys detected - commit allowed"
fi
EOF
    
    chmod +x "$pre_commit_hook"
    success "Pre-commit hook installed at: $pre_commit_hook"
    
    # Test the hook
    info "Testing the hook..."
    if "$pre_commit_hook" >/dev/null 2>&1; then
        success "Hook test passed"
    else
        warn "Hook test had issues - check manually"
    fi
}

# Show help
show_help() {
    cat <<'EOF'
API Key Commit Prevention Tool

This tool prevents accidental commits of real API keys while allowing
safe placeholder values.

Usage:
  ./bin/prevent_api_key_commits.sh --check-staged   # Check staged files (for pre-commit)
  ./bin/prevent_api_key_commits.sh --check-all      # Check all tracked files  
  ./bin/prevent_api_key_commits.sh --install        # Install as pre-commit hook
  ./bin/prevent_api_key_commits.sh --help           # Show this help

Safe patterns (allowed):
  - your_api_key_here
  - sk-test-example  
  - example_key
  - placeholder_key
  - Any key containing: example, placeholder, demo, test, fake, dummy

Dangerous patterns (blocked):
  - sk-[real OpenAI keys]
  - ghp_[GitHub tokens]  
  - AIza[Google API keys]
  - Long base64 or hex strings
  - Any realistic-looking API key

Examples:
  ✅ OPENAI_API_KEY="your_api_key_here"           # Safe placeholder
  ✅ API_KEY="sk-test-example"                    # Obviously fake
  ❌ OPENAI_API_KEY="sk-proj-abc123def456..."     # Real OpenAI key (example)
  ❌ GITHUB_TOKEN="ghp_1234567890abcdef..."       # Real GitHub token

Security Philosophy:
  Better to block a legitimate placeholder than allow a real key.
  When in doubt, the tool blocks the commit.
EOF
}

# Main function
main() {
    case "${1:-help}" in
        --check-staged)
            if check_staged; then
                error "🚨 COMMIT BLOCKED - API keys found in staged files!"
                exit 1
            else
                success "✅ No API keys detected in staged files"
                exit 0
            fi
            ;;
        --check-all)
            if check_all; then
                error "🚨 API keys found in tracked files!"
                exit 1
            else
                success "✅ No API keys detected in tracked files"
                exit 0
            fi
            ;;
        --install)
            install_hook
            ;;
        --help|-h|help)
            show_help
            ;;
        *)
            error "Unknown option: ${1:-}"
            show_help
            exit 1
            ;;
    esac
}

main "$@"