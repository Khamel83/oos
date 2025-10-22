# 📚 Complete OOS Command Reference

## Command Ecosystem Overview

**Total Commands: 55** (10 consolidated + 45 legacy + help system)

### Understanding the Command Structure

OOS uses a **dual-layer command system**:

1. **10 Consolidated Commands** - Modern, organized interface
2. **45 Legacy Commands** - Still available for backward compatibility
3. **Built-in Claude Code Commands** - Default Claude Code functionality

---

## 🚀 10 Consolidated Commands (Primary Interface)

These are the **recommended commands** for daily use.

### `/dev` - Development Environment
**Consolidates:** `/start-coding`, `/modules`, `/dev-setup`, `/startup-check`, `/reload-commands`

```bash
/dev setup              # Start systematic development session
/dev check              # Validate development environment
/dev modules            # Run security/python/git modules
/dev refresh            # Reload Claude Code commands
```

### `/test` - Testing & Validation
**Consolidates:** `/test-debug`, `/test-connection`, `/test-user-scenarios`, `/validate`

```bash
/test scenarios         # Run user-acceptance testing
/test debug             # Test command functionality
/test connection        # Test system connections
/test all               # Run all tests
```

### `/fix` - Code Quality & Optimization
**Consolidates:** `/auto-fix`, `/optimize`, `/doc-check`, `/smart-commit`

```bash
/fix auto               # Automatically fix code issues
/fix optimize           # Optimize for performance/tokens
/fix docs               # Check documentation quality
/fix commit             # Generate intelligent commit messages
```

### `/think` - AI-Powered Problem Solving
**Consolidates:** `/brain-dump`, `/clarify`, `/solve`, `/meta-ai`

```bash
/think dump             # Process rambling input
/think clarify          # Clarify vague requirements
/think solve            # Solve complex problems
/think meta             # Meta-level analysis
```

### `/workflow` - Process Orchestration
**Consolidates:** `/agentic-workflow`, `/complete-workflow`, `/idea-to-done`

```bash
/workflow complete      # Complete A→B→C→D workflow
/workflow idea          # Quick idea-to-completion
/workflow daily         # Daily routine workflow
```

### `/project` - Infrastructure Management
**Consolidates:** `/create-project`, `/provision`, `/update-oos`, `/oos-refresh`

```bash
/project create         # Create new project
/project provision      # AI-powered infrastructure
/project update         # Update OOS from GitHub
/project refresh        # Refresh OOS installation
```

### `/op` - 1Password Operations
**Consolidates:** All `/op-*` commands

```bash
/op status              # Check authentication status
/op signin              # Sign in to 1Password
/op get [item]          # Retrieve password/item
/op session             # Manage sessions
```

### `/archon` - Knowledge Base & Project Management
**Consolidates:** All `/archon-*` commands

```bash
/archon research        # Search knowledge base
/archon status          # Show project status
/archon tasks           # Manage tasks
```

### `/task` - Task Management
**Consolidates:** `/archon-task-start`, `/archon-complete`

```bash
/task start             # Start working on tasks
/task complete          # Mark tasks complete
/task list              # Show all tasks
```

### `/check` - System Validation
**Consolidates:** `/security-review`, `/context-stats`

```bash
/check security         # Run security audit
/check context          # Show context statistics
/check all              # Complete system validation
```

---

## 🛠️ 45 Legacy Commands (Backward Compatibility)

**These still work but redirect to consolidated commands.**

### Development Commands
```bash
/start-coding           # → /dev setup
/modules [name]         # → /dev modules
/dev-setup              # → /dev setup
/startup-check          # → /dev check
/reload-commands        # → /dev refresh
```

### AI & Workflow Commands
```bash
/help-me [args]         # → /think clarify
/brain-dump [text]      # → /think dump
/clarify [text]         # → /think clarify
/solve [problem]        # → /think solve
/meta-ai [prompt]       # → /think meta
/agentic-workflow       # → /workflow complete
/complete-workflow      # → /workflow complete
/idea-to-done           # → /workflow complete
```

### Quality & Optimization Commands
```bash
/auto-fix               # → /fix auto
/optimize               # → /fix optimize
/doc-check              # → /fix docs
/smart-commit           # → /fix commit
```

### Project Commands
```bash
/create-project [name]  # → /project create
/provision              # → /project provision
/update-oos             # → /project update
/oos-refresh            # → /project refresh
```

### 1Password Commands
```bash
/op-status              # → /op status
/op-signin              # → /op signin
/op-get [item]          # → /op get
/op-session             # → /op session
/op-session-automated   # → /op session automated
/op-setup               # → /op setup
/op-secret [name]       # → /op secret
```

### Archon Commands
```bash
/archon-status          # → /archon status
/archon-research         # → /archon research
/archon-task-start      # → /task start
/archon-complete        # → /task complete
```

### Testing Commands
```bash
/test-debug             # → /test debug
/test-connection        # → /test connection
/test-user-scenarios    # → /test scenarios
/validate               # → /check all
```

### Security & Context Commands
```bash
/security-review        # → /check security
/context-stats          # → /check context
```

### Utility Commands
```bash
/screenshot             # Take and analyze screenshot
/pre-commit             # Run pre-commit checks
/do [command]           # Execute command
/ruat                   # User acceptance testing
/morning                # Morning routine
/evening                # Evening routine
```

---

## 🆚 Built-in Claude Code Commands

**These are Claude Code's default commands, always available:**

```bash
/model                  # Switch AI models
/status                 # Show Claude Code status
/commit                 # Git commit interface
/diff                   # Show git differences
/branch                 # Git branch management
/merge                  # Git merge
/push                   # Git push
/pull                   # Git pull
/add                    # Git add files
/reset                  # Git reset
/stash                  # Git stash
/log                    # Git log
```

---

## 📖 Command Discovery System

### Primary Help Command
```bash
/help                   # Show help overview
/help all               # List all 55+ commands
/help [command]         # Get help with specific command
/help [topic]           # Topic-based help
```

### Available Help Topics
```bash
/help installation      # Installation and setup
/help commands          # Command system overview
/help tasks             # Task management
/help workflows         # Development workflows
/help troubleshooting   # Common issues
/help migration         # Moving from legacy to consolidated
```

### Self-Documentation
Every OOS command includes:
- **Description** of what it does
- **Consolidation info** (what it replaces)
- **Usage examples**
- **Argument hints**

---

## 🎯 Recommended Daily Workflow

### For New Users
```bash
/help                   # Get oriented
/help installation      # If new to OOS
/dev setup              # Start development session
/workflow complete      # Run complete workflow
```

### For Daily Development
```bash
/dev check              # Validate environment
/task start             # Start work on tasks
/fix auto               # Fix any issues found
/help-me [problem]      # When stuck on something
```

### For System Maintenance
```bash
/project update         # Keep OOS current
/check security         # Security audit
/test scenarios         # Validate user workflows
```

---

## 📊 Command Statistics

- **Total OOS Commands:** 55
- **Consolidated Commands:** 10 (recommended)
- **Legacy Commands:** 45 (backward compatible)
- **Built-in Claude Commands:** ~15
- **Available in Every Project:** ~70 commands total

### Command Categories
- **Development:** 8 commands
- **Testing & Validation:** 6 commands
- **Quality & Optimization:** 8 commands
- **AI & Problem Solving:** 7 commands
- **Workflow & Process:** 6 commands
- **Project Management:** 6 commands
- **Authentication:** 8 commands
- **Task Management:** 4 commands
- **Security & Auditing:** 4 commands
- **Utilities:** 8 commands

---

## 🔍 Command Examples by Use Case

### Starting a New Project
```bash
# Recommended approach
/project create my-project
/dev setup
/help installation

# Legacy approach (still works)
/create-project my-project
/start-coding
```

### Daily Development Session
```bash
# Modern workflow
/dev check
/task start
/fix auto
/workflow complete

# Legacy workflow (still works)
/startup-check
/archon-task-start
/auto-fix
/complete-workflow
```

### When You Need Help
```bash
/help                   # General help
/help all               # See everything
/help [specific]        # Command-specific help
/think clarify [problem] # AI help with problems
```

---

## 🎉 Summary

**OOS provides a comprehensive command ecosystem with:**

1. **10 modern consolidated commands** - Simple, organized interface
2. **45 legacy commands** - Complete backward compatibility
3. **Built-in Claude Code commands** - Native functionality
4. **Smart help system** - `/help` for discovery and assistance
5. **Self-documenting** - Every command explains itself

**Key Insight:** The 10 consolidated commands provide a simpler interface while maintaining full compatibility with all 55 legacy commands. Users can gradually migrate or continue using whatever commands they prefer.

**Migration Path:** Run `/help migration` to learn how to move from legacy to consolidated commands.