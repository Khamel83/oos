# OOS Philosophy Correction - CRITICAL

## The Misunderstanding

**What I Built (WRONG):**
- Tiers as "optional features for others"
- "Core is default, Enhanced/Advanced are optional"
- User manually edits .env files
- "Enable AI later if you want"
- Treating it like a product with feature tiers

**What You Actually Want (RIGHT):**
- **ALL tiers are YOUR complete workflow**
- Setup ONCE (everything), use FOREVER
- No manual .env editing - wizard handles it
- Tiers are for graceful degradation, not gatekeeping
- This is YOUR tool, others can use it after it's perfect for you

## The Real Philosophy

```
This is NOT a product with "basic" and "premium" tiers.
This is YOUR WORKFLOW TOOL with three types of services:

1. Local (Core) - Always works (tasks, dev tools)
2. API (Enhanced) - Your AI (configured once, works forever)
3. Server (Advanced) - Your knowledge base (configured once, works forever)

Tiers mean: "Is service reachable right now?"
NOT: "Have you enabled this feature yet?"
```

## How It Should Actually Work

### First Time EVER (per machine):

```bash
oos setup

# Wizard prompts ONCE for EVERYTHING:

=== OOS Complete Setup ===

1. Python Environment
   [auto-installs uv, dependencies]
   ✅ Ready

2. AI Provider (Your Workflow)
   Choose: OpenRouter / OpenAI / Anthropic
   API Key: [paste once]
   ✅ Tested and working

3. Archon (Your Brain)  
   URL: https://archon.khamel.com
   API Key: [paste once]
   ✅ Connected and tested

4. Deployment (Your Workflow)
   Vercel: [configure once]
   OCI VM: IP, SSH key [configure once]
   ✅ All configured

=== Setup Complete ===

Configuration saved to: ~/.config/oos/credentials
These settings work in ALL projects forever.
You should never need to configure OOS again.
```

### From Then On (FOREVER):

```bash
# In ANY project:
oos task list          # Just works
oos ai analyze "x"     # Just works
oos archon research    # Just works (or says "Archon offline")
oos deploy vercel      # Just works

# Status shows what's REACHABLE, not what's "enabled":
oos status

OOS Status
==========
✅ CORE: Task tracking, dev tools
✅ AI: OpenRouter configured and responding
⚠️  ARCHON: Configured but offline (check server)
✅ DEPLOY: Vercel and OCI configured
```

## Key Changes Needed

### 1. Global Configuration

**Current:** Per-project `.env` files
**Should Be:** `~/.config/oos/credentials` (once per machine)

```bash
# ~/.config/oos/credentials (chmod 600)
OPENROUTER_API_KEY=sk-...
ARCHON_URL=https://archon.khamel.com
ARCHON_API_KEY=...
OCI_VM_IP=...
OCI_SSH_USER=...
OCI_SSH_KEY=~/.ssh/oci_key
VERCEL_CONFIGURED=true
```

### 2. Setup Wizard (Already Created)

**File:** `bin/oos-setup-wizard`
**Purpose:** Run ONCE, configure EVERYTHING
**User Experience:**
- Prompts for all services
- Tests each connection
- Saves to global location
- Reports what's working
- Never need to configure again

### 3. Tier Detection Rewrite

**Current:** "Is it enabled?" (wrong mindset)
**Should Be:** "Is it reachable?" (right mindset)

```bash
oos_check_enhanced() {
    # Load global credentials
    source ~/.config/oos/credentials
    
    # Check if configured (not "enabled")
    if [[ -n "$OPENROUTER_API_KEY" ]]; then
        echo "available"
    else
        echo "not-configured"   # Not "unavailable"
    fi
}

oos_check_advanced() {
    source ~/.config/oos/credentials
    
    if [[ -n "$ARCHON_URL" ]]; then
        # Try to reach it
        if curl -sf "$ARCHON_URL/api/health" &>/dev/null; then
            echo "available"          # Service is up
        else
            echo "configured-offline"  # Configured but unreachable
        fi
    else
        echo "not-configured"
    fi
}
```

### 4. Commands Always Load Global Credentials

```bash
# bin/oos-enhanced/ai.sh
source ~/.config/oos/credentials

# If not configured, friendly message:
if [[ -z "$OPENROUTER_API_KEY" ]]; then
    echo "AI not configured yet. Run: oos setup"
    exit 1
fi

# Otherwise just use it
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" ...
```

### 5. Status Command Shows Reality

```bash
oos status

OOS Status
==========
✅ CORE: Always ready
✅ AI: OpenRouter responding (11ms)
⚠️  ARCHON: Offline (configured at https://archon.khamel.com)
✅ DEPLOY: Vercel + OCI ready

Everything configured works across all projects.
```

### 6. Documentation Rewrite

**QUICKSTART.md:**
```markdown
# Start Using OOS

## One-Time Setup (5 minutes)

```bash
# Install OOS
git clone https://github.com/Khamel83/oos
cd oos

# Setup EVERYTHING once
oos setup
```

Wizard will ask for:
- AI provider (OpenRouter/OpenAI/Anthropic) + key
- Archon URL + key (if you have it)
- Deployment targets (Vercel, OCI VM)

After this, OOS works in ALL projects.

## Daily Usage

```bash
# Any project
oos task create "Build feature"
oos ai analyze "How to optimize this?"
oos archon research "authentication patterns"
oos deploy vercel
```

No configuration needed. Ever.
```

## Implementation Checklist

- [ ] Create `bin/oos-setup-wizard` (✅ Done)
- [ ] Rewrite `lib/oos-tier-detection.sh` to use global credentials
- [ ] Update all commands to load from `~/.config/oos/credentials`
- [ ] Add `oos setup` command to main CLI
- [ ] Change "enable" language to "configure once" language
- [ ] Update all documentation with new philosophy
- [ ] Remove all `.env` references for user configuration
- [ ] Test: setup once, works in multiple projects
- [ ] Ensure graceful degradation when services offline

## The Core Insight

**"Nothing is 'optional' unless it's optional to ME"**

If YOU use it daily, it's not optional. It's part of YOUR workflow.
Others might not use Archon - that's fine.
But for YOU, it's configured and expected to work.

**"Setup once, never think about it again"**

Not "enable features as you discover them."
But "configure everything once, use forever."

**"Environmental variables are friction"**

User should never touch .env files.
Setup wizard handles it once, globally.

## Why This Matters

**Current OOS feels like:**
"Here's the basic version. Want more? Enable these optional features..."

**YOUR OOS should feel like:**
"Here's MY complete workflow. Setup once. Use forever."

**The difference:**
- Product with tiers vs. Personal tool with services
- Enable features vs. Configure once
- Per-project config vs. Global config
- "Optional" vs. "Offline right now"

## Next Steps

1. Finish rewriting tier detection
2. Update all commands to use global credentials
3. Integrate setup wizard into main flow
4. Rewrite all docs with new philosophy
5. Test across multiple projects
6. Ensure "configure once, works everywhere"

---

**The Goal:**
Think once (setup), plan once (configure), use forever (everywhere).
