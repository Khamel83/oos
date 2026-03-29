# Common Tasks - Exact Commands

## Starting a New Project

```bash
oos project create my-new-project
cd my-new-project
oos dev setup
```

**What this does:**
- Creates project directory
- Installs OOS tools
- Sets up environment

## Daily Development Workflow

### Check What You're Working On

```bash
oos task list
```

### Start a Task

```bash
oos task start <task-id>
```

### Check Environment Health

```bash
oos dev check
```

### Run Tests

```bash
oos test run
```

### Fix Code Issues

```bash
oos fix auto
```

### Security Scan

```bash
oos check security
```

### Complete a Task

```bash
oos task done <task-id>
```

## Task Management

### Create Task

```bash
oos task create "Task title" "Optional description"
```

### List All Tasks

```bash
oos task list
```

### Show Task Details

```bash
oos task show <task-id>
```

### Update Task

```bash
oos task update <task-id> --status doing
```

## When You Need Help

### See All Commands

```bash
oos help
```

### Help for Specific Command

```bash
oos help task
oos help dev
oos help setup
```

### Check Available Features

```bash
oos status
```

## Enable AI Features (Optional)

### 1. Get API Key

Visit https://openrouter.ai and create account

### 2. Add to .env

```bash
# Edit .env file
OPENROUTER_API_KEY=sk-your-key-here
```

### 3. Test AI

```bash
oos ai test
oos ai analyze "How can I optimize this code?"
```

## Common Problems

### "Command not found: oos"

```bash
# Re-run installation
curl -fsSL https://raw.githubusercontent.com/Khamel83/oos/master/install.sh | bash

# Or add to PATH
export PATH="$PATH:/path/to/oos/bin"
```

### "ModuleNotFoundError"

```bash
# Install Python dependencies
oos dev setup
```

### "Task database not found"

```bash
# Initialize environment
oos dev setup
```

## Update OOS

```bash
oos project update
```

---

**These are the 20% of commands you'll use 80% of the time.**
