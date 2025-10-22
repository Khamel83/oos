# 🔄 Daily OOS Workflow

**How to use OOS every day without thinking about it.**

---

## 🌅 Morning Routine (5 minutes)

**Start your day right:**
```bash
# Navigate to your project
cd ~/my-project

# See what you should work on
oos task ready

# Get latest changes
git pull

# That's it. Now start coding.
```

**What this tells you:**
- What tasks are ready to work on
- What your team members have been doing
- Any new issues or blockers

---

## 💻 During the Day (As needed)

**When you think of something new:**
```bash
# Quickly add a task
oos task create "Quick idea I just had"

# Get back to work
# Don't overthink it - just capture the thought
```

**When you start working on something:**
```bash
# Update task status (optional but helpful)
oos task update abc123 --status doing
```

**When you finish something:**
```bash
# Mark it complete
oos task complete abc123

# Celebrate small wins! ✨
```

**When you're stuck:**
```bash
# See what else you can work on
oos task ready

# Or see all tasks
oos task list
```

---

## 🌙 End of Day (5 minutes)

**Wrap up your work:**
```bash
# Complete any finished tasks
oos task complete abc123
oos task complete def456

# Commit your work
git add .
git commit -m "progress: implemented user authentication and fixed login bugs"

# Share with team
git push

# Backup tasks (optional but smart)
oos task export backup-$(date +%Y%m%d).jsonl

# See what's ready for tomorrow
oos task ready

# Go home! 🎉
```

---

## 📝 Weekly Routine (15 minutes)

**Once a week, do some housekeeping:**
```bash
# Review all your tasks
oos task list

# Clean up old completed tasks
oos task export archive-$(date +%Y%m).jsonl --status done

# Update task priorities if needed
oos task update abc123 --priority high
oos task update def456 --priority low

# Plan the week ahead
oos task create "Week of $(date +%Y-%m-%d) planning" --priority medium
```

---

## 🎯 Typical Day Example

**Let's walk through a realistic day:**

**9:00 AM - Start work:**
```bash
cd ~/project-alpha
oos task ready
git pull
```
*Output shows 3 ready tasks*

**9:05 AM - Pick a task and start:**
```bash
oos task update abc123 --status doing
# Start coding...
```

**10:30 AM - Think of something new:**
```bash
oos task create "Need to fix the CSS for mobile" --tags "css,mobile,bug"
# Back to main task...
```

**2:00 PM - Finish a task:**
```bash
oos task complete abc123
git add .
git commit -m "feat: implement user authentication flow"
```

**2:05 PM - Check what's next:**
```bash
oos task ready
```
*New task appears that was blocked by the completed task*

**5:30 PM - End of day:**
```bash
git add .
git commit -m "fix: mobile responsive issues and security improvements"
git push
oos task complete def456
oos task export backup-$(date +%Y%m%d).jsonl
```

---

## 🔥 Power User Tips

### Habit Building

**Make it automatic:**
```bash
# Add to your shell profile (.zshrc or .bashrc)
alias workon='cd ~/project && oos task ready && git pull'
alias daydone='git add . && git commit -m "daily progress" && git push && oos task export backup-$(date +%Y%m%d).jsonl'

# Now your workflow is:
workon    # Start work
# ...code all day...
daydone   # End work
```

### Context Switching

**Working on multiple projects:**
```bash
# Morning - Project A
cd ~/project-a
oos task ready

# Afternoon - Project B
cd ~/project-b
oos task ready

# Each project has its own tasks
```

### Team Coordination

**Sync with team:**
```bash
# Morning - get team tasks
git pull
oos task import team-tasks.jsonl --resolution merge

# Evening - share your tasks
oos task export team-tasks.jsonl
git add team-tasks.jsonl
git commit -m "update: task export for team sync"
git push
```

---

## 🎯 Decision Tree

**Don't know what to do? Ask yourself:**

```
Did I just start working?
├── YES: Run 'oos task ready' and pick something
└── NO: Continue...

Did I just finish something?
├── YES: Run 'oos task complete ID' and commit work
└── NO: Continue...

Am I stuck or confused?
├── YES: Run 'oos task list' to see all options
└── NO: Keep coding...

Is it end of day?
├── YES: Run end-of-day routine
└── NO: Keep working...
```

---

## 🆘 Common Daily Issues

**"No ready tasks"**
```bash
# Check what's blocking you
oos task list --status blocked

# Or see all tasks to reorganize
oos task list
```

**"I forgot what I was working on"**
```bash
# See your doing tasks
oos task list --status doing

# Or see recently updated
oos task list --sort updated --reverse --limit 5
```

**"Git conflicts"**
```bash
# Solve git issues first
git status
git pull --rebase
# Then continue with tasks
```

---

## 📈 Track Your Progress

**Weekly review:**
```bash
# What did I accomplish?
oos task list --status done --sort completed --reverse

# How many tasks completed?
oos task stats

# What's still pending?
oos task list --status todo,doing
```

**Monthly metrics:**
```bash
# Export all completed tasks
oos task export $(date +%Y-%m)-completed.jsonl --status done

# Review your productivity
# Look at patterns in your completed tasks
```

---

## 💡 The Philosophy

**Make it invisible:** The best workflow is one you don't have to think about.

**Five rules for daily success:**
1. **Start with `oos task ready`**
2. **End with committing and exporting**
3. **Create tasks immediately when you think of something**
4. **Don't over-organize - just capture and complete**
5. **Make it a habit, not a chore**

---

## 🎯 Minimum Viable Workflow

**If you only do 3 things each day:**
```bash
# Morning
oos task ready

# During work (as needed)
oos task create "new task"
oos task complete abc123

# End of day
git add . && git commit -m "daily work" && git push
```

**That's 80% of the value for 20% of the effort.**

---

*The goal is productivity, not bureaucracy. Use what helps, ignore what doesn't. The perfect workflow is the one you actually stick with.*