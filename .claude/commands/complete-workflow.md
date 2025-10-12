---
description: "Run complete idea-to-completion workflow A→B→C→D systematic process"
argument-hint: <arguments>
allowed-tools: Bash
model: claude-3-5-sonnet-20241022
---


Run complete idea-to-completion workflow A→B→C→D

```bash
./bin/complete-workflow.sh "$ARGUMENTS"
```

The complete systematic workflow includes:
A: Development environment setup (/start-coding)
B: Development with RUAT validation
C: Comprehensive validation (/validate)
D: User scenario testing (/ruat)
E: Pre-commit validation
F: Smart commit
G: Infrastructure provisioning (/provision)
H: Final validation and completion

Usage examples:
- `./bin/complete-workflow.sh plan` - Show workflow plan
- `./bin/complete-workflow.sh interactive "My App"` - Interactive mode
- `./bin/complete-workflow.sh auto "API Service"` - Automatic mode

This systematic process ensures technical correctness AND user experience excellence.