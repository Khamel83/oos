# ⚡ OOS Quick Reference

**One-page cheat sheet. Print this. Save it. Keep it handy.**

---

## 🚀 Project Management

| What You Want | Command | Example |
|---------------|---------|---------|
| **Create new project** | `oos create <name>` | `oos create my-app` |
| **Get help** | `oos --help` | `oos --help` |
| **Check OOS status** | `oos status` | `oos status` |

---

## 📋 Task Management

| What You Want | Command | Example |
|---------------|---------|---------|
| **Create new task** | `oos task create "title"` | `oos task create "Fix login bug"` |
| **List all tasks** | `oos task list` | `oos task list` |
| **See ready tasks** | `oos task ready` | `oos task ready` |
| **Show task details** | `oos task show <ID>` | `oos task show abc123` |
| **Update task** | `oos task update <ID>` | `oos task update abc123 --status doing` |
| **Complete task** | `oos task complete <ID>` | `oos task complete abc123` |
| **Delete task** | `oos task delete <ID>` | `oos task delete abc123` |

---

## 🔧 Task Creation Options

| Option | What it does | Example |
|--------|--------------|---------|
| `--description` | Add description | `--description "Fix the OAuth flow"` |
| `--priority` | Set priority | `--priority high` |
| `--assignee` | Assign to person | `--assignee alice` |
| `--tags` | Add tags | `--tags "bug,urgent,frontend"` |
| `--depends-on` | Set dependencies | `--depends-on "task123,task456"` |

**Full example:**
```bash
oos task create "Fix authentication" \
  --description "Users can't log in with Google" \
  --priority urgent \
  --assignee alice \
  --tags "bug,auth,urgent" \
  --depends-on "abc123"
```

---

## 📊 Task Filtering & Listing

| What You Want | Command | Example |
|---------------|---------|---------|
| **Tasks by status** | `oos task list --status <status>` | `oos task list --status todo` |
| **Tasks by person** | `oos task list --assignee <name>` | `oos task list --assignee alice` |
| **Tasks by priority** | `oos task list --priority <level>` | `oos task list --priority high` |
| **Tasks with tags** | `oos task list --tags <tags>` | `oos task list --tags "bug,urgent"` |
| **Limit results** | `oos task list --limit <number>` | `oos task list --limit 5` |
| **Sort tasks** | `oos task list --sort <field>` | `oos task list --sort priority` |

**Status options:** `todo`, `doing`, `technical-complete`, `ruat-validation`, `review`, `done`, `blocked`, `cancelled`

**Priority options:** `low`, `medium`, `high`, `urgent`

---

## 💾 Data Management

| What You Want | Command | Example |
|---------------|---------|---------|
| **Export tasks** | `oos task export <file>` | `oos task export backup.jsonl` |
| **Import tasks** | `oos task import <file>` | `oos task import backup.jsonl` |
| **Sync with file** | `oos task sync <file>` | `oos task sync remote.jsonl` |
| **Get statistics** | `oos task stats` | `oos task stats` |

---

## 🔄 Daily Workflow

**Morning routine:**
```bash
cd ~/my-project          # Enter project
git pull                  # Get latest changes
oos task ready            # See what to work on
```

**During work:**
```bash
oos task create "New task"  # Add tasks as you think of them
git add . && git commit -m "Working on feature"  # Commit progress
```

**End of day:**
```bash
oos task complete abc123  # Mark finished tasks
git push                  # Share work
oos task export backup.jsonl  # Backup tasks
```

---

## 📝 Task Status Flow

```
todo → doing → technical-complete → ruat-validation → review → done
```

**Quick status changes:**
```bash
oos task update abc123 --status doing        # Start working
oos task update abc123 --status done         # Mark done
```

---

## 🎯 Common Task Patterns

**Bug fix:**
```bash
oos task create "Fix X bug" --priority high --tags "bug"
```

**Feature:**
```bash
oos task create "Add X feature" --tags "feature,backend"
```

**Research:**
```bash
oos task create "Research X" --tags "research,documentation"
```

**Dependent task:**
```bash
oos task create "Test X feature" --depends-on "task123"
```

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| **Command not found** | Restart terminal or check PATH |
| **Database not found** | Make sure you're in an OOS project directory |
| **Task ID not found** | Run `oos task list` to see correct IDs |
| **Permission denied** | Check file permissions in `.oos/` directory |

---

## 📂 Project Structure

```
my-project/
├── .oos/
│   ├── tasks/
│   │   ├── tasks.db      # Task database (don't edit manually)
│   │   └── export.jsonl  # Exported tasks (safe to share)
│   └── config.yaml       # Project configuration
├── src/                  # Your code goes here
├── tests/                # Your tests go here
└── README.md
```

---

## 🔍 Find Task IDs

**Run `oos task ready` or `oos task list` to see IDs:**
```
🟡 abc12345: Fix the login bug (@alice)
🟠 def67890: Add user profile (@bob)
```

**Use the short ID (first 6-8 characters):**
```bash
oos task complete abc123
```

---

## 💡 Pro Tips

1. **Always use `oos task ready`** to know what to work on next
2. **Export tasks regularly** as backup: `oos task export backup.jsonl`
3. **Use descriptive titles** - you'll thank yourself later
4. **Tag everything** - makes finding things easier
5. **Update task status** as you work, not just at the end

---

## 🎯 The 80/20 Rule

**You'll use these 5 commands 80% of the time:**
```bash
oos create project-name      # Start new project
oos task create "Task"       # Add task
oos task ready               # See what to do
oos task complete ID         # Finish task
oos task list                # See everything
```

**Everything else is for special situations.**

---

*Print this page. Keep it on your desk. You'll need it.*