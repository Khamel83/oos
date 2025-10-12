---
argument-hint: <command-specific-args>
model: claude-3-5-sonnet-20241022
---

# op-get

## Description
Quick access to 1Password secrets. Shortcut for `/op-secret get`.

## Usage
```bash
/op-get <secret-name> [field]
```

## Examples
```bash
/op-get database-password          # Get database password
/op-get api-key username          # Get API key username
/op-get "aws-secret"              # Get AWS secret
```

## Parameters
- `secret-name` - Name of the secret in 1Password
- `field` - Field to retrieve (default: password)

## Notes
This command automatically manages 1Password authentication and provides instant access to secrets from your "dev" vault.