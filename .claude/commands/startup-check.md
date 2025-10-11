---
description: "Startup health check and command refresh - runs automatically to ensure OOS is ready"
tools: ["Bash"]
---

OOS Startup Health Check - ensures slash commands are fresh and working

```bash
./bin/startup-check.sh "$ARGUMENTS"
```

This startup check ensures:
- Commands are always current with OOS version
- Any fuckups are detected immediately
- Validation passes before commands are used
- Clear feedback on command status

Run this manually or set it as your startup command to ensure OOS is always ready.