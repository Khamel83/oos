---
description: "🔒 Run comprehensive security audit and review"
tools: ["Bash"]
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