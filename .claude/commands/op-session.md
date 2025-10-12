# 1Password Session Management

Manage persistent 1Password CLI sessions for OCI VM environments

```bash
./bin/op-session-manager.sh "$ARGUMENTS"
```

This command provides comprehensive 1Password CLI session management specifically designed for OCI VMs where the desktop app is not available. Features include:

- **Persistent Sessions**: Maintains 12-hour (configurable) sessions
- **Auto-Refresh**: Automatically detects expired sessions
- **Secure Storage**: Session tokens stored securely in ~/.op_session
- **Status Monitoring**: Clear visibility into authentication state
- **Graceful Fallbacks**: Handles connection issues elegantly

## Usage Examples

```bash
# Ensure you're signed in (most common)
/op-session ensure

# Force new signin with 24-hour session
OP_SESSION_DURATION=24h /op-session signin

# Check current status
/op-session status

# Sign out and cleanup
/op-session signout

# Refresh expired session
/op-session refresh
```

## Integration with OOS

The session manager integrates with:
- Development gate checks
- Smart commit workflows
- Environment variable access
- Secret management operations

Perfect for OCI VMs where desktop app integration isn't available.