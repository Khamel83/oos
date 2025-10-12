---
argument-hint: <command-specific-args>
model: claude-3-5-sonnet-20241022
---

# op-session-automated

## Description
Provides automated 1Password authentication for non-interactive environments using service accounts or session tokens.

## Usage
```bash
/op-session-automated [command]
```

## Commands
- `ensure` - Ensure valid authentication exists (most common)
- `status` - Show current authentication status
- `authenticate` - Force authentication attempt
- `help` - Show help documentation

## Examples
```bash
/op-session-automated ensure      # Ensure authentication exists
/op-session-automated status      # Check status
```

## Setup
For automated environments, set up a service account:
```bash
# Create service account with appropriate permissions
op service-account create my-agent --vault MyVault:read_items

# Set environment variable with the token
export OP_SERVICE_ACCOUNT_TOKEN="your-service-account-token"

# Test automated authentication
/op-session-automated ensure
```

## Integration
This command integrates with the main session manager:
```bash
# The regular op-session command now tries automated auth first
/op-session ensure
```