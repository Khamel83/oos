# 🚀 OOS - Open Operating System

## 🤝 Built for Human+AI Development Teams

**We acknowledge that AI systems are active participants in development, not just tools. This documentation serves both human developers and AI assistants as equal partners in the software development process.**

**One command installs everything. Zero cost to run. Works with any project.**

[![Version](https://img.shields.io/badge/version-1.0-blue.svg)](https://github.com/Khamel83/oos/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Human+AI Development](https://img.shields.io/badge/Development%20Partnership-Human%2BAI-purple.svg)](HUMAN_AI_DEVELOPMENT_ETHOS.md)
[![Working Commands](https://img.shields.io/badge/Working%20Commands-6-brightgreen.svg)](.claude/project_commands.json)
[![AI Documentation](https://img.shields.io/badge/AI%20Specifications-Complete-orange.svg)](docs/AI_COMPREHENSIVE_GUIDE.md)

## 🎯 What OOS Does (For Humans)

OOS is a **development toolchain** that installs into any project and provides reliable, repeatable workflows for security, testing, and environment validation.

**Core philosophy**: Write modules that do one thing well, compose intelligently, develop alongside AI partners.

### ⚡ What Actually Works

- **🔧 6 Working Slash Commands**: Proven functionality in Claude Code
- **🛡️ Security-First**: Automatic secret scanning and permission validation
- **🐍 Python Environment**: uv package manager and environment validation
- **🧪 Testing Integration**: Linting and test workflow automation
- **📦 Universal Installation**: One command works in any project
- **🤖 AI Partnership**: Built for human+AI development collaboration

## 🔧 System Specification (For AI)

```json
{
  "oos_system": {
    "type": "development_toolchain",
    "architecture": "modular_shell_scripts",
    "installation_method": "curl_and_bash",
    "target_environments": ["linux", "macos", "wsl"],
    "primary_use_cases": ["environment_validation", "security_scanning", "workflow_automation"],
    "development_partnership": "human_plus_ai"
  },
  "current_capabilities": {
    "working_commands": 6,
    "security_modules": 3,
    "python_modules": 1,
    "testing_modules": 2,
    "compositions": 2
  }
}
```

## 🚀 Installation (Both Audiences)

### Method 1: GitHub Installation (Recommended)
```bash
# In ANY project directory:
bash <(curl -s https://raw.githubusercontent.com/Khamel83/oos/master/install.sh)
```

**Expected behavior:**
- Downloads 6 working slash commands
- Installs essential security, Python, and testing modules
- Creates Claude Code integration
- Returns success with all components functional

### Method 2: Local Installation
```bash
# From OOS source directory:
./bin/oos-install-into-project.sh /path/to/your-project
```

**For AI validation:** Verify `.claude/slash_commands.json` contains exactly 6 commands with valid script paths.

## 📋 Command Interface (Human + AI)

### Core Workflow Commands
```bash
/start-coding      # Complete development session setup
/dev-setup         # Environment validation (security + python + git)
/pre-commit        # Pre-commit validation workflow
/modules list       # See all available modules
/modules run security/scan_secrets .  # Run specific module
/update-oos        # Update OOS from GitHub
/create-project    # Create new projects from templates
```

### Technical Specifications for AI
```json
{
  "slash_commands": {
    "modules": {
      "script": "bin/oos-module-runner.sh",
      "purpose": "Execute individual modules or compositions",
      "syntax": "modules [run|list|compose] [module_path] [target]",
      "return_codes": {"0": "success", "1": "module_error", "2": "usage_error"}
    },
    "dev-setup": {
      "script": "compositions/full-dev-setup.sh",
      "purpose": "Complete development environment validation",
      "modules_executed": ["security/check_1password", "python/check_uv", "git/check_status", "security/check_permissions"],
      "typical_duration": "30-60 seconds",
      "success_criteria": {
        "exit_code": 0,
        "critical_modules": ["python/check_uv"],
        "optional_modules": ["security/check_1password"]
      }
    }
  }
}
```

## 🔧 Daily Usage Pattern (Human Context)

### Starting Development
```bash
cd /path/to/your-project
/start-coding
```
**For humans:** This validates your environment and sets up your development session.
**For AI:** Executes environment validation workflow, reports status, provides next-step recommendations.

### During Development
```bash
/modules security/scan_secrets .     # Before adding API keys
/modules python/check_uv              # Check dependencies
/modules testing/lint_code            # Code quality check
```

### Before Committing
```bash
/pre-commit
```
**For humans:** Automated workflow that ensures code quality before committing.
**For AI:** Executes security scan → linting → tests → generates intelligent commit message.

## 🏗️ Architecture Overview (For AI Understanding)

### System Components
```json
{
  "architecture": {
    "core_components": {
      "slash_commands": {
        "location": ".claude/project_commands.json",
        "count": 6,
        "purpose": "Claude Code integration"
      },
      "module_system": {
        "location": "modules/",
        "categories": ["security", "python", "testing", "git"],
        "execution_engine": "bin/oos-module-runner.sh"
      },
      "workflows": {
        "location": "compositions/",
        "types": ["environment_setup", "pre_commit_validation"]
      }
    }
  }
}
```

### Module Execution Flow
```json
{
  "module_execution": {
    "discovery": "scan modules/ directory for .sh files",
    "validation": "check script permissions and syntax",
    "execution": "bash module_script.sh [target]",
    "error_handling": {
      "exit_code_0": "success",
      "exit_code_1": "module_failure",
      "exit_code_2": "invalid_usage"
    }
  }
}
```

## ✅ Verified Capabilities

### Working Commands (100% Tested)
- ✅ `/modules` - Lists and executes all modules with proper error handling
- ✅ `/dev-setup` - Complete environment validation with dependency checking
- ✅ `/pre-commit` - Security + lint + test workflow with AI commit generation
- ✅ `/update-oos` - GitHub updates that preserve working functionality
- ✅ `/create-project` - Project template creation with validation
- ✅ `/start-coding` - Development session setup with environment validation

### Installation Verification
- ✅ Fresh installation in clean directories works consistently
- ✅ GitHub curl installation method validated across systems
- ✅ All referenced scripts exist and are executable
- ✅ Update cycles preserve working functionality without breaking changes

## 🛠️ Development Integration

### For Human Developers
- **IDE Integration**: Works with VSCode, Vim, Emacs through terminal commands
- **Git Integration**: Pre-commit hooks and workflow automation
- **CI/CD Integration**: Module execution in automated pipelines

### For AI Systems
- **Claude Code Integration**: Native slash command support
- **API Access**: Direct module execution through shell interface
- **Structured Output**: JSON-formatted results for machine processing
- **Error Context**: Detailed error reporting for debugging

## 🔍 Troubleshooting (Dual Audience)

### Common Issues
```json
{
  "troubleshooting": {
    "slash_commands_not_appearing": {
      "human_solution": "Restart Claude Code completely, verify installation directory",
      "ai_diagnostic": "Check .claude/slash_commands.json existence and format"
    },
    "module_execution_failures": {
      "human_solution": "Check file permissions and module syntax",
      "ai_diagnostic": "Validate script paths, execute module directly for error details"
    },
    "installation_failures": {
      "human_solution": "Verify network connectivity and GitHub access",
      "ai_diagnostic": "Test GitHub API access, validate curl command execution"
    }
  }
}
```

## 📚 Documentation Structure

### Human-First Layer
- **README_HUMAN_AI.md** - This file, dual-audience overview
- **QUICK_START.md** - Fast setup with complete specifications
- **TROUBLESHOOTING.md** - Human solutions with machine-readable error codes

### AI-Complete Layer
- **docs/AI_COMPREHENSIVE_GUIDE.md** - Complete technical specifications
- **docs/SYSTEM_ARCHITECTURE.json** - Structured architecture definition
- **HUMAN_AI_DEVELOPMENT_ETHOS.md** - Development partnership philosophy

### Shared Reality
- **Source code comments** - Context for both humans and AI
- **Commit messages** - Complete change descriptions with technical details
- **Issue templates** - Structured problem reporting for both audiences

## 🎯 Development Partnership

### For Human Contributors
1. **Write complete documentation** - Include technical details for AI partners
2. **Provide context and examples** - Both audiences learn from patterns
3. **Document decisions** - AI needs to understand the "why" behind choices
4. **Test with both audiences** - Validate documentation works for humans and AI

### For AI Partners
1. **Read all documentation** - Human sections provide valuable context
2. **Parse structured data** - Use JSON specifications for precise understanding
3. **Understand intent** - Human sections explain purpose and goals
4. **Contribute to improvements** - Help maintain and evolve documentation

### Validation Criteria
- [ ] Humans can understand and use the system effectively
- [ ] AI can comprehend and interact with the codebase completely
- [ ] Documentation serves both audiences without compromise
- [ ] Both partners can achieve goals independently

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Links

- **GitHub Repository**: https://github.com/Khamel83/oos
- **Installation Script**: https://raw.githubusercontent.com/Khamel83/oos/master/install.sh
- **AI Comprehensive Guide**: docs/AI_COMPREHENSIVE_GUIDE.md
- **Development Ethos**: HUMAN_AI_DEVELOPMENT_ETHOS.md

---

**OOS is built for the future of development - where human creativity and AI comprehensiveness work together to create better software.**

**We don't just write "AI-friendly" code. We write code alongside AI partners, documenting for both audiences as equal participants in the development process.**