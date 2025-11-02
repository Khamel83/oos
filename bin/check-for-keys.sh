#!/usr/bin/env bash
set -euo pipefail

# Check for accidentally committed API keys
# This should be run as a pre-commit hook

echo "🔍 Scanning for accidentally committed API keys..."

# Define patterns for real API keys (excluding fake ones)
OPENROUTER_PATTERN='sk-or-v1-[A-Za-z0-9]{48}'
PERPLEXITY_PATTERN='pplx-[A-Za-z0-9]{40}'

# Files to check (exclude .env and fake patterns)
FILES_TO_CHECK=$(git ls-files | grep -E '\.(md|py|js|ts|json|yaml|yml|sh)$' | grep -v '.env')

FOUND_ISSUES=0

for file in $FILES_TO_CHECK; do
    if [[ -f "$file" ]]; then
        # Check for OpenRouter keys (excluding fake ones)
        if grep -q "$OPENROUTER_PATTERN" "$file" 2>/dev/null && ! grep -q "FAKE\|EXAMPLE\|DEMO" "$file" 2>/dev/null; then
            echo "❌ REAL OpenRouter API key found in: $file"
            FOUND_ISSUES=1
        fi

        # Check for Perplexity keys (excluding fake ones)
        if grep -q "$PERPLEXITY_PATTERN" "$file" 2>/dev/null && ! grep -q "FAKE\|EXAMPLE\|DEMO" "$file" 2>/dev/null; then
            echo "❌ REAL Perplexity API key found in: $file"
            FOUND_ISSUES=1
        fi
    fi
done

if [[ $FOUND_ISSUES -eq 1 ]]; then
    echo ""
    echo "❌ CRITICAL: Real API keys found in repository!"
    echo "   Remove them immediately and use environment variables instead."
    echo "   See docs/FAKE_API_KEYS.md for documentation examples."
    exit 1
else
    echo "✅ No real API keys found in repository"
    exit 0
fi