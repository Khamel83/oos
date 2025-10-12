---
description: "🔒 Run comprehensive security audit and review"
argument-hint: <arguments>
allowed-tools: Bash
model: claude-3-5-sonnet-20241022
---


Run a comprehensive security audit and review of your OOS project

```bash
./bin/security_audit.sh "$ARGUMENTS"
```

Available security review commands:
- `scan` - Run full security scan (default)
- `permissions` - Check file permissions
- `secrets` - Scan for exposed secrets
- `compliance` - Generate compliance report
- `audit-logs` - Review security audit log

Add `--fix` to auto-fix issues:
```bash
/security-review scan --fix
```

Add `--report filename.json` to save report:
```bash
/security-review compliance --report security-report.json
```