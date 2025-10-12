#!/bin/bash

# AGENTIC HABITS - Automated Habit Formation System
# =================================================
# Creates and reinforces daily agentic workflow habits

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

HABIT_DIR=".oos/habits"
STREAK_FILE="$HABIT_DIR/streaks.json"
AUTOMATION_FILE="$HABIT_DIR/automation.sh"

mkdir -p "$HABIT_DIR"

# Initialize habit tracking
init_habits() {
    echo -e "${BOLD}${BLUE}🔄 INITIALIZING AGENTIC HABITS${NC}"
    echo "==============================="
    echo ""

    # Create streak tracking
    cat > "$STREAK_FILE" << 'EOF'
{
  "morning_startup": {
    "streak": 0,
    "last_date": "",
    "total_days": 0
  },
  "evening_capture": {
    "streak": 0,
    "last_date": "",
    "total_days": 0
  },
  "agentic_usage": {
    "daily_goal": 3,
    "today_count": 0,
    "streak": 0,
    "last_date": ""
  }
}
EOF

    # Create automation script
    cat > "$AUTOMATION_FILE" << EOF
#!/bin/bash
# Auto-generated agentic workflow automation

# Terminal integration - add to your shell config
agentic_auto_start() {
    if [ -f "$PROJECT_ROOT/$HABIT_DIR/active" ]; then
        echo "🤖 Agentic mode active - use /do, /solve, /learn, /complete"
    else
        echo "💡 Start your agentic session: /morning"
    fi
}

# Aliases for daily use
alias morning='$PROJECT_ROOT/bin/agentic-daily.sh morning'
alias evening='$PROJECT_ROOT/bin/agentic-daily.sh evening'
alias do='$PROJECT_ROOT/bin/agentic-daily.sh do'
alias solve='$PROJECT_ROOT/bin/agentic-daily.sh solve'
alias learn='$PROJECT_ROOT/bin/agentic-daily.sh learn'
alias complete='$PROJECT_ROOT/bin/agentic-daily.sh complete'

# Smart prompt integration
if [ "\$PS1" ]; then
    agentic_auto_start
fi
EOF

    chmod +x "$AUTOMATION_FILE"

    echo -e "${GREEN}✅ Habit tracking initialized${NC}"
    echo -e "${BLUE}📋 Shell Integration:${NC}"
    echo "   Add this to your .bashrc or .zshrc:"
    echo "   source $PROJECT_ROOT/$AUTOMATION_FILE"
    echo ""
}

# Track habit completion
track_habit() {
    local habit="$1"
    local today=$(date '+%Y-%m-%d')

    if [ ! -f "$STREAK_FILE" ]; then
        init_habits
    fi

    # Update streak (simplified - in real implementation would use jq)
    echo "Habit tracked: $habit on $today" >> "$HABIT_DIR/activity.log"

    echo -e "${GREEN}✅ Habit tracked: $habit${NC}"
}

# Show habit status
show_status() {
    echo -e "${BOLD}${CYAN}📊 AGENTIC HABITS STATUS${NC}"
    echo "========================="
    echo ""

    if [ -f "$HABIT_DIR/activity.log" ]; then
        local today=$(date '+%Y-%m-%d')
        local morning_today=$(grep "morning" "$HABIT_DIR/activity.log" | grep "$today" | wc -l)
        local evening_today=$(grep "evening" "$HABIT_DIR/activity.log" | grep "$today" | wc -l)
        local usage_today=$(grep -E "(do|solve|learn|complete)" "$HABIT_DIR/activity.log" | grep "$today" | wc -l)

        echo -e "${BLUE}📅 Today's Progress:${NC}"
        echo "   Morning startup: $([ $morning_today -gt 0 ] && echo "✅" || echo "⏸️")"
        echo "   Evening capture: $([ $evening_today -gt 0 ] && echo "✅" || echo "⏸️")"
        echo "   Agentic commands: $usage_today (goal: 3)"
        echo ""

        echo -e "${BLUE}📈 Recent Activity:${NC}"
        tail -5 "$HABIT_DIR/activity.log" | sed 's/^/   • /'
        echo ""
    else
        echo -e "${YELLOW}⚠️  No habit data yet - start with: /morning${NC}"
        echo ""
    fi

    # Motivation and guidance
    echo -e "${CYAN}💡 Today's Agentic Actions:${NC}"
    echo "   • /morning - Start systematic session"
    echo "   • /do \"your task\" - Use natural language commands"
    echo "   • /solve \"your problem\" - Systematic problem solving"
    echo "   • /evening - Capture learnings"
    echo ""
}

# Weekly habit review
weekly_review() {
    echo -e "${BOLD}${BLUE}📊 WEEKLY AGENTIC HABITS REVIEW${NC}"
    echo "================================="
    echo ""

    if [ -f "$HABIT_DIR/activity.log" ]; then
        # Last 7 days analysis
        local last_week=$(date -d '7 days ago' '+%Y-%m-%d')
        local this_week_activities=$(awk -v start="$last_week" '$0 >= start' "$HABIT_DIR/activity.log" | wc -l)

        echo -e "${BLUE}📈 This Week's Stats:${NC}"
        echo "   Total agentic activities: $this_week_activities"
        echo "   Daily average: $((this_week_activities / 7))"
        echo ""

        # Patterns analysis
        echo -e "${BLUE}🔍 Pattern Analysis:${NC}"
        echo "   Most used command: $(grep -E "(do|solve|learn|complete)" "$HABIT_DIR/activity.log" | awk '{print $3}' | sort | uniq -c | sort -nr | head -1 | awk '{print $2}')"
        echo "   Consistency streak building: $([ $this_week_activities -gt 10 ] && echo "Strong 💪" || echo "Keep building 🔨")"
        echo ""

        # Recommendations
        echo -e "${CYAN}💡 Recommendations:${NC}"
        if [ $this_week_activities -lt 10 ]; then
            echo "   • Try using /do more frequently for daily tasks"
            echo "   • Set up shell aliases for easier access"
            echo "   • Use /morning and /evening to build routine"
        else
            echo "   • Great consistency! Try more complex /idea-to-done workflows"
            echo "   • Experiment with /solve for systematic debugging"
            echo "   • Share learnings with team using captured patterns"
        fi
        echo ""
    else
        echo -e "${YELLOW}⚠️  No data for weekly review yet${NC}"
        echo "   Start building habits with daily /morning and /evening routines"
        echo ""
    fi
}

# Setup shell integration
setup_shell_integration() {
    echo -e "${BOLD}${BLUE}🐚 SHELL INTEGRATION SETUP${NC}"
    echo "============================"
    echo ""

    local shell_config=""
    if [ "$SHELL" = "/bin/bash" ]; then
        shell_config="$HOME/.bashrc"
    elif [ "$SHELL" = "/bin/zsh" ]; then
        shell_config="$HOME/.zshrc"
    else
        echo -e "${YELLOW}⚠️  Shell not detected - manual setup needed${NC}"
        echo "Add this to your shell config:"
        echo ""
        cat "$AUTOMATION_FILE"
        return
    fi

    echo -e "${BLUE}📝 Adding agentic integration to: $shell_config${NC}"
    echo ""

    # Check if already integrated
    if grep -q "agentic workflow automation" "$shell_config" 2>/dev/null; then
        echo -e "${GREEN}✅ Already integrated!${NC}"
    else
        echo "# Agentic workflow automation" >> "$shell_config"
        echo "source $PROJECT_ROOT/$AUTOMATION_FILE" >> "$shell_config"
        echo -e "${GREEN}✅ Integration added!${NC}"
        echo ""
        echo -e "${YELLOW}🔄 Restart your terminal or run: source $shell_config${NC}"
    fi
    echo ""
}

# Daily reminder system
setup_daily_reminders() {
    echo -e "${BOLD}${BLUE}⏰ DAILY REMINDER SETUP${NC}"
    echo "========================"
    echo ""

    # Create simple reminder script
    cat > "$HABIT_DIR/daily-reminder.sh" << EOF
#!/bin/bash
# Daily agentic workflow reminder

echo "🌅 Good morning! Start your agentic session:"
echo "   /morning - Initialize systematic thinking"
echo ""
echo "🌙 Don't forget your evening routine:"
echo "   /evening - Capture today's learnings"
EOF

    chmod +x "$HABIT_DIR/daily-reminder.sh"

    echo -e "${BLUE}💡 Reminder Options:${NC}"
    echo "   1. Terminal startup reminder (recommended)"
    echo "   2. Calendar/todo app integration"
    echo "   3. System notifications"
    echo ""

    echo -e "${GREEN}✅ Reminder script created at: $HABIT_DIR/daily-reminder.sh${NC}"
    echo "Integrate with your preferred reminder system"
    echo ""
}

# Main command router
main() {
    local command="${1:-help}"
    shift || true

    case "$command" in
        init|initialize)
            init_habits "$@"
            ;;
        track)
            track_habit "$@"
            ;;
        status|show)
            show_status "$@"
            ;;
        weekly|review)
            weekly_review "$@"
            ;;
        shell|shell-integration)
            setup_shell_integration "$@"
            ;;
        reminders|daily-reminders)
            setup_daily_reminders "$@"
            ;;
        complete-setup)
            echo -e "${BOLD}${GREEN}🚀 COMPLETE AGENTIC HABITS SETUP${NC}"
            echo "=================================="
            echo ""
            init_habits
            setup_shell_integration
            setup_daily_reminders
            echo -e "${GREEN}✅ Complete agentic habits setup finished!${NC}"
            echo ""
            echo "Next steps:"
            echo "1. Restart your terminal"
            echo "2. Try: /morning"
            echo "3. Use: /do \"your first task\""
            echo "4. End with: /evening"
            ;;
        help|--help|-h)
            echo "AGENTIC HABITS - Automated Habit Formation"
            echo "=========================================="
            echo ""
            echo "Setup Commands:"
            echo "  init              - Initialize habit tracking"
            echo "  shell-integration - Setup shell aliases and prompts"
            echo "  daily-reminders   - Setup reminder system"
            echo "  complete-setup    - Run full setup process"
            echo ""
            echo "Tracking Commands:"
            echo "  track [habit]     - Track habit completion"
            echo "  status            - Show today's habit status"
            echo "  weekly            - Weekly habits review"
            echo ""
            echo "Quick Start:"
            echo "  $0 complete-setup"
            ;;
        *)
            echo "Unknown command: $command"
            echo "Use '$0 help' for available commands"
            exit 1
            ;;
    esac
}

main "$@"