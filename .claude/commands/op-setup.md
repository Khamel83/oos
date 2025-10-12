---
argument-hint: <command-specific-args>
model: claude-3-5-sonnet-20241022
---

# op-setup

## Description
One-time setup to open 1Password vault and establish persistent secure pathway. After this setup, 1Password access is fully automated and persistent.

## Usage
```bash
/op-setup [command]
```

## Commands
- `setup` - Run complete one-time setup (default)
- `status` - Show current connection status

## Examples
```bash
/op-setup setup    # Run one-time setup
/op-setup status   # Check connection status
```

## What It Does
1. **Opens the vault once** - Using your existing service account or one-time authentication
2. **Establishes persistent pathway** - Creates secure, automated connection that persists
3. **Configures auto-renewal** - Connection automatically renews every 30 minutes
4. **Enables slash commands** - Makes `/op-secret` and `/op-get` always available

## Initial Requirements
You need ONE of these:
- Service account token set as `OP_SERVICE_ACCOUNT_TOKEN` environment variable
- One-time interactive authentication
- Access to "dev" vault with "bootstrap-env" item

## After Setup
No more manual authentication! You can use:
```bash
/op-secret status     # Check connection
/op-get secret-name   # Get any secret instantly
/op-secret bootstrap  # Load environment variables
```

## Security
- Connection persists for 1 hour with auto-renewal
- Service account provides least-privilege access
- No passwords stored in plain text
- Secure pathway established once, then reused

This is the **one-time manual step** to open the vault. After that, everything is fully automated!