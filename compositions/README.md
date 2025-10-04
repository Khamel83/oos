# OOS Compositions - Unix Philosophy in Practice

## Everything is Module Composition

This directory contains **composition scripts** that combine focused modules into useful workflows. This is where "products" get built.

### Philosophy

Following the Unix Philosophy:
> "The power of a system comes more from the relationships among programs than from the programs themselves."

### Architecture Layers

```
🧩 MODULES (Level 1 - Pure Functions)
├── security/check_1password.sh     # Does ONE thing: check 1Password
├── python/check_uv.sh              # Does ONE thing: check uv
├── git/check_status.sh             # Does ONE thing: check git status

🏗️ COMPOSITIONS (Level 2 - Workflows)
├── start-coding.sh                 # Composes: validation workflow
├── deploy.sh                       # Composes: deployment workflow
├── test-suite.sh                   # Composes: testing workflow

🎯 PRODUCTS (Level 3 - User Features)
├── /start-coding (slash command)   # User entry point → compositions
├── /deploy (slash command)         # User entry point → compositions
├── /test-all (slash command)       # User entry point → compositions
```

### Benefits for AI Development

1. **AI writes modules** (single responsibility, easy to reason about)
2. **Humans design compositions** (workflow logic, error handling)
3. **Products emerge naturally** (slash commands just call compositions)

### Example: How a Product Gets Built

```bash
# 1. AI writes focused modules
modules/security/scan_vulnerabilities.sh   # Scans for vulns
modules/testing/run_pytest.sh              # Runs pytest
modules/deploy/push_to_staging.sh           # Deploys to staging

# 2. Human designs composition
compositions/pre-deploy.sh:
  scan_vulnerabilities && run_pytest && push_to_staging

# 3. Product emerges
/pre-deploy slash command → compositions/pre-deploy.sh
```

### Composition Patterns

1. **Sequential**: `module1 && module2 && module3`
2. **Conditional**: `module1 || fallback_module`
3. **Parallel**: `module1 & module2 & wait`
4. **Pipeline**: `module1 | module2 | module3`
5. **Best Effort**: Continue even if some modules fail

### This IS the Software Architecture

This modular composition pattern becomes:
- Your development workflow
- Your CI/CD pipeline
- Your testing strategy
- Your deployment process
- Your monitoring system

**Everything is just module composition.**