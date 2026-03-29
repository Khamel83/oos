# Setup Optional Features

## You Already Have: Core Features ✅

**Working right now:**
- Task tracking (`oos task`)
- Project management (`oos project`)
- Development tools (`oos dev`)
- Testing utilities (`oos test`)
- Code fixes (`oos fix`)
- Security checks (`oos check`)

**No setup needed for these.**

---

## Enable: AI Features (Enhanced Tier)

AI-powered analysis, code suggestions, and automation.

### Step 1: Get API Key

Choose one provider:

**OpenRouter (Recommended - Access to many models):**
1. Visit https://openrouter.ai
2. Create account
3. Generate API key

**OpenAI:**
1. Visit https://platform.openai.com
2. Create account
3. Generate API key

**Anthropic:**
1. Visit https://console.anthropic.com
2. Create account
3. Generate API key

### Step 2: Add to .env

```bash
# Edit .env file in OOS root
nano .env

# Add your key (choose one):
OPENROUTER_API_KEY=sk-or-v1-your-key-here
# OR
OPENAI_API_KEY=sk-your-key-here
# OR
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Step 3: Test

```bash
oos ai test
# Should show: AI connection OK

oos status
# Should show: ✅ ENHANCED: AI features, advanced search
```

### Step 4: Use AI Features

```bash
oos ai analyze "How can I optimize my database queries?"
oos ai analyze "Explain this error message"
```

**Cost:** Most providers have free tier or pay-as-you-go

---

## Enable: Archon Integration (Advanced Tier)

Archon provides persistent knowledge base, cross-project learning, and distributed task management.

### What Is Archon?

Archon is a separate service that acts as:
- **Knowledge Base:** RAG search across all your docs and code
- **Project Management:** Cross-project task tracking
- **Learning System:** Captures patterns and decisions
- **MCP Server:** Claude Code integration

### Step 1: Install Archon

```bash
# Clone Archon repository
git clone https://github.com/Khamel83/archon
cd archon

# Follow Archon's installation guide
./install.sh
```

### Step 2: Start Archon Server

```bash
# In archon directory
./bin/start-archon

# Archon will run at: https://archon.khamel.com:3737
# Or locally: http://localhost:8000
```

### Step 3: Configure OOS

```bash
# Edit .env in OOS root
nano .env

# Add Archon configuration:
ARCHON_URL=https://archon.khamel.com
ARCHON_API_KEY=your-archon-api-key
ARCHON_PROJECT_ID=your-project-uuid
```

### Step 4: Test Connection

```bash
oos archon status
# Should show: Archon connected: https://archon.khamel.com

oos status
# Should show: ✅ ADVANCED: Archon knowledge base, distributed computing
```

### Step 5: Use Archon Features

```bash
# Search knowledge base
oos archon research "authentication patterns"

# Archon MCP tools work in Claude Code automatically
```

**Note:** Archon requires server infrastructure. Use cloud hosting or local server.

---

## Verify Your Setup

```bash
oos status
```

Should show:
- ✅ CORE: Always available
- ✅ ENHANCED: If API keys configured
- ✅ ADVANCED: If Archon configured

---

## Troubleshooting

### AI features not working

```bash
# Check .env file exists and has API key
cat .env | grep API_KEY

# Test specific provider
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  https://openrouter.ai/api/v1/models

# Check Python environment
oos dev check
```

### Archon not connecting

```bash
# Test Archon server directly
curl https://archon.khamel.com/api/health

# Check firewall/network
ping archon.khamel.com

# Verify .env configuration
cat .env | grep ARCHON
```

### Dependencies missing

```bash
# Reinstall Python environment
oos dev setup

# Or manually:
cd /path/to/oos
uv sync
```

---

## Next Steps

Once features are enabled:
- Read [USAGE.md](USAGE.md) for common tasks
- Check [REFERENCE.md](REFERENCE.md) for all commands
- See [examples/](examples/) for usage examples

---

**Remember:** Core features work without any setup. Enhanced and Advanced tiers are optional.
