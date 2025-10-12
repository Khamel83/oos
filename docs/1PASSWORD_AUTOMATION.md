# 1Password Automation Guide for Non-Interactive Environments

This guide covers setting up 1Password authentication for automated environments like CI/CD pipelines, agents, and VMs where interactive authentication is not possible.

## Overview

For automated/agent use cases, 1Password provides **Service Accounts** which are designed specifically for programmatic access without requiring interactive authentication.

## Recommended Solution: Service Account Authentication

### Why Service Accounts?

- ✅ **No interactive authentication required**
- ✅ **Designed for automation and CI/CD**
- ✅ **Fine-grained permissions (vault-level access control)**
- ✅ **Can be revoked independently of user accounts**
- ✅ **No need for 2FA codes or password prompts**
- ✅ **Works consistently across all environments**

### Setup Instructions

#### Step 1: Create a Service Account

First, create a service account with appropriate permissions:

```bash
# Create service account with read access to specific vaults
op service-account create my-automation-agent \
  --vault "Production:read_items" \
  --vault "Development:read_items,write_items"
```

**Important:** Save the token immediately! 1Password only shows it once.

#### Step 2: Configure Environment Variables

Set the service account token as an environment variable:

```bash
# Set the service account token
export OP_SERVICE_ACCOUNT_TOKEN="your-service-account-token-here"
```

For persistent configuration, add this to your shell profile (`.bashrc`, `.zshrc`, etc.) or environment file.

#### Step 3: Use Automated Authentication

Now you can use the automated authentication system:

```bash
# Ensure authentication exists (creates session if needed)
./bin/op-auth-automated.sh ensure

# Check authentication status
./bin/op-auth-automated.sh status

# Force authentication renewal
./bin/op-auth-automated.sh authenticate
```

## Integration with OOS Session Manager

The OOS session manager now integrates with automated authentication:

```bash
# This will now try automated authentication first
./bin/op-session-manager.sh ensure
```

## Service Account Permissions

### Available Permissions

- `read_items` - Read items from vault (default)
- `write_items` - Create and modify items (requires read_items)
- `share_items` - Share items with others (requires read_items)

### Examples

```bash
# Read-only access to production vault
op service-account create readonly-agent --vault Production:read_items

# Read/write access to development vault
op service-account create dev-agent --vault Development:read_items,write_items

# Multiple vaults with different permissions
op service-account create fullstack-agent \
  --vault Production:read_items \
  --vault Development:read_items,write_items \
  --vault Staging:read_items

# Service account with expiry (for temporary access)
op service-account create temp-agent --vault Production:read_items --expires-in=24h

# Service account that can create vaults
op service-account create vault-admin --vault Production:read_items --can-create-vaults
```

## Security Best Practices

### 1. Principle of Least Privilege

Only grant the minimum permissions necessary:
```bash
# Good: Read-only access to specific vault
op service-account create deploy-agent --vault Production-secrets:read_items

# Bad: Full access to everything
# Avoid using admin privileges for automation
```

### 2. Token Management

- **Never commit tokens to version control**
- **Use environment variables or secret management systems**
- **Rotate tokens regularly**
- **Revoke compromised tokens immediately**

### 3. Vault Organization

Organize vaults by purpose and environment:
```
├── Production-secrets (read-only for agents)
├── Development-secrets (read-write for developers)
├── CI-CD-secrets (read-write for pipelines)
└── Monitoring-secrets (read-only for monitoring)
```

## Alternative Methods (If Service Accounts Aren't Available)

### Method 1: Pre-configured Session Token

For development/testing environments:

```bash
# 1. Set up account interactively once
op account add --address my.1password.com --email user@example.com --signin

# 2. Session will be managed automatically by the session manager
./bin/op-session-manager.sh ensure
```

### Method 2: Environment-based Configuration

```bash
# Set account details in environment
export OP_ACCOUNT_ADDRESS="my.1password.com"
export OP_ACCOUNT_EMAIL="user@example.com"
export OP_PASSWORD="password"  # Not recommended for production

# The session manager will attempt to use these
./bin/op-session-manager.sh signin
```

## Troubleshooting

### Common Issues

1. **"Service account token not found"**
   - Set `OP_SERVICE_ACCOUNT_TOKEN` environment variable
   - Or save token to `~/.op_service_account`

2. **"Failed to authenticate with service account"**
   - Check if token is valid and not expired
   - Verify service account has proper vault permissions
   - Ensure vault names match exactly

3. **"Permission denied"**
   - Service account may not have access to requested vault
   - Check vault name spelling and permissions

### Debug Commands

```bash
# Check authentication status
./bin/op-auth-automated.sh status

# Test service account directly
OP_SERVICE_ACCOUNT_TOKEN="your-token" op whoami

# List available vaults
op vault list

# Test specific vault access
op item list --vault "Vault-Name"
```

## Integration Examples

### CI/CD Pipeline

```yaml
# GitHub Actions example
- name: Setup 1Password Authentication
  run: |
    export OP_SERVICE_ACCOUNT_TOKEN="${{ secrets.OP_SERVICE_ACCOUNT_TOKEN }}"
    ./bin/op-auth-automated.sh ensure

- name: Retrieve secrets
  run: |
    op item get "database-credentials" --field password
```

### Docker Container

```dockerfile
# Dockerfile
COPY ./bin/op-auth-automated.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/op-auth-automated.sh

# Entry point script
#!/bin/bash
export OP_SERVICE_ACCOUNT_TOKEN="${OP_SERVICE_ACCOUNT_TOKEN}"
./bin/op-auth-automated.sh ensure
exec "$@"
```

### Systemd Service

```ini
[Unit]
Description=My Service with 1Password Integration
After=network.target

[Service]
Type=oneshot
Environment=OP_SERVICE_ACCOUNT_TOKEN=/run/secrets/op-token
ExecStart=/usr/local/bin/op-auth-automated.sh ensure
ExecStart=/usr/local/bin/my-actual-service
```

## Migration from Interactive to Automated

If you currently have interactive authentication set up:

1. **Create service account** with appropriate permissions
2. **Test service account** in parallel with existing setup
3. **Update applications** to use service account token
4. **Remove interactive credentials** once migration is complete

## Conclusion

Service accounts provide the most reliable, secure, and automated way to use 1Password in non-interactive environments. They eliminate the need for:

- Interactive password prompts
- 2FA code entry
- Manual session management
- Account credential sharing

For any automated or agent-based workflow, service accounts should be the preferred authentication method.