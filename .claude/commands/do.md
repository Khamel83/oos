---
argument-hint: <arguments>
model: claude-3-5-sonnet-20241022
---

# /do

Universal agentic entry point - just describe what you want to accomplish.

The AI automatically routes your request to the appropriate systematic workflow.

## Usage

```bash
./bin/agentic-daily.sh do "$ARGUMENTS"
```

## Examples

```bash
/do "build a web scraper for news articles"
/do "fix my authentication errors"
/do "learn Docker containerization"
/do "complete the user dashboard feature"
```

## What It Does

**Intelligent Intent Recognition:**
- **Build/Create** → Routes to `/idea-to-done` workflow
- **Fix/Solve** → Routes to `/quick-solve` workflow
- **Learn/Research** → Routes to `/learn` workflow
- **Complete/Finish** → Routes to `/complete` workflow

**Automatic Orchestration:**
1. Analyzes your request
2. Searches Archon knowledge base
3. Applies systematic OOS patterns
4. Guides you through execution
5. Captures learnings

**Natural Language Interface:**
No need to remember complex syntax - just describe what you want in plain English.

This is your **primary daily command** for agentic workflow.