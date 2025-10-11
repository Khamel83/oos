---
description: "Run comprehensive OOS validation - code-documentation alignment and quality checks"
tools: ["Bash"]
---

Run comprehensive OOS validation

```bash
./bin/validate-oos "$ARGUMENTS"
```

Validates:
- Code-documentation alignment
- Functional testing
- Integration testing
- Simplicity analysis
- Recursive User-Acceptance Testing integration

Generates actionable reports with prioritized improvements for maintaining OOS quality and consistency.

Usage examples:
- `./bin/validate-oos` - Run full validation
- `./bin/validate-oos --report` - Generate report only
- `./bin/validate-oos --help` - Show help