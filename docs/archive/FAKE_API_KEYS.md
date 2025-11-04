# Fake API Keys for Documentation

## Purpose
Use these FAKE API keys in documentation, examples, and tests to prevent accidental exposure of real credentials.

## OpenRouter Fake Keys
```bash
# Use these in documentation examples:
OPENROUTER_API_KEY="sk-or-v1-FAKE0000000000000000000000000000000000000000000000000000"
OPENROUTER_FALLBACK_KEY="sk-or-v1-EXAMPLE0000000000000000000000000000000000000000000000000"
OPENROUTER_PROJECT_KEY="sk-or-v1-DEMO00000000000000000000000000000000000000000000000000000"
```

## Perplexity Fake Keys
```bash
# Use these in documentation examples:
PERPLEXITY_API_KEY="pplx-FAKE0000000000000000000000000000000000000000"
```

## ZAI Fake Keys
```bash
# Use these in documentation examples:
ZAI_API_KEY="00000000000000000000000000000000.FAKE_EXAMPLE_TOKEN"
```

## Usage Rules

### ✅ DO use fake keys for:
- Documentation examples
- README files
- Tutorial content
- Code comments showing format
- Test files (when not using real API)

### ❌ NEVER use real keys in:
- Documentation files
- README content
- Code examples in markdown
- Committed test files
- Any file that goes into git

## Pattern Recognition
These fake keys follow the real format but use obviously fake values:
- OpenRouter: `sk-or-v1-` + FAKE/EXAMPLE/DEMO + zeros
- Perplexity: `pplx-` + FAKE + zeros
- ZAI: zeros + `.FAKE_` + descriptive text

## Git Pre-commit Hook Pattern
Update `.gitignore` patterns to catch real keys but allow fake ones:
```bash
# Block real patterns but allow FAKE/EXAMPLE/DEMO
^(?!.*FAKE)(?!.*EXAMPLE)(?!.*DEMO)sk-or-v1-[A-Za-z0-9]{40,}
^(?!.*FAKE)(?!.*EXAMPLE)(?!.*DEMO)pplx-[A-Za-z0-9]{40,}
```

This ensures we can use fake keys in docs while preventing real key leaks.