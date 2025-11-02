# 🔒 OOS Security Setup - MANDATORY

## Critical Security Issue Resolution

**This document addresses the recurring API key exposure incidents and ensures they never happen again.**

## The Problem
API keys were repeatedly committed to the public repository because:
1. Pre-commit hooks weren't installed
2. .env files were accidentally tracked
3. Documentation used real keys instead of fake ones
4. No mandatory security validation during setup

## The Solution - 3-Step Security Setup

### Step 1: Install Pre-Commit Security Hook (MANDATORY)

**Run this command IMMEDIATELY after OOS installation:**

```bash
# Install the security hook (this should be automatic)
./bin/prevent_api_key_commits.sh --install

# Verify it's working
git commit --dry-run -m "test" || echo "✅ Security hook is active"
```

**What this does:**
- Blocks any commit containing real API keys
- Allows safe placeholder values like `sk-or-v1-FAKE...`
- Provides helpful error messages when keys are detected

### Step 2: Verify Environment Setup (MANDATORY)

**Check your .env configuration:**

```bash
# Verify .env is gitignored
git check-ignore .env
# Should output: .env

# Check for any tracked .env files
git ls-files | grep -E "\.env$"
# Should be empty (no output)

# Verify your API key is set but not tracked
grep -o ".{10}$" .env | head -1
# Should show last 10 chars of your key
```

### Step 3: Run Security Audit (MANDATORY)

**Before any development work:**

```bash
# Check for any existing API keys in repository
./bin/prevent_api_key_commits.sh --check-all

# Should output: "✅ No API keys detected in tracked files"
# If it finds issues, fix them before proceeding
```

## Automated Setup Integration

**This security setup is now integrated into OOS commands:**

```bash
# Security check is built into:
/dev setup           # Validates security before development
/project create      # Installs security hooks automatically
/check security      # Runs comprehensive security audit
```

## Documentation Standards

**When writing documentation, ALWAYS use fake API keys:**

```bash
# ✅ CORRECT - Use fake keys in docs
OPENROUTER_API_KEY="sk-or-v1-FAKE0000000000000000000000000000000000000000000000000000"

# ❌ WRONG - Never use real keys
# OPENROUTER_API_KEY="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"

# ✅ CORRECT - Use environment reference
export OPENROUTER_API_KEY  # Loaded from .env
```

**Reference:** See `docs/FAKE_API_KEYS.md` for standard fake key patterns.

## Quick Security Checklist

Before any git commit, verify:

- [ ] Pre-commit hook is installed (`.git/hooks/pre-commit` exists)
- [ ] .env file is gitignored (not in `git status`)
- [ ] No real API keys in documentation
- [ ] All examples use fake keys or environment references
- [ ] Security audit passes: `./bin/prevent_api_key_commits.sh --check-all`

## Emergency Procedures

**If an API key is accidentally exposed:**

1. **Immediately rotate the key** at the provider (OpenRouter, etc.)
2. **Remove the key from repository history** (if needed)
3. **Verify security hooks are properly installed**
4. **Run security audit to check for other exposures**

**If security hook is blocking a legitimate commit:**

1. **Review the detected pattern carefully**
2. **Ensure it's actually safe (UUID, markdown anchor, etc.)**
3. **Add the pattern to SAFE_KEYS in `bin/prevent_api_key_commits.sh`**
4. **Re-run the commit**

## Integration with CI/CD

**GitHub Actions will also check for API keys:**

```yaml
# This is automatically added to .github/workflows/
- name: Security Scan
  run: ./bin/prevent_api_key_commits.sh --check-all
```

## Dev Gate Integration

**The development gate now includes security validation:**

```bash
# Dev gate checks:
1. Pre-commit hook installed
2. .env properly configured
3. No API keys in repository
4. Security audit passes

# If any fail, dev gate blocks development commands
```

## For OOS Maintainers

**When adding new features that use APIs:**

1. **Never hardcode keys in examples**
2. **Always use environment variables**
3. **Add fake key patterns to documentation**
4. **Update security patterns if needed**
5. **Test security hooks before merging**

## Auto-Fix Commands

**If security issues are detected:**

```bash
# Auto-fix common security issues
/fix security         # Removes hardcoded keys, installs hooks

# Check security status
/check security       # Comprehensive security audit

# Emergency bypass (use sparingly)
DEV_GATE_BYPASS=true git commit -m "emergency fix"
```

---

**This security setup is now MANDATORY for all OOS installations and will be enforced by the development gate system.**