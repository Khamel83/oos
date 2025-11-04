# Complete Command Reference

## oos task - Task Management

```
oos task list                   List all tasks
oos task create <title>         Create new task
oos task start <id>             Start working on task
oos task done <id>              Mark task complete
oos task show <id>              Show task details
oos task update <id> [opts]     Update task
```

**Tier:** Core (always available)

## oos dev - Development Environment

```
oos dev setup                   Complete development setup
oos dev check                   Validate environment
oos dev modules [name]          Run development modules
```

**Tier:** Core (always available)

## oos project - Project Management

```
oos project create <name>       Create new project with OOS
oos project update              Update OOS from GitHub
```

**Tier:** Core (always available)

## oos test - Testing

```
oos test run                    Run all tests
oos test run <path>             Run specific test
oos test debug                  Run tests in debug mode
oos test scenarios              Run user scenario tests
```

**Tier:** Core (always available)

## oos fix - Code Fixes

```
oos fix auto                    Automatic formatting and fixes
oos fix optimize                Optimize for tokens/performance
```

**Tier:** Core (always available)

## oos check - Validation

```
oos check security              Run security checks
oos check all                   Run all validation checks
```

**Tier:** Core (always available)

## oos ai - AI Features

```
oos ai analyze <query>          Analyze with AI
oos ai test                     Test AI connection
```

**Tier:** Enhanced (requires API key)
**Setup:** `oos help setup`

## oos archon - Knowledge Base

```
oos archon research <query>     Search knowledge base
oos archon status               Check Archon connection
```

**Tier:** Advanced (requires Archon server)
**Setup:** `oos help archon`

## oos (meta commands)

```
oos status                      Show available features
oos help [command]              Show help
oos version                     Show version
```

## Aliases

Many commands have short aliases:

```
oos task list    = oos task ls
oos task create  = oos task new
oos task done    = oos task complete
oos task start   = oos task begin
```

## Environment Variables

OOS reads configuration from `.env`:

```bash
# Enhanced Tier
OPENROUTER_API_KEY=sk-your-key
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=sk-your-key

# Advanced Tier
ARCHON_URL=https://archon-server
ARCHON_API_KEY=your-key
```

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Feature not available (wrong tier)

## Examples by Use Case

### Solo Developer (Core Only)

```bash
oos dev setup
oos task create "Build feature"
oos task start <id>
oos test run
oos fix auto
oos task done <id>
```

### With AI Features (Enhanced)

```bash
# Add API key to .env first
oos ai analyze "Optimize this function"
oos ai test
```

### With Team Knowledge Base (Advanced)

```bash
# Configure Archon first
oos archon research "authentication patterns"
oos archon status
```

---

**For detailed usage examples, see [USAGE.md](USAGE.md)**
