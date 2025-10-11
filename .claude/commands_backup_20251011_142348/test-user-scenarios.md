---
description: "Run user acceptance testing (RUAT) - full command name"
tools: ["Bash"]
---

Run user acceptance testing (RUAT) - full command name

```bash
./bin/test-user-scenarios "$ARGUMENTS"
```

Full version of /ruat command. Tests features with GIVEN/WHEN/THEN scenario format to ensure user experience excellence.

Available scenarios:
- start-coding
- help-me
- screenshot
- provision
- validate-oos
- test-user-scenarios

Examples:
- `./bin/test-user-scenarios start-coding`
- `./bin/test-user-scenarios --all`