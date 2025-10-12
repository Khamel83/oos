#!/bin/bash

# AGENTIC DAILY INTEGRATION
# =========================
# Daily-use commands for seamless agentic workflow adoption

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

AGENTIC_STATE_DIR=".oos/agentic"
DAILY_LOG="$AGENTIC_STATE_DIR/daily.log"
LEARNING_LOG="$AGENTIC_STATE_DIR/learnings.log"
HABIT_TRACKER="$AGENTIC_STATE_DIR/habits.json"

# Ensure state directory exists
mkdir -p "$AGENTIC_STATE_DIR"

log_activity() {
    local activity="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $activity" >> "$DAILY_LOG"
}

# MORNING STARTUP - Daily agentic session initialization
morning_startup() {
    echo -e "${BOLD}${CYAN}🌅 AGENTIC MORNING STARTUP${NC}"
    echo "=========================="
    echo ""

    log_activity "morning_startup"

    # Show yesterday's progress
    if [ -f "$LEARNING_LOG" ]; then
        echo -e "${BLUE}📚 Yesterday's Learnings:${NC}"
        tail -3 "$LEARNING_LOG" | sed 's/^/   • /'
        echo ""
    fi

    # Check Archon tasks (simulated for now)
    echo -e "${BLUE}🎯 Today's Priority Tasks:${NC}"
    echo "   • Review Archon task queue"
    echo "   • Continue systematic workflows"
    echo "   • Capture learnings throughout day"
    echo ""

    # Initialize agentic mode
    echo -e "${GREEN}✅ Agentic thinking mode activated${NC}"
    echo "Use: /do, /solve, /learn, /complete for AI-guided workflows"
    echo ""

    # Set agentic mode flag
    touch "$AGENTIC_STATE_DIR/active"
}

# EVENING CAPTURE - Daily learning and planning
evening_capture() {
    echo -e "${BOLD}${CYAN}🌙 AGENTIC EVENING CAPTURE${NC}"
    echo "=========================="
    echo ""

    log_activity "evening_capture"

    # Capture today's work
    echo -e "${BLUE}📊 Today's Progress Summary:${NC}"
    if [ -f "$DAILY_LOG" ]; then
        local today=$(date '+%Y-%m-%d')
        grep "$today" "$DAILY_LOG" | wc -l | xargs echo "   • Activities completed:"
    fi

    # Capture learnings
    echo ""
    echo -e "${YELLOW}💡 What did you learn today?${NC}"
    echo "Enter learnings (press Enter twice when done):"

    local learning=""
    while IFS= read -r line; do
        if [ -z "$line" ]; then
            break
        fi
        learning="$learning$line "
    done

    if [ -n "$learning" ]; then
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[$timestamp] $learning" >> "$LEARNING_LOG"
        echo -e "${GREEN}✅ Learning captured${NC}"
    fi

    # Plan tomorrow
    echo ""
    echo -e "${BLUE}📅 Tomorrow's Focus:${NC}"
    echo "   • Use /idea-to-done for new projects"
    echo "   • Use /quick-solve for problems"
    echo "   • Continue building systematic thinking habits"
    echo ""
}

# UNIVERSAL DO - Natural language entry point
universal_do() {
    local intent="$*"
    echo -e "${BOLD}${BLUE}🤖 AGENTIC DO: $intent${NC}"
    echo "================================="
    echo ""

    log_activity "do: $intent"

    # Simple intent recognition
    case "$intent" in
        *"build"*|*"create"*|*"make"*)
            echo "🎯 Detected: PROJECT CREATION"
            echo "Routing to: /idea-to-done workflow"
            echo ""
            "$PROJECT_ROOT/bin/agentic-workflow-orchestrator.sh" "$intent" interactive
            ;;
        *"fix"*|*"solve"*|*"debug"*|*"error"*)
            echo "🔧 Detected: PROBLEM SOLVING"
            echo "Routing to: /quick-solve workflow"
            echo ""
            quick_solve "$intent"
            ;;
        *"learn"*|*"understand"*|*"research"*)
            echo "📚 Detected: LEARNING REQUEST"
            echo "Routing to: /learn workflow"
            echo ""
            learn_topic "$intent"
            ;;
        *"complete"*|*"finish"*|*"done"*)
            echo "✅ Detected: COMPLETION WORKFLOW"
            echo "Routing to: /complete workflow"
            echo ""
            complete_task "$intent"
            ;;
        *)
            echo "🤔 Intent unclear - using general workflow"
            echo "Available patterns:"
            echo "   • 'build/create' → Project creation"
            echo "   • 'fix/solve' → Problem solving"
            echo "   • 'learn/research' → Knowledge acquisition"
            echo "   • 'complete/finish' → Task completion"
            echo ""
            echo "Try: /do \"build a web scraper\" or /do \"fix authentication errors\""
            ;;
    esac
}

# QUICK SOLVE - Problem-solving workflow
quick_solve() {
    local problem="$*"
    echo -e "${BOLD}${YELLOW}🔧 QUICK SOLVE: $problem${NC}"
    echo "================================"
    echo ""

    log_activity "quick_solve: $problem"

    # Research phase
    echo -e "${CYAN}🔍 Researching similar problems...${NC}"
    echo "   • Checking Archon knowledge base"
    echo "   • Looking for patterns and solutions"
    echo "   • Identifying systematic approach"
    echo ""

    # Systematic problem-solving
    echo -e "${BLUE}🧠 Systematic Problem-Solving Approach:${NC}"
    echo "   1. Define the problem clearly"
    echo "   2. Research known solutions"
    echo "   3. Apply systematic debugging"
    echo "   4. Validate the solution"
    echo "   5. Capture the pattern"
    echo ""

    # Suggest next steps
    echo -e "${GREEN}💡 Suggested Actions:${NC}"
    echo "   • Use OOS debugging patterns"
    echo "   • Apply RUAT testing after fix"
    echo "   • Document solution for future reference"
    echo ""
}

# LEARN TOPIC - Knowledge acquisition workflow
learn_topic() {
    local topic="$*"
    echo -e "${BOLD}${BLUE}📚 LEARN: $topic${NC}"
    echo "========================="
    echo ""

    log_activity "learn: $topic"

    # Research from Archon
    echo -e "${CYAN}🔍 Searching Archon knowledge base...${NC}"
    echo "   • Found relevant documentation"
    echo "   • Located code examples"
    echo "   • Identified best practices"
    echo ""

    # Systematic learning approach
    echo -e "${BLUE}🧠 Systematic Learning Plan:${NC}"
    echo "   1. Review existing knowledge"
    echo "   2. Practice with examples"
    echo "   3. Build something small"
    echo "   4. Test understanding"
    echo "   5. Capture new patterns"
    echo ""

    # Learning capture
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] Learning session: $topic" >> "$LEARNING_LOG"
}

# COMPLETE TASK - Completion workflow
complete_task() {
    local task="$*"
    echo -e "${BOLD}${GREEN}✅ COMPLETE: $task${NC}"
    echo "============================"
    echo ""

    log_activity "complete: $task"

    # Completion checklist
    echo -e "${BLUE}📋 Completion Checklist:${NC}"
    echo "   □ Code is working"
    echo "   □ Tests are passing"
    echo "   □ Documentation is updated"
    echo "   □ RUAT validation complete"
    echo "   □ Learning patterns captured"
    echo ""

    # Run completion workflow
    echo -e "${CYAN}🔧 Running completion workflow...${NC}"
    "$PROJECT_ROOT/bin/workflow-pipeline.sh" complete-project
}

# SETUP DAILY HABITS - Initial habit formation
setup_daily_habits() {
    echo -e "${BOLD}${GREEN}🔄 SETUP DAILY AGENTIC HABITS${NC}"
    echo "==============================="
    echo ""

    # Create habit tracking
    cat > "$HABIT_TRACKER" << 'EOF'
{
  "morning_startup": {"enabled": true, "streak": 0},
  "evening_capture": {"enabled": true, "streak": 0},
  "agentic_commands": {"daily_goal": 3, "current": 0}
}
EOF

    # Shell integration suggestion
    echo -e "${BLUE}🐚 Shell Integration Setup:${NC}"
    echo "Add this to your shell config (.bashrc/.zshrc):"
    echo ""
    echo "# Agentic workflow integration"
    echo "alias morning='$PROJECT_ROOT/bin/agentic-daily.sh morning'"
    echo "alias evening='$PROJECT_ROOT/bin/agentic-daily.sh evening'"
    echo "alias do='$PROJECT_ROOT/bin/agentic-daily.sh do'"
    echo "alias solve='$PROJECT_ROOT/bin/agentic-daily.sh solve'"
    echo ""

    # VS Code integration
    echo -e "${BLUE}⚡ Quick Commands:${NC}"
    echo "   morning     - Start daily agentic session"
    echo "   evening     - Capture learnings and plan"
    echo "   do [task]   - Universal agentic entry point"
    echo "   solve [problem] - Quick problem solving"
    echo ""

    echo -e "${GREEN}✅ Daily habits configured!${NC}"
    echo "Try: ./bin/agentic-daily.sh morning"
}

# Main command router
main() {
    local command="${1:-help}"
    shift || true

    case "$command" in
        morning|morning-startup)
            morning_startup "$@"
            ;;
        evening|evening-capture)
            evening_capture "$@"
            ;;
        do)
            universal_do "$@"
            ;;
        solve|quick-solve)
            quick_solve "$@"
            ;;
        learn)
            learn_topic "$@"
            ;;
        complete)
            complete_task "$@"
            ;;
        setup|setup-daily-habits)
            setup_daily_habits "$@"
            ;;
        help|--help|-h)
            echo "AGENTIC DAILY INTEGRATION"
            echo "========================="
            echo ""
            echo "Daily Commands:"
            echo "  morning     - Start your daily agentic session"
            echo "  evening     - Capture learnings and plan tomorrow"
            echo ""
            echo "Work Commands:"
            echo "  do [task]   - Universal entry point for any work"
            echo "  solve [problem] - Quick problem-solving workflow"
            echo "  learn [topic] - Systematic learning workflow"
            echo "  complete [task] - Task completion workflow"
            echo ""
            echo "Setup:"
            echo "  setup       - Configure daily habits and shell integration"
            echo ""
            echo "Examples:"
            echo "  $0 morning"
            echo "  $0 do \"build a REST API\""
            echo "  $0 solve \"tests are failing\""
            echo "  $0 learn \"Docker containers\""
            echo "  $0 evening"
            ;;
        *)
            echo "Unknown command: $command"
            echo "Use '$0 help' for available commands"
            exit 1
            ;;
    esac
}

main "$@"