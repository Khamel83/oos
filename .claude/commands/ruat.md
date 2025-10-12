---
description: "Run user acceptance testing (RUAT) - mandatory user experience validation"
argument-hint: <arguments>
allowed-tools: Bash
model: claude-3-5-sonnet-20241022
---


Run user acceptance testing (RUAT) - Recursive User-Acceptance Testing

```bash
./bin/test-user-scenarios "$ARGUMENTS"
```

RUAT validates that features work from a REAL USER perspective:
- Does it work how users actually use it?
- Are edge cases handled gracefully?
- Is the user experience intuitive?
- Do integrations feel seamless?
- Are error messages helpful?

This is MANDATORY before marking any task "done" in Archon to prevent "technically correct but terrible UX" features.

Usage examples:
- `./bin/test-user-scenarios start-coding` - Test specific feature
- `./bin/test-user-scenarios --all` - Test all features
- `./bin/test-user-scenarios --create new-feature` - Create scenario template
- `./bin/test-user-scenarios --help` - Show help