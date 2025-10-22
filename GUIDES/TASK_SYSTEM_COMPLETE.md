# 🎓 OOS Task System - Complete Guide

**Everything you need to become a task management expert.**

---

## 🎯 From Beginner to Expert

**You've mastered the basics. Now learn the powerful features that make OOS tasks truly exceptional.**

**If you haven't read [Task System Basics](TASK_SYSTEM_SIMPLE.md) yet, start there.**

---

## 📊 Advanced Task Creation

### Rich Task Metadata

**Create comprehensive tasks:**
```bash
oos task create "Implement OAuth2 authentication" \
  --description "Add Google and GitHub OAuth login with proper error handling" \
  --priority high \
  --assignee alice \
  --tags "auth,security,frontend,backend" \
  --depends-on "abc123,def456" \
  --estimated-hours 8 \
  --due-date "2024-01-15" \
  --context "project=web-app,sprint=3,story_id=PROJ-456,complexity=high"
```

**Task Context Explained:**
- `project`: Which project this belongs to
- `sprint`: Development sprint number
- `story_id`: Link to external tracking systems
- `complexity`: How complex this task is
- Any custom key-value pairs you want

### Bulk Task Creation

**Create multiple related tasks:**
```bash
# User authentication feature tasks
oos task create "Design auth UI" --priority high --tags "auth,frontend,design"
oos task create "Implement login API" --priority high --tags "auth,backend,api" --depends-on $(oos task list --tags "design" --json | jq -r '.[0].id')
oos task create "Add password hashing" --priority high --tags "auth,security,backend" --depends-on $(oos task list --tags "api" --json | jq -r '.[0].id')
oos task create "Write auth tests" --priority medium --tags "auth,testing"
oos task create "Document auth flow" --priority low --tags "auth,documentation"
```

---

## 🔗 Advanced Dependency Management

### Complex Dependency Chains

**Build a proper dependency graph:**
```bash
# Database layer
DB_TASK=$(oos task create "Design database schema" --tags "database,design" --json | jq -r '.id')

# API layer depends on database
API_TASK=$(oos task create "Build REST API" --tags "api,backend" --depends-on $DB_TASK --json | jq -r '.id')

# Frontend depends on API
UI_TASK=$(oos task create "Create user interface" --tags "frontend,ui" --depends-on $API_TASK --json | jq -r '.id')

# Testing depends on everything
TEST_TASK=$(oos task create "Integration testing" --tags "testing,qa" --depends-on "$API_TASK,$UI_TASK" --json | jq -r '.id')
```

### Managing Dependency Conflicts

**Check for circular dependencies:**
```bash
# This would show if you accidentally created circular deps
oos task list --status blocked
```

**Update dependencies safely:**
```bash
# Add a new dependency
oos task update abc123 --add-dependencies "def456"

# Remove a completed dependency
oos task update abc123 --remove-dependencies "old123"

# See what a task is blocking
oos task show abc123 | grep "Blocks"
```

---

## 📈 Advanced Querying and Filtering

### Complex Filters

**Combine multiple filters:**
```bash
# High priority tasks assigned to me that are bugs
oos task list \
  --priority high \
  --assignee $(whoami) \
  --tags "bug" \
  --status todo,doing

# Tasks due this week
oos task list \
  --due-before $(date -d "next friday" +%Y-%m-%d) \
  --status todo,doing

# Complex tag combinations (OR logic within tags)
oos task list --tags "urgent,security,performance"

# Tasks I assigned that are now done (for review)
oos task list --assignee $(whoami) --status done --limit 10
```

### Advanced Sorting and Grouping

**Sort tasks intelligently:**
```bash
# Sort by priority, then by creation date
oos task list --sort priority --reverse --sort created

# See recently updated tasks
oos task list --sort updated --reverse --limit 5

# Group by status (manual grouping)
for status in todo doing blocked done; do
  echo "=== $status ==="
  oos task list --status $status --limit 3
  echo
done
```

### Custom Queries with JSON Output

**Build custom queries:**
```bash
# Get tasks as JSON for custom processing
oos task list --json | jq '.[] | select(.priority == "urgent" and .status == "todo")'

# Count tasks by assignee
oos task list --json | jq 'group_by(.assignee) | map({assignee: .[0].assignee, count: length})'

# Find tasks that have been "doing" for more than 3 days
oos task list --status doing --json | jq '.[] | select(.updated_at < (now - 3*24*3600 | strftime("%Y-%m-%d")))'
```

---

## 🔄 Advanced Workflow Management

### Custom Status Workflows

**Beyond the basic todo → done:**
```bash
# Standard development workflow
oos task create "New feature" --status todo
# ... start working ...
oos task update abc123 --status doing
# ... code is ready ...
oos task update abc123 --status technical-complete
# ... testing phase ...
oos task update abc123 --status ruat-validation
# ... ready for review ...
oos task update abc123 --status review
# ... approved! ...
oos task complete abc123
```

### Sprint and Milestone Management

**Organize tasks by sprint:**
```bash
# Create sprint tasks
oos task create "Sprint 3 Planning" --context "sprint=3,type=planning"
oos task create "User authentication" --context "sprint=3,type=feature,story_points=5"
oos task create "Fix login bug" --context "sprint=3,type=bug,story_points=2"
oos task create "Performance optimization" --context "sprint=3,type=optimization,story_points=3"

# View sprint tasks
oos task list --context "sprint=3"

# Get sprint metrics
oos task list --context "sprint=3" --json | jq '
{
  total_tasks: length,
  story_points: map(.context.story_points | tonumber) | add,
  by_status: group_by(.status) | map({status: .[0].status, count: length})
}'
```

### Time Tracking Integration

**Track time on tasks:**
```bash
# Create task with time estimate
oos task create "Complex feature" --estimated-hours 16

# Log actual hours as you work
oos task update abc123 --actual-hours 4
oos task update abc123 --actual-hours 8  # Adds 4 more hours (total 12)

# View time tracking reports
oos task list --json | jq '.[] | {title: .title, estimated: .estimated_hours, actual: .actual_hours, efficiency: (.estimated_hours / .actual_hours)}'
```

---

## 💾 Advanced Data Management

### Intelligent Export/Import

**Export with custom filters:**
```bash
# Export only high-p incomplete tasks
oos task export critical-tasks.jsonl \
  --status todo,doing,blocked \
  --priority high,urgent

# Export tasks for a specific project
oos task export project-tasks.jsonl \
  --context "project=web-app"

# Export completed tasks for archive
oos task export done-tasks-$(date +%Y%m).jsonl \
  --status done \
  --exclude-fields "context,actual_hours"
```

### Backup and Recovery Strategies

**Automated backup system:**
```bash
#!/bin/bash
# backup-tasks.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$HOME/backups/oos-tasks"

mkdir -p $BACKUP_DIR

# Export current tasks
oos task export $BACKUP_DIR/tasks-$DATE.jsonl

# Compress old backups
find $BACKUP_DIR -name "tasks-*.jsonl" -mtime +7 -exec gzip {} \;

# Keep only last 30 days of backups
find $BACKUP_DIR -name "tasks-*.jsonl.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/tasks-$DATE.jsonl"
```

### Cross-Project Task Templates

**Export project templates:**
```bash
# Export project structure (no actual work)
oos task export web-app-template.jsonl \
  --status todo \
  --exclude-fields "assignee,actual_hours,completed_at"

# Import template into new project
cd new-project
oos task import ../templates/web-app-template.jsonl \
  --resolution create-new
```

---

## 👥 Advanced Team Collaboration

### Team Workflows

**Code review process:**
```bash
# Developer creates task and assigns to reviewer
oos task create "Implement feature X" --assignee alice
oos task update abc123 --status review --context "reviewer=bob"

# Reviewer can see tasks assigned for review
oos task list --context "reviewer=$(whoami)"

# After review, update status
oos task update abc123 --status done --context "review_approved=true"
```

### Bulk Operations

**Team task management:**
```bash
# Reassign all tasks from a team member who left
for task_id in $(oos task list --assignee alice --json | jq -r '.[].id'); do
  oos task update $task_id --assignee bob
done

# Bulk update priorities for sprint planning
oos task list --context "sprint=4" --json | jq -r '.[].id' | xargs -I {} oos task update {} --priority high

# Close all cancelled tasks
oos task list --status cancelled --json | jq -r '.[].id' | xargs -I {} oos task update {} --status done
```

### Integration with External Tools

**GitHub Issues integration:**
```bash
# Create tasks from GitHub issues
for issue in $(gh issue list --json number,title --jq '.[].number'); do
  title=$(gh issue view $issue --json title --jq '.title')
  oos task create "$title" --context "github_issue=$issue"
done

# Update GitHub issue when task completes
oos task complete abc123
issue_id=$(oos task show abc123 --json | jq -r '.context.github_issue')
gh issue edit $issue_id --state closed
```

---

## 📊 Advanced Analytics and Reporting

### Custom Reports

**Productivity metrics:**
```bash
# Task completion rate by week
oos task list --json | jq '
group_by(.completed_at[0:7]) |
map({
  month: .[0].completed_at[0:7],
  completed: map(select(.status == "done")) | length,
  total: length,
  rate: (map(select(.status == "done")) | length / length * 100 | round)
})
'

# Average time to complete tasks
oos task list --status done --json | jq '
map(.completed_at - .created_at | tonumber / 86400) |
add / length |
round |
"The average task takes \(.) days to complete"
'

# Priority distribution
oos task list --json | jq '
group_by(.priority) |
map({priority: .[0].priority, count: length}) |
sort_by(.count) |
reverse
'
```

### Performance Dashboards

**Create a dashboard script:**
```bash
#!/bin/bash
# task-dashboard.sh

echo "=== OOS Task Dashboard ==="
echo "Generated: $(date)"
echo

echo "📊 Overall Status:"
oos task list --json | jq -r '
[
  {status: "todo", count: map(select(.status == "todo")) | length},
  {status: "doing", count: map(select(.status == "doing")) | length},
  {status: "done", count: map(select(.status == "done")) | length}
] | .[] | "\(.status): \(.count) tasks"
'
echo

echo "🔥 High Priority Items:"
oos task list --priority high,urgent --status todo,doing
echo

echo "⚠️ Blocked Tasks:"
oos task list --status blocked
echo

echo "🏆 Recently Completed (last 7 days):"
oos task list --status done --sort completed --reverse --limit 5
```

---

## 🔧 Customization and Automation

### Project-Specific Task Types

**Define custom task workflows:**
```bash
# Create custom task categories
oos task create "Design new component" --context "type=design,phase=concept"
oos task create "Build component" --context "type=development,phase=implementation"
oos task create "Test component" --context "type=testing,phase=qa"
oos task create "Deploy component" --context "type=deployment,phase=production"

# Query by type and phase
oos task list --context "type=development"
oos task list --context "phase=qa"
```

### Automation Scripts

**Automated task management:**
```bash
#!/bin/bash
# auto-task-manager.sh

# Find tasks stuck in "doing" for too long
STUCK_TASKS=$(oos task list --status doing --json | jq '.[] | select(.updated_at < (now - 3*24*3600 | strftime("%Y-%m-%d"))) | .id')

if [ ! -z "$STUCK_TASKS" ]; then
  echo "⚠️ Tasks stuck in 'doing' for over 3 days:"
  echo "$STUCK_TASKS"
  echo
  echo "Consider updating or unblocking these tasks."
fi

# Auto-create daily standup task
TODAY=$(date +%Y-%m-%d)
if ! oos task list --context "daily_standup=$TODAY" | grep -q .; then
  oos task create "Daily standup - $TODAY" \
    --context "daily_standup=$TODAY,type=meeting" \
    --priority medium
fi
```

---

## 🎯 Pro Tips and Best Practices

### Task Hygiene

**Keep your task system clean:**
```bash
# Weekly cleanup script
#!/bin/bash

# Archive completed tasks older than 30 days
oos task export archive-$(date +%Y%m).jsonl \
  --status done \
  --filter "completed_at < $(date -d '30 days ago' +%Y-%m-%d)"

# Delete old archived tasks (careful!)
# oos task delete $(oos task list --status done --json --filter "completed_at < $(date -d '90 days ago' +%Y-%m-%d)" | jq -r '.[].id')

# Update stale tasks
oos task list --status doing --json | jq '.[] | select(.updated_at < (now - 7*24*3600 | strftime("%Y-%m-%d"))) | .id' | xargs -I {} oos task update {} --context "stale=true"
```

### Advanced Git Integration

**Sophisticated git workflow:**
```bash
#!/bin/bash
# git-task-hook.sh

# Pre-commit hook
echo "Exporting tasks..."
oos task export .oos/tasks/pre-commit-export.jsonl
git add .oos/tasks/pre-commit-export.jsonl

# Check if task is referenced in commit message
TASK_ID=$(git log -1 --pretty=format:%s | grep -o '\b[a-z0-9]\{6\}\b')
if [ ! -z "$TASK_ID" ]; then
  echo "Referencing task $TASK_ID in commit"
  oos task update $TASK_ID --context "last_commit=$(git rev-parse HEAD)"
fi
```

---

## 🎓 Mastery Checklist

**You're an OOS Task Master when you can:**

- [ ] **Design complex dependency graphs** without creating cycles
- [ ] **Use context fields effectively** for project organization
- [ ] **Create custom queries** with JSON output and jq
- [ ] **Implement team workflows** with proper handoffs
- [ ] **Set up automated backups** and recovery procedures
- [ ] **Build custom reports** and dashboards
- [ ] **Integrate with external tools** like GitHub Issues
- [ ] **Automate routine task management** with scripts
- [ ] **Maintain task hygiene** with cleanup procedures
- [ ] **Customize workflows** for your specific needs

---

## 📖 Next Steps

**Continue your journey:**
- [Task Dependencies Guide](TASK_DEPENDENCIES.md) - Master dependency planning
- [Team Collaboration Guide](TASK_TEAMWORK.md) - Multi-person workflows
- [Advanced Usage Guide](../docs/ADVANCED_USAGE_GUIDE.md) - Power user features
- [API Reference](../docs/API_REFERENCE.md) - For developers

---

**Remember: The goal is productive organization, not bureaucratic overhead. Use the features that help you, ignore the ones that don't.**