# 🧠 Emergency Refresher

**"I haven't used OOS in weeks and forgot everything"**

---

## 🚀 The Only 3 Commands You Need

**1. Create a new project:**
```bash
oos create my-project-name
cd my-project-name
```

**2. See what tasks to work on:**
```bash
oos task ready
```

**3. Mark a task complete:**
```bash
oos task complete TASK_ID
```

---

## 📋 Quick Command Cheat Sheet

**Project Management:**
```bash
oos create project-name      # Create new project
oos --help                  # See all commands
```

**Task Management:**
```bash
oos task create "Do thing"  # Add new task
oos task list               # See all tasks
oos task ready              # See what you can work on now
oos task show TASK_ID       # Get task details
oos task complete TASK_ID   # Mark task done
```

**Daily Usage:**
```bash
git status                   # Check git status
oos task ready              # What to work on
# ...do work...
git add . && git commit -m "message"  # Commit work
oos task complete TASK_ID   # Mark task complete
```

---

## 🎯 "I Just Want To..." Quick Answers

**"...start a new project"**
```bash
oos create cool-project
cd cool-project
# Start coding
```

**"...see what I should work on"**
```bash
oos task ready
```

**"...add a new task"**
```bash
oos task create "Fix the login bug"
```

**"...finish a task"**
```bash
oos task complete abc123  # Use the task ID from 'oos task ready'
```

**"...see all my tasks"**
```bash
oos task list
```

**"...export/import tasks"**
```bash
oos task export backup.jsonl
oos task import backup.jsonl
```

---

## 🔍 How to Find Task IDs

**When you run `oos task ready`, you see something like:**
```
🟡 abc12345: Fix the login bug
🟠 def67890: Add user profile
```

**The ID is the first part (abc12345 or def67890).**
Use that with `oos task complete abc12345`

---

## 📁 Typical Project Structure

**Your OOS project looks like this:**
```
my-project/
├── .oos/
│   ├── tasks/
│   │   ├── tasks.db      # Task database (gitignored)
│   │   └── export.jsonl  # Exported tasks (committed)
│   └── config.yaml       # Project config
├── src/                  # Your code goes here
├── tests/                # Your tests go here
└── README.md
```

**You mostly work in `src/` and ignore `.oos/`**

---

## 🛠️ When Stuff Breaks

**"oos command not found"**
```bash
# Restart terminal or run:
export PATH="$HOME/oos/bin:$PATH"
```

**"Database not found"**
```bash
# You're probably not in an OOS project
cd ~/path/to/your-project
# Or create a new one:
oos create new-project
```

**"Task ID not found"**
```bash
# Check the actual task ID:
oos task list
# Use the full ID shown there
```

---

## 🔄 Daily Workflow Reminder

**Morning:**
```bash
cd ~/my-project
oos task ready        # See what to work on
git pull              # Get latest changes
```

**During Work:**
```bash
# Work on tasks...
git add .
git commit -m "progress on feature X"
```

**End of Day:**
```bash
oos task complete abc123  # Mark finished tasks
git push                   # Share your work
oos task export backup.jsonl  # Backup tasks
```

---

## 💡 Memory Joggers

**Think of OOS as:**
- **Project creator**: `oos create project-name`
- **Task manager**: `oos task create/list/ready/complete`
- **That's it. Everything else is optional.**

**Key mental models:**
- **Projects** = folders with your code
- **Tasks** = things you need to do
- **Ready tasks** = tasks you can work on right now
- **Complete** = when you're done with a task

---

## 🆘 Still Stuck?

1. **Are you in the right project folder?** Run `pwd` and `ls -la`
2. **Does OOS work at all?** Run `oos --help`
3. **Are you trying the right command?** Check the cheat sheet above
4. **Need a refresher on what OOS even is?** Read [What Even Is OOS?](WHAT_IS_OOS.md)

---

## 🎯 The 30-Second Summary

**OOS = tool to create projects and manage tasks**

**Create → Work → Complete**
```bash
oos create project    # Create
cd project            # Enter
oos task ready        # See work
# ...do work...
oos task complete ID  # Complete
```

**That's 90% of what you'll ever use.**

---

*Come back to this page whenever your brain resets. It's designed for exactly that.*