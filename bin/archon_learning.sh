#!/usr/bin/env bash
set -euo pipefail

# Archon Learning System - Use Archon to Track and Enforce Learnings
# Usage: ./bin/archon_learning.sh [record|review|check|enforce]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# This could be a dedicated "Learning Repository" Archon project
LEARNING_PROJECT_ID="${ARCHON_LEARNING_PROJECT_ID:-learning-system-uuid}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

record_lesson() {
  local lesson_title="$1"
  local lesson_description="$2"
  local context="${3:-general}"
  
  echo -e "${BLUE}📚 Recording lesson in Archon...${NC}"
  
  # This would create an Archon task that serves as a "lesson learned"
  cat << EOF
Create Archon Learning Task:

Title: "LESSON: $lesson_title"
Description: "$lesson_description

Context: $context
Date Learned: $(date)
Status: Must Review Before Similar Work

Anti-Pattern: What NOT to do
Pattern: What TO do instead
Trigger: When to remember this lesson"

Feature: learning-retention
Assignee: Developer (whoever works on similar features)
EOF
}

check_for_similar_lessons() {
  local current_work="$1"
  
  echo -e "${YELLOW}🔍 Checking Archon for similar lessons...${NC}"
  
  echo "Query Archon for tasks with:"
  echo "  - Feature: learning-retention"
  echo "  - Title contains: 'LESSON:'"
  echo "  - Description contains keywords from: '$current_work'"
  echo
  echo "This would prevent you from repeating mistakes in:"
  echo "  - Testing approaches"
  echo "  - User experience decisions"
  echo "  - Architecture choices"
  echo "  - Documentation patterns"
}

enforce_lesson_review() {
  local work_type="$1"
  
  echo -e "${PURPLE}🎓 LESSON ENFORCEMENT: $work_type${NC}"
  echo "================================================"
  
  case "$work_type" in
    "testing")
      echo "🧪 Before implementing tests, review these lessons:"
      echo "   - Simple assertion libraries beat complex frameworks"
      echo "   - Test user behavior, not implementation details"
      echo "   - CI fragility comes from over-engineering"
      ;;
    "documentation")
      echo "📖 Before writing docs, review these lessons:"
      echo "   - Users need 'what do I actually need?' guidance"
      echo "   - Start with overview, then details"
      echo "   - Hyperlink everything for navigation"
      ;;
    "features")
      echo "⚡ Before adding features, review these lessons:"
      echo "   - Core should be simple, power tools optional"
      echo "   - Archive clutter, show essentials"
      echo "   - Ask 'will users understand this?'"
      ;;
    "architecture")
      echo "🏗️ Before architecture changes, review these lessons:"
      echo "   - Separate core from optional components"
      echo "   - Make dependencies clear"
      echo "   - Document what everything actually does"
      ;;
  esac
  
  echo
  read -p "Confirm you've reviewed and will apply these lessons (y/N): " -n 1 -r
  echo
  
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ Please review lessons before proceeding${NC}"
    return 1
  fi
}

create_learning_project() {
  echo -e "${GREEN}🎯 Creating Archon Learning System Project${NC}"
  
  cat << EOF
Archon Project Setup:

Title: "OOS Learning & Anti-Pattern Prevention System"
Description: "Tracks lessons learned to prevent repeating the same mistakes.

This project contains:
- Lessons learned from past development
- Anti-patterns to avoid  
- Proven patterns to follow
- Triggers for when to review specific lessons

Each task represents a lesson that should be reviewed before similar work."

Features to track:
- testing-lessons
- documentation-lessons  
- architecture-lessons
- user-experience-lessons
- ci-cd-lessons

Task Pattern:
Title: "LESSON: [Brief Description]"
Description: "
Problem: What went wrong
Solution: How it was fixed
Learning: Key insight
Trigger: When to remember this
Anti-Pattern: What NOT to do
Pattern: What TO do instead
"
EOF
}

main() {
  local command="${1:-check}"
  
  case "$command" in
    "record")
      if [[ $# -lt 3 ]]; then
        echo "Usage: $0 record 'lesson title' 'lesson description' [context]"
        exit 1
      fi
      record_lesson "$2" "$3" "${4:-general}"
      ;;
    "review")
      local work_type="${2:-general}"
      enforce_lesson_review "$work_type"
      ;;
    "check")
      local current_work="${2:-current development}"
      check_for_similar_lessons "$current_work"
      ;;
    "setup")
      create_learning_project
      ;;
    *)
      echo -e "${BLUE}OOS Archon Learning System${NC}"
      echo "========================="
      echo
      echo "Usage: $0 [command] [args...]"
      echo
      echo "Commands:"
      echo "  setup                     - Show how to create learning project in Archon"
      echo "  record 'title' 'desc'     - Record a new lesson in Archon"
      echo "  check 'work description'  - Check for relevant lessons before starting"
      echo "  review [testing|docs|features|architecture] - Enforce lesson review"
      echo
      echo "Example workflow:"
      echo "  1. $0 setup                    # Create learning project in Archon"
      echo "  2. $0 check 'implementing tests' # Before test work"
      echo "  3. $0 review testing           # Enforce lesson review"
      echo "  4. $0 record 'Test Lesson' 'What I learned' # After work"
      ;;
  esac
}

main "$@"