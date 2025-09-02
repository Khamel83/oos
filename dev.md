# dev log

## 2025-09-02 - Project completion
- Added comprehensive documentation suite
- README.md with quick start and overview
- docs/ directory with specialized guides:
  - ENV_TEMPLATE.md - 1Password environment setup
  - ONEPASSWORD.md - Step-by-step 1Password configuration  
  - MCP.md - MCP registration and runner details
  - TROUBLESHOOTING.md - Common issues and solutions
  - OPERATIONS.md - Daily usage and maintenance
- SECURITY.md - Security posture and threat model
- LICENSE - MIT license
- Project now ready for distribution and use

## 2025-09-02 - Bootstrap & Daily Ops Reference

OOS — Bootstrap & Daily Ops (Final Notes)

This is the "look it up later" guide. It only covers what isn't obvious from the code.

⸻

What you have working
    •    1Password CLI auth, pulling env into .env
    •    Archon MCP reachable at http://localhost:8051/mcp
    •    Claude/Gemini/Qwen runners wired to MCP & OpenRouter
    •    OpenRouter keys auto-rotated: first valid key becomes OPENAI_API_KEY via .env.active
    •    GitHub repo Khamel83/oos with secrets scrubbed and .gitignore in place

⸻

Repo layout (what matters)

oos/
├─ .agents/
│  └─ runners/
│     ├─ run_claude.sh   # starts Claude CLI with project MCPs
│     ├─ run_gemini.sh   # starts Gemini CLI with project MCPs
│     └─ run_qwen.sh     # starts Qwen CLI with project MCPs
├─ bin/
│  ├─ safe_source_env.sh # robust .env loader → .env.export
│  └─ select_or_key.sh   # picks OPENAI_API_KEY → .env.active
├─ bootstrap.sh          # one-command new-project bootstrapper
├─ .gitignore            # keeps secrets out of git
└─ (docs, dev notes, etc.)


⸻

One-time prerequisites (already done)
    •    1Password CLI installed & signed in
    •    gh installed & logged in
    •    Archon server running locally (localhost:8051)

⸻

Daily use (every new shell)

# 1) 1Password session
eval "$(op signin)"

# 2) go to the project
cd /home/ubuntu/dev/oos

# 3) (re)load env + select a valid OpenRouter key
bin/safe_source_env.sh .env
bin/select_or_key.sh .env .env.active

# 4) launch your runner
.agents/runners/run_claude.sh   # inside Claude: /mcp
# or:
.agents/runners/run_gemini.sh
.agents/runners/run_qwen.sh

Quick checks

# Archon should answer fast with 200/405
curl -4 -I http://localhost:8051/mcp

# Runners see MCPs (archon ✓, context7 ✓)
claude mcp list


⸻

New project bootstrap (the whole point)

# Choose a folder & name
mkdir -p /home/ubuntu/dev/Not-Fake-Project

# Run bootstrap with your 1P item (vault=Private, item=bootstrap-env, field=env)
OP_VAULT="Private" OP_ITEM="bootstrap-env" OP_FIELD="env" \
ORG="Khamel83" VIS="public" \
/home/ubuntu/dev/oos/bootstrap.sh "Not-Fake-Project" "/home/ubuntu/dev/Not-Fake-Project"

That script:
    •    Creates the project skeleton
    •    Pulls the env from 1Password into .env
    •    Wires MCPs (archon + context7)
    •    Initializes a public GitHub repo under your account (unless you change VIS)
    •    Sets up runners that auto-pick a valid OpenRouter key

⸻

Managing secrets (1Password)

Single source of truth = 1Password item named bootstrap-env in vault "Private", field env.

What to store in that env field:
    •    Everything from your .env, including:
    •    ARCHON_URL (use http://localhost:8051/mcp unless your HTTPS endpoint is truly reachable)
    •    OPENAI_API_BASE_URL
    •    OPENROUTER_KEYS (comma-separated) or OPENROUTER_API_KEY
    •    FIRECRAWL_API_KEY, SUPABASE_*, MODEL, etc.
    •    Optional: GITHUB_PAT, CONTEXT7_API_KEY
    •    No quotes, no stray lines. Unix newlines only.

Sync local → 1Password (optional, when you edit .env locally):

eval "$(op signin)"
cd /home/ubuntu/dev/oos
tr -d '\r' < .env | op item edit "bootstrap-env" --vault "Private" env=-

Pull 1Password → local (fresh shell or machine):

eval "$(op signin)"
cd /home/ubuntu/dev/oos
op item get "bootstrap-env" --vault "Private" --fields env > .env
sed -i 's/\r$//' .env


⸻

Switching Archon endpoint
    •    Local (recommended):

ARCHON_URL=http://localhost:8051/mcp


    •    Remote (only if confirmed reachable over TLS):

sed -i 's|^ARCHON_URL=.*|ARCHON_URL=https://archon.khamel.com:8051/mcp|' .env
bin/safe_source_env.sh .env
claude mcp remove archon || true
claude mcp add --transport http archon https://archon.khamel.com:8051/mcp
claude mcp list



If remote shows ✗, go back to localhost.

⸻

OpenRouter key rotation (automatic)
    •    Put multiple keys in:

OPENROUTER_KEYS=sk-or-AAA,sk-or-BBB,sk-or-CCC


    •    The runner writes the first valid key to .env.active as:

OPENAI_API_KEY=sk-or-...


    •    If you change keys, rerun:

bin/select_or_key.sh .env .env.active



⸻

GitHub push protection & history scrubbing

If GitHub blocks a push with GH013 (secret detected):
    1.    Make sure .env and friends are ignored (already set):

.env
.env.*
!.env.template

    2.    Remove the secret from history (you already used this; keep for future):

sudo apt install -y git-filter-repo || python3 -m pip install --user git-filter-repo
git filter-repo --force \
  --path .env \
  --path .env.active \
  --path .env.export \
  --invert-paths
git remote add origin https://github.com/Khamel83/oos.git  # if removed
git push -u origin --force HEAD:master


⸻

Common fixes
    •    op signin warning
Run exactly:

eval "$(op signin)"


    •    .env: line XX / weird errors
Normalize & rebuild:

sed -i 's/\r$//' .env
bin/safe_source_env.sh .env
bin/select_or_key.sh .env .env.active


    •    Stray : No such file or directory or quotes around values
Clean up .env (remove that line, remove accidental leading/trailing quotes).
    •    MCP shows archon ✗
Use localhost:

sed -i 's|^ARCHON_URL=.*|ARCHON_URL=http://localhost:8051/mcp|' .env
bin/safe_source_env.sh .env
claude mcp remove archon || true
claude mcp add --transport http archon http://localhost:8051/mcp
claude mcp list


    •    OpenRouter 401/429
Rotate to next key:

bin/select_or_key.sh .env .env.active



⸻

Minimal "do this now" recap

# new shell
eval "$(op signin)"
cd /home/ubuntu/dev/oos
bin/safe_source_env.sh .env
bin/select_or_key.sh .env .env.active
.agents/runners/run_claude.sh   # then /mcp

For a new project:

mkdir -p /home/ubuntu/dev/Not-Fake-Project
OP_VAULT="Private" OP_ITEM="bootstrap-env" OP_FIELD="env" \
ORG="Khamel83" VIS="public" \
/home/ubuntu/dev/oos/bootstrap.sh "Not-Fake-Project" "/home/ubuntu/dev/Not-Fake-Project"

Sleep easy — this is set.
