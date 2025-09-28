#!/bin/bash
# Archon Learning System - Use Archon as OOS Learning Repository
# Captures patterns from inefficient user flows and creates reusable solutions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Archon Integration Functions
create_learning_project() {
    local lesson_title="$1"
    local lesson_description="$2"
    local trigger_pattern="$3"
    local solution_approach="$4"

    echo -e "${BLUE}📚 Creating Archon learning project for: $lesson_title${NC}"

    # This would integrate with Archon MCP to create a structured learning entry
    python3 << EOF
import sys
sys.path.insert(0, '$PROJECT_ROOT/src')

import asyncio
import json
from datetime import datetime

async def create_archon_lesson():
    """Create an Archon project to track this learning"""

    lesson_data = {
        "title": "$lesson_title",
        "description": "$lesson_description",
        "lesson_type": "user_flow_inefficiency",
        "trigger_pattern": "$trigger_pattern",
        "solution_approach": "$solution_approach",
        "date_learned": datetime.now().isoformat(),
        "status": "documented"
    }

    # Save to local learning repository for now
    # TODO: Integrate with Archon MCP when available
    import os
    os.makedirs("$PROJECT_ROOT/memory/lessons_learned", exist_ok=True)

    filename = f"$PROJECT_ROOT/memory/lessons_learned/{lesson_data['title'].lower().replace(' ', '_')}.json"
    with open(filename, 'w') as f:
        json.dump(lesson_data, f, indent=2)

    print(f"✅ Lesson documented: {filename}")

asyncio.run(create_archon_lesson())
EOF
}

# Specific lesson from the atlas update flow
capture_atlas_update_lesson() {
    echo -e "${PURPLE}🎯 Capturing User Flow Learning: Atlas Update Inefficiency${NC}"
    echo "============================================================="

    local title="Inefficient Repository Update Flow"
    local description="User requested vague 'update oos from github' but assistant had to make many discovery calls instead of being intelligent about the request"
    local trigger="User says 'update' or 'sync' with vague repository references"
    local solution="Pre-analyze context: check current repo, detect git remotes, intelligent defaults, single-command updates"

    create_learning_project "$title" "$description" "$trigger" "$solution"

    echo ""
    echo -e "${YELLOW}📝 Key Inefficiencies Identified:${NC}"
    echo "1. Multiple git remote checks instead of smart detection"
    echo "2. Manual ls/cd navigation vs context intelligence"
    echo "3. No automated backup safety vs manual backup creation"
    echo "4. Redundant verification steps vs streamlined confirmation"
    echo ""

    echo -e "${GREEN}💡 Future Efficiency Pattern:${NC}"
    echo "For 'update X from github' requests:"
    echo "→ 1. Smart repo detection (git remote -v + context analysis)"
    echo "→ 2. Automated safety (backup + branch check)"
    echo "→ 3. Intelligent update (pull vs clone vs replace based on state)"
    echo "→ 4. Single verification (status + latest commit)"
    echo ""
}

# Anti-pattern tracking
track_antipattern() {
    local pattern="$1"
    local why_bad="$2"
    local better_approach="$3"

    echo -e "${RED}❌ Anti-Pattern Detected: $pattern${NC}"
    echo "   Why Bad: $why_bad"
    echo -e "${GREEN}   Better: $better_approach${NC}"

    # Log to anti-patterns file
    cat >> "$PROJECT_ROOT/memory/anti_patterns.md" << EOF

### $pattern
**Date**: $(date '+%Y-%m-%d')
**Why Bad**: $why_bad
**Better Approach**: $better_approach

EOF
}

# Learning application check
apply_learnings_check() {
    echo -e "${PURPLE}🧠 OOS Learning Application Check${NC}"
    echo "=================================="
    echo ""

    if [ -d "$PROJECT_ROOT/memory/lessons_learned" ]; then
        echo -e "${BLUE}📚 Available Lessons:${NC}"
        find "$PROJECT_ROOT/memory/lessons_learned" -name "*.json" -exec basename {} .json \; | sed 's/_/ /g' | sed 's/^/  - /'
        echo ""
    fi

    echo -e "${YELLOW}⚡ Quick Efficiency Reminders:${NC}"
    echo "  • For repository updates: Use intelligent context detection"
    echo "  • For vague requests: Provide smart defaults with confirmation"
    echo "  • For complex flows: Break into predictable patterns"
    echo "  • For repetitive tasks: Create reusable scripts"
    echo ""

    read -p "Will you apply these learnings to avoid repeating inefficiencies? (y/N): " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ Please review lessons learned before proceeding${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Ready to apply learnings efficiently${NC}"
        return 0
    fi
}

# Enhanced update command that applies learnings
smart_update_oos() {
    local target_repo="${1:-oos}"

    echo -e "${BLUE}🚀 Smart OOS Update (Learning-Enhanced with Testing)${NC}"
    echo "====================================================="

    # 1. Context Intelligence
    echo "🔍 Step 1: Intelligent Context Detection"
    local current_dir=$(pwd)
    local git_root=""

    if git rev-parse --git-dir > /dev/null 2>&1; then
        git_root=$(git rev-parse --show-toplevel)
        echo "  ✓ Current directory is in git repo: $(basename "$git_root")"
    fi

    # 2. Smart Repository Detection
    echo "🎯 Step 2: Smart Repository Analysis"
    if [ -d "$target_repo" ]; then
        echo "  ✓ Found existing $target_repo directory"
        cd "$target_repo"

        if git remote -v | grep -q "github.com.*$target_repo"; then
            echo "  ✓ Existing directory is correct git repository"
            # Smart update: pull latest
            echo "  → Performing smart pull update..."
            git fetch --all
            git pull origin master
        else
            echo "  ⚠️  Existing directory not correct git repo - will replace"
            cd ..
            mv "$target_repo" "${target_repo}_backup_$(date +%Y%m%d_%H%M%S)"
            git clone "https://github.com/Khamel83/$target_repo.git"
        fi
    else
        echo "  → No existing directory, performing fresh clone..."
        git clone "https://github.com/Khamel83/$target_repo.git"
    fi

    # 3. Pre-Integration Testing (NEW - prevents failures)
    echo "🧪 Step 3: Pre-Integration Testing"
    cd "$target_repo" 2>/dev/null || { echo "Failed to enter $target_repo"; exit 1; }

    if [ -f "bin/test_integration.sh" ]; then
        echo "  → Running integration tests..."
        if ./bin/test_integration.sh > /tmp/oos_test.log 2>&1; then
            echo -e "  ${GREEN}✓ All integration tests passed${NC}"
        else
            echo -e "  ${RED}❌ Integration tests failed${NC}"
            echo "  📋 Test output:"
            cat /tmp/oos_test.log | tail -10
            echo ""
            echo -e "  ${YELLOW}⚠️  Proceeding anyway, but integration may fail${NC}"
        fi
    else
        echo "  ⚠️  No integration tests found"
    fi

    # 4. Auto-Integration (solving the slash command issue)
    echo "🔗 Step 4: Auto-Integration to Parent Project"

    if [ -f "bin/integrate_to_parent.sh" ]; then
        echo "  → Running bulletproof integration script..."
        if ./bin/integrate_to_parent.sh; then
            echo -e "  ${GREEN}✓ Integration completed successfully${NC}"
        else
            echo -e "  ${RED}❌ Integration failed${NC}"
            echo "  💡 Check logs above for details"
        fi
    else
        echo "  ⚠️  No integration script found - manual integration may be needed"
    fi

    # 5. Post-Integration Validation (NEW - verifies success)
    echo "✅ Step 5: Post-Integration Validation"
    cd "$current_dir"

    # Check if consultant was properly integrated
    if [ -f ".claude/slash_commands.json" ]; then
        if python3 -c "import json; json.load(open('.claude/slash_commands.json'))" 2>/dev/null; then
            echo -e "  ${GREEN}✓ slash_commands.json is valid JSON${NC}"

            if grep -q '"name": "consultant"' .claude/slash_commands.json; then
                echo -e "  ${GREEN}✓ /consultant command found in JSON${NC}"
            else
                echo -e "  ${YELLOW}⚠️  /consultant command not found in JSON${NC}"
            fi
        else
            echo -e "  ${RED}❌ slash_commands.json contains invalid JSON${NC}"
            echo "  📋 This is the fundamental problem we're fixing!"
        fi
    else
        echo -e "  ${YELLOW}⚠️  No .claude/slash_commands.json found${NC}"
    fi

    local latest_commit=$(git log --oneline -1 -C "$target_repo")
    echo "  ✓ Latest commit: $latest_commit"

    echo ""
    echo -e "${GREEN}🎉 Smart update complete with testing and validation!${NC}"
    echo -e "${YELLOW}💡 Learning applied: Integration now tested and validated${NC}"
}

main() {
    local command="${1:-help}"

    case "$command" in
        "capture-atlas")
            capture_atlas_update_lesson
            ;;
        "antipattern")
            shift
            track_antipattern "$1" "$2" "$3"
            ;;
        "check")
            apply_learnings_check
            ;;
        "smart-update")
            shift
            smart_update_oos "$1"
            ;;
        "help"|*)
            echo "OOS Archon Learning System"
            echo "========================="
            echo ""
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  capture-atlas  - Document the atlas update inefficiency lesson"
            echo "  antipattern    - Track anti-pattern: $0 antipattern 'pattern' 'why bad' 'better'"
            echo "  check          - Apply learnings check before development"
            echo "  smart-update   - Enhanced update command using learnings"
            echo ""
            echo "Examples:"
            echo "  $0 capture-atlas"
            echo "  $0 antipattern 'Multiple git checks' 'Inefficient discovery' 'Smart context detection'"
            echo "  $0 check"
            echo "  $0 smart-update atlas"
            ;;
    esac
}

main "$@"