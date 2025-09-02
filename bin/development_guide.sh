#!/usr/bin/env bash
set -euo pipefail

# OOS Development Guide - Enforce Learning Application
# Usage: ./bin/development_guide.sh [check|reminder|update]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

show_critical_reminders() {
  echo -e "${PURPLE}🧠 OOS DEVELOPMENT WISDOM - READ BEFORE CODING${NC}"
  echo "=================================================================="
  echo
  
  echo -e "${RED}⚠️  STOP: Have you read the testing philosophy?${NC}"
  echo "   📖 docs/TESTING_PHILOSOPHY.md contains hard-learned lessons"
  echo "   🎯 Key insight: 'I keep learning the same lessons over and over'"
  echo
  
  echo -e "${YELLOW}📋 PRE-DEVELOPMENT CHECKLIST:${NC}"
  echo "   □ Read docs/TESTING_PHILOSOPHY.md recent learnings section"
  echo "   □ Check docs/SYSTEM_OVERVIEW.md for architecture understanding"
  echo "   □ Ask: 'Will users understand this change?'"
  echo "   □ Ask: 'Can this be tested automatically?'"
  echo "   □ Ask: 'Is this the simplest solution?'"
  echo
  
  echo -e "${BLUE}🔄 LEARNED ANTI-PATTERNS TO AVOID:${NC}"
  echo "   ❌ Complex test frameworks (they break more than they help)"
  echo "   ❌ Overwhelming users with too many options"
  echo "   ❌ Creating tools without clear documentation of their purpose"
  echo "   ❌ Assuming users understand the system architecture"
  echo "   ❌ Building features before understanding user confusion"
  echo
  
  echo -e "${GREEN}✅ PROVEN PATTERNS TO FOLLOW:${NC}"
  echo "   ✓ Simple, reliable validation over complex frameworks"
  echo "   ✓ Clear separation between core and optional features"
  echo "   ✓ Documentation that explains 'what do I actually need?'"
  echo "   ✓ Modular design - users can ignore what they don't need"
  echo "   ✓ Archive clutter, keep essentials visible"
  echo
}

check_recent_learnings() {
  local philosophy_file="$PROJECT_ROOT/docs/TESTING_PHILOSOPHY.md"
  
  if [[ -f "$philosophy_file" ]]; then
    local last_update
    last_update=$(stat -c %Y "$philosophy_file")
    local days_old=$(( ($(date +%s) - last_update) / 86400 ))
    
    if [[ $days_old -gt 30 ]]; then
      echo -e "${YELLOW}⚠️  Testing philosophy hasn't been updated in $days_old days${NC}"
      echo "   Consider adding recent learnings to prevent repeating lessons"
    else
      echo -e "${GREEN}✓ Testing philosophy recently updated ($days_old days ago)${NC}"
    fi
  fi
}

enforce_learning_review() {
  echo -e "${PURPLE}🎓 LEARNING ENFORCEMENT CHECK${NC}"
  echo "=============================="
  echo
  
  echo "Before proceeding with development, confirm you've internalized:"
  echo
  
  echo "1. Testing Approach:"
  echo "   - Simple assertion libraries > Complex test frameworks"
  echo "   - Test user behavior, not implementation details"
  echo "   - CI should be reliable, not fragile"
  echo
  
  echo "2. User Experience:"
  echo "   - Users get confused by overlapping systems"
  echo "   - Documentation must explain 'what do I actually need?'"
  echo "   - Archive non-essential files to reduce cognitive load"
  echo
  
  echo "3. Development Philosophy:"
  echo "   - Core functionality should be simple"
  echo "   - Power tools should be optional"
  echo "   - Always ask 'will users understand this?'"
  echo
  
  read -p "Have you reviewed and will apply these learnings? (y/N): " -n 1 -r
  echo
  
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ Please review docs/TESTING_PHILOSOPHY.md before continuing${NC}"
    exit 1
  else
    echo -e "${GREEN}✅ Learning review confirmed. Proceed with development.${NC}"
  fi
}

update_learnings() {
  local philosophy_file="$PROJECT_ROOT/docs/TESTING_PHILOSOPHY.md"
  
  echo -e "${BLUE}📝 Adding new learning to testing philosophy...${NC}"
  echo
  echo "What new insight did you discover? (Enter to skip)"
  read -r new_insight
  
  if [[ -n "$new_insight" ]]; then
    echo "#### **$(date '+%B %Y') Development Session**" >> "$philosophy_file"
    echo "- **Learning**: $new_insight" >> "$philosophy_file"
    echo "" >> "$philosophy_file"
    
    echo -e "${GREEN}✅ Learning added to $philosophy_file${NC}"
    echo "This will help prevent repeating the same lessons."
  fi
}

main() {
  local command="${1:-reminder}"
  
  case "$command" in
    "check")
      check_recent_learnings
      ;;
    "reminder")
      show_critical_reminders
      echo
      enforce_learning_review
      ;;
    "update")
      update_learnings
      ;;
    "quick")
      show_critical_reminders
      ;;
    *)
      echo "Usage: $0 [check|reminder|update|quick]"
      echo
      echo "  check     - Check if learnings are up to date"
      echo "  reminder  - Show critical reminders and enforce review"
      echo "  update    - Add new learning to prevent repetition"
      echo "  quick     - Show reminders without enforcement"
      exit 1
      ;;
  esac
}

main "$@"