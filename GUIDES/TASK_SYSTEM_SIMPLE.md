# 📋 Task System - The Simple Version

**Just the essentials. No technical jargon.**

---

## 🎯 What Are Tasks?

**Tasks = things you need to do in your project.**

Think of it like a to-do list that:
- Lives inside your project
- Tracks what's blocking what
- Remembers what you've finished
- Works with git (so you don't lose it)

---

## 🚀 Getting Started with Tasks

**Step 1: Create your first task**
```bash
oos task create "Set up user login"
```

**Step 2: See what you can work on**
```bash
oos task ready
```

**Step 3: Finish a task**
```bash
oos task complete abc123  # Use the ID from step 2
```

**That's the basic loop. Everything else is optional.**

---

## 📝 Essential Task Commands

| What you want | Command | Example |
|---------------|---------|---------|
| **Add a new task** | `oos task create "title"` | `oos task create "Fix login bug"` |
| **See what to work on** | `oos task ready` | `oos task ready` |
| **See all tasks** | `oos task list` | `oos task list` |
| **Finish a task** | `oos task complete <ID>` | `oos task complete abc123` |
| **Get task details** | `oos task show <ID>` | `oos task show abc123` |

---

## 🔄 Daily Task Workflow

**When you start working:**
```bash
oos task ready    # See what you can work on
```

**When you think of something new:**
```bash
oos task create "New thing I need to do"
```

**When you finish something:**
```bash
oos task complete abc123  # Use the task ID
```

**When you're confused:**
```bash
oos task list    # See everything
```

---

## 🏷️ Making Tasks Useful

**Add some details when creating tasks:**
```bash
oos task create "Fix login bug" \
  --priority high \
  --tags "bug,urgent" \
  --description "Users can't log in with Google"
```

**Priority levels:** `low`, `medium`, `high`, `urgent`

**Tags help you find related tasks:**
- `bug` - for bugs
- `feature` - for new features
- `urgent` - for important things
- `documentation` - for docs

---

## 🔗 Task Dependencies

**Sometimes tasks depend on other tasks:**

```bash
# First task
oos task create "Set up database"

# Second task that depends on the first
oos task create "Create user table" --depends-on abc123
```

**What happens:**
- The second task won't show up in `oos task ready`
- It will only become ready after the first task is completed
- This prevents you from working on things out of order

---

## 📊 Task Statuses

**The main statuses you'll use:**

| Status | When to use it | Command |
|--------|----------------|---------|
| `todo` | New tasks (default) | `--status todo` |
| `doing` | Currently working on | `oos task update ID --status doing` |
| `done` | Finished | `oos task complete ID` |

**Other statuses (rarely used):**
- `technical-complete` - Code works, needs testing
- `ruat-validation` - Testing by real users
- `review` - Ready for code review
- `blocked` - Can't work on this (dependencies)
- `cancelled` - Not doing this anymore

---

## 🎯 Finding the Right Tasks

**See what you can work on right now:**
```bash
oos task ready
```

**See all tasks of a certain type:**
```bash
oos task list --status todo        # All not-started tasks
oos task list --priority high      # All important tasks
oos task list --tags "bug"         # All bugs
oos task list --assignee alice     # All tasks for a person
```

**Limit the results:**
```bash
oos task list --limit 5            # Show only 5 tasks
```

---

## 💾 Backing Up Tasks

**Export your tasks (good practice):**
```bash
oos task export backup.jsonl
```

**This creates a file you can:**
- Commit to git
- Share with teammates
- Restore from if something breaks

**Import tasks (less common):**
```bash
oos task import backup.jsonl
```

---

## 🤝 Working with a Team

**Assign tasks to people:**
```bash
oos task create "Review code" --assignee alice
```

**See tasks for a specific person:**
```bash
oos task list --assignee alice
```

**Team workflow:**
1. Everyone creates tasks as needed
2. Export tasks regularly: `oos task export team-tasks.jsonl`
3. Commit the export to git
4. Pull latest changes and import: `oos task import team-tasks.jsonl`

---

## 🎯 Real-World Examples

**Bug fixing:**
```bash
oos task create "Fix login button doesn't work" \
  --priority high \
  --tags "bug,frontend" \
  --assignee john
```

**Feature development:**
```bash
oos task create "Add user profile page" \
  --priority medium \
  --tags "feature,frontend" \
  --depends-on abc123  # Depends on user authentication
```

**Documentation:**
```bash
oos task create "Write API documentation" \
  --priority low \
  --tags "documentation"
```

---

## 🆘 Common Problems

**"I don't see any tasks in `oos task ready`"**
- Either all tasks are completed
- Or tasks are blocked by dependencies
- Run `oos task list` to see everything

**"I can't find my task ID"**
```bash
oos task list  # Shows all task IDs
```

**"I completed a task but it still shows up"**
```bash
oos task complete abc123  # Make sure to complete, not just update status
```

---

## 💡 Best Practices

1. **Create tasks immediately** when you think of something
2. **Use descriptive titles** - "Fix X" is better than "Issue"
3. **Set priorities** - helps you focus on what matters
4. **Use tags** - makes finding related tasks easier
5. **Export regularly** - don't lose your work
6. **Complete tasks properly** - use `oos task complete`, not just changing status

---

## 🎯 The Mental Model

**Think of tasks like email:**
- **Create tasks** like composing emails
- **Ready tasks** like your inbox
- **Complete tasks** like archiving emails
- **Dependencies** like waiting for a reply

**The goal:** Always know what to work on next without thinking about it.

---

## 📖 What's Next?

- **[Quick Reference](../QUICK_REFERENCE.md)** - All commands on one page
- **[Emergency Refresher](EMERGENCY_REFRESHER.md)** - When you forget this
- **[Task Dependencies](TASK_DEPENDENCIES.md)** - Advanced planning
- **[Team Task Management](TASK_TEAMWORK.md)** - Working with others

---

**Remember: The goal is to make your life easier, not more complicated. Start with the basic commands and add more as you need them.**