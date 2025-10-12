---
argument-hint: <arguments>
model: claude-3-5-sonnet-20241022
---

# /op-signin

Sign into 1Password CLI with extended session duration

```bash
./bin/op-session-manager.sh signin "$ARGUMENTS"
```

Signs into 1Password CLI with configurable session duration (default: 12h).
Uses the OOS session manager for reliable, persistent authentication.

Options:
- Duration: 1h, 12h, 24h, etc.

Examples:
- `/op-signin` - Sign in with default 12h duration
- `/op-signin 24h` - Sign in for 24 hours
- `/op-signin 1h` - Sign in for 1 hour

The session manager automatically handles:
- Extended session durations
- Auto-refresh capabilities
- Desktop app integration detection
- Session status tracking