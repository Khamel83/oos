# op-secret

## Description
Access 1Password secrets through a persistent, automated connection. Manages secrets from the "dev" vault with always-on authentication.

## Usage
```bash
/op-secret [command] [options]
```

## Commands
- `init` - Initialize persistent connection (run on startup)
- `get <secret> [field]` - Get specific secret value (default field: password)
- `list` - List all available secrets in dev vault
- `bootstrap` - Load bootstrap environment variables
- `status` - Show connection status
- `close` - Close connection

## Examples
```bash
/op-secret init                    # Initialize persistent connection
/op-secret get "database-password" # Get database password
/op-secret get "api-key" username   # Get API key username
/op-secret list                    # List all secrets
/op-secret bootstrap                # Load environment variables
/op-secret status                  # Check connection status
```

## Integration
This command provides automated access to your "dev" vault secrets without manual authentication. The connection persists for 1 hour and automatically renews as needed.

## Default Configuration
- Vault: `dev`
- Bootstrap Item: `bootstrap-env`
- Connection Duration: 1 hour (auto-renews)

## Environment Variables
Set these to override defaults:
```bash
export OP_VAULT="your-vault"
export OP_BOOTSTRAP_ITEM="your-bootstrap-item"
```