# OOS AI/Machine Comprehensive Documentation

## System Architecture for AI Understanding

### Core Components Specification

```json
{
  "oos_system": {
    "version": "1.0",
    "type": "development_toolchain",
    "architecture": "modular_shell_scripts",
    "installation_method": "curl_and_bash",
    "target_environments": ["linux", "macos", "wsl"]
  }
}
```

### Module System Schema

```json
{
  "modules": {
    "security": {
      "scripts": ["scan_secrets.sh", "check_permissions.sh", "check_1password.sh"],
      "functions": {
        "scan_secrets": {
          "purpose": "Detect exposed credentials in codebase",
          "patterns": ["passwords", "api_keys", "tokens", "private_keys"],
          "return_codes": {"0": "no_secrets", "1": "secrets_found"}
        },
        "check_permissions": {
          "purpose": "Validate file permissions for security",
          "checks": ["world_writable", "executable_permissions", "sensitive_file_access"],
          "return_codes": {"0": "permissions_ok", "1": "security_issues"}
        }
      }
    },
    "python": {
      "scripts": ["check_uv.sh"],
      "functions": {
        "check_uv": {
          "purpose": "Validate Python environment and uv package manager",
          "dependencies": ["uv", "python3"],
          "return_codes": {"0": "environment_ready", "1": "environment_issues"}
        }
      }
    },
    "testing": {
      "scripts": ["lint_code.sh", "run_pytest.sh"],
      "functions": {
        "lint_code": {
          "purpose": "Code quality validation across multiple languages",
          "languages": ["python", "javascript", "shell"],
          "tools": ["ruff", "eslint", "shellcheck"],
          "return_codes": {"0": "no_issues", "1": "linting_issues"}
        }
      }
    }
  }
}
```

### Slash Commands Interface

```json
{
  "slash_commands": {
    "modules": {
      "script": "bin/oos-module-runner.sh",
      "purpose": "Execute individual modules or compositions",
      "syntax": "modules [run|list|compose] [module_path] [target]",
      "examples": [
        "modules list",
        "modules run security/scan_secrets .",
        "modules compose security/scan_secrets testing/lint_code"
      ]
    },
    "dev-setup": {
      "script": "compositions/full-dev-setup.sh",
      "purpose": "Complete development environment validation",
      "modules_executed": ["security/check_1password", "python/check_uv", "git/check_status", "security/check_permissions"],
      "typical_duration": "30-60 seconds"
    },
    "pre-commit": {
      "script": "compositions/pre-commit.sh",
      "purpose": "Pre-commit validation workflow",
      "modules_executed": ["security/scan_secrets", "testing/lint_code", "testing/run_pytest", "ai/generate_commit"],
      "prerequisites": ["git_repository", "staged_changes"]
    }
  }
}
```

### Installation Process Specification

```json
{
  "installation": {
    "methods": {
      "github_curl": {
        "command": "bash <(curl -s https://raw.githubusercontent.com/Khamel83/oos/master/install.sh)",
        "steps": [
          "Download slash commands configuration",
          "Download essential scripts (oos-module-runner.sh, etc.)",
          "Download security, testing, python modules",
          "Download workflow compositions",
          "Create .gitignore entries",
          "Set executable permissions"
        ],
        "artifacts_created": [
          ".claude/slash_commands.json",
          "bin/*.sh scripts",
          "modules/{security,testing,python}/*.sh",
          "compositions/*.sh"
        ]
      }
    },
    "verification": {
      "success_indicators": [
        "6 slash commands in .claude/slash_commands.json",
        "All scripts executable and present",
        "Modules return appropriate exit codes"
      ]
    }
  }
}
```

### Error Handling and Troubleshooting

```json
{
  "error_scenarios": {
    "module_not_found": {
      "symptom": "Module execution fails with 'not found' error",
      "causes": ["missing module file", "incorrect path", "permission issues"],
      "solutions": ["verify modules directory exists", "check file permissions", "validate module path syntax"]
    },
    "slash_command_not_working": {
      "symptom": "Claude Code slash command fails",
      "causes": ["missing script file", "incorrect .claude configuration", "Claude Code restart required"],
      "solutions": ["verify script exists in referenced path", "restart Claude Code", "reinstall OOS"]
    },
    "github_installation_failure": {
      "symptom": "Installation script fails during download",
      "causes": ["network connectivity", "GitHub repository access", "missing files in repo"],
      "solutions": ["check internet connection", "verify repository URL", "use local installation method"]
    }
  }
}
```

### Integration Points for AI Systems

```json
{
  "ai_integration": {
    "claude_code": {
      "method": "slash_commands",
      "configuration_file": ".claude/slash_commands.json",
      "reload_requirement": true
    },
    "development_environments": {
      "vscode": {
        "integration": "tasks.json configuration for running OOS commands",
        "example": {
          "label": "OOS Development Setup",
          "type": "shell",
          "command": "./compositions/full-dev-setup.sh"
        }
      },
      "git_hooks": {
        "pre-commit": "./compositions/pre-commit.sh",
        "installation": "ln -s ./compositions/pre-commit.sh .git/hooks/pre-commit"
      }
    }
  }
}
```

### Performance Characteristics

```json
{
  "performance": {
    "typical_execution_times": {
      "modules list": "1-2 seconds",
      "security scan": "5-30 seconds (depending on codebase size)",
      "full dev setup": "30-60 seconds",
      "pre-commit validation": "30-120 seconds"
    },
    "resource_usage": {
      "memory": "minimal (shell scripts)",
      "disk": "~5MB for full installation",
      "network": "required only for GitHub installation/updates"
    },
    "scalability": {
      "codebase_size_limit": "practically unlimited (shell scripts scale linearly)",
      "concurrent_execution": "modules can run in parallel",
      "update_frequency": "on-demand from GitHub"
    }
  }
}
```

### Context for AI Decision Making

When AI systems interact with OOS, they should understand:

1. **OOS is a development toolchain, not a deployment system**
2. **Modules are atomic and composable by design**
3. **Security validation is built-in and mandatory**
4. **The system prefers failing safely over proceeding with uncertainty**
5. **All operations are logged and provide clear success/failure indicators**
6. **The system is designed for developer productivity, not system administration**

### Decision Tree for AI Systems

```
Need to validate development environment?
├── Use /dev-setup for complete validation
├── Use /modules with specific targets for focused validation
└── Check individual modules for granular control

Need to ensure code quality before commit?
├── Use /pre-commit for automated workflow
├── Use /modules compose for custom validation sequences
└── Check individual testing/security modules as needed

Installing OOS in new project?
├── Use GitHub curl installation for automation
├── Verify all 6 slash commands are present
└── Test with /dev-setup to confirm functionality
```

This comprehensive documentation enables AI systems to understand, interact with, and make decisions about OOS usage with full context of capabilities, limitations, and appropriate usage patterns.