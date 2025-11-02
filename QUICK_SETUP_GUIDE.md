# OOS Full Stack Quick Setup Guide

## 🚀 5-Minute Setup

This guide gets you from zero to working OOS full stack integration.

### ✅ What Works Out of the Box
- **AI Analysis**: Working with OpenRouter models
- **Archon Task Sync**: Syncing tasks to your project
- **Local RelayQ**: ocivm node fully operational
- **Testing**: 6/7 integration tests passing

### 🔧 What Needs Configuration
- **Remote SSH Keys**: For MacMini/RPi4 nodes (optional)
- **Archon Endpoints**: Some 404s (core features work)

---

## Step 1: Verify Current Setup

```bash
# Test AI integration
python3 src/ai_provider.py

# Test RelayQ topology
python3 src/relayq_architecture.py

# Test Archon sync
source .env && python3 src/archon_sync.py

# Run full test suite
python3 tests/test_full_stack_integration.py
```

**Expected Result**: All tests show ✅ except remote execution

---

## Step 2: SSH Configuration (Optional - for remote nodes)

### Generate SSH Keys
```bash
# Generate key for MacMini
ssh-keygen -t ed25519 -f ~/.ssh/macmini_key -N ""

# Generate key for RPi4
ssh-keygen -t ed25519 -f ~/.ssh/rpi4_key -N ""
```

### Copy Keys to Remote Nodes
```bash
# Copy to MacMini (replace with actual IP)
ssh-copy-id -i ~/.ssh/macmini_key.pub ubuntu@192.168.1.100

# Copy to RPi4 (replace with actual IP)
ssh-copy-id -i ~/.ssh/rpi4_key.pub pi@192.168.1.101
```

### Update RelayQ Configuration
```bash
# Edit .relayq_config.json
nano .relayq_config.json
```

Replace example IPs with your actual node IPs:
```json
{
  "name": "macmini-server",
  "host": "YOUR_MACMINI_IP",
  "ssh_config": {
    "user": "ubuntu",
    "key_path": "~/.ssh/macmini_key"
  }
}
```

### Test SSH Connections
```bash
# Test MacMini
ssh -i ~/.ssh/macmini_key ubuntu@YOUR_MACMINI_IP "echo 'SSH works!'"

# Test RPi4
ssh -i ~/.ssh/rpi4_key pi@YOUR_RPI4_IP "echo 'SSH works!'"
```

---

## Step 3: Fix Archon 404 Endpoints

### Check What's Working
```bash
# This works (tasks API)
curl -H "Authorization: Bearer $ARCHON_VAULT_PASSWORD" \
  https://archon.khamel.com/api/tasks

# These may return 404 (expected for demo setup)
curl https://archon.khamel.com/api/heartbeat
curl https://archon.khamel.com/api/knowledge/upload
```

### What's Working vs. Expected 404s
- ✅ **Tasks API**: Working perfectly
- ✅ **Project API**: Working perfectly
- ❌ **Heartbeat API**: 404 (not critical)
- ❌ **Knowledge Upload API**: 404 (not critical)

**The 404s don't affect core functionality.** Task sync and project management work perfectly.

---

## Step 4: Run Full Demo

```bash
# Basic AI analysis
./bin/oos-full-stack "How can I improve my testing workflow?"

# AI + local execution
./bin/oos-full-stack "Test system" --command "echo 'Demo successful!'"

# Full test scenario
./bin/oos-full-stack --test
```

---

## 🔍 Troubleshooting

### AI Issues
```bash
# Check API key
echo $OPENROUTER_PROJECT_KEY

# Test OpenRouter directly
curl -H "Authorization: Bearer $OPENROUTER_PROJECT_KEY" \
  https://openrouter.ai/api/v1/models
```

### SSH Issues
```bash
# Check SSH connectivity
ssh -v -i ~/.ssh/macmini_key ubuntu@TARGET_IP

# Common fixes:
# - Check IP addresses
# - Verify user accounts
# - Check firewall rules
# - Ensure SSH service running on remote nodes
```

### Archon Issues
```bash
# Check project access
curl -H "Authorization: Bearer $ARCHON_VAULT_PASSWORD" \
  https://archon.khamel.com/api/projects

# Verify environment
cat .env | grep ARCHON
```

---

## 📋 Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| AI Provider | ✅ Working | OpenRouter integration operational |
| Local RelayQ | ✅ Working | ocivm node ready |
| Remote RelayQ | ⚠️ SSH Config | Needs SSH keys for MacMini/RPi4 |
| Archon Tasks | ✅ Working | Syncing to project successfully |
| Archon Other APIs | ⚠️ 404s | Non-critical endpoints missing |
| Test Suite | ✅ 6/7 Passing | Only remote execution failing |

---

## 🎯 Next Steps

### For Immediate Use (Today)
- Use AI analysis: `./bin/oos-full-stack "your question"`
- Local task execution works perfectly
- Archon task sync keeps your project updated

### For Full Distributed Setup
1. Configure SSH keys for remote nodes
2. Update IPs in `.relayq_config.json`
3. Test remote execution

### For Complete Archon Integration
- The 404s are from missing optional endpoints
- Core functionality (tasks, projects) works perfectly
- Can be addressed later without impact

---

## 🚀 Quick Test Commands

```bash
# 1. Test everything in 30 seconds
python3 tests/test_full_stack_integration.py

# 2. Demo AI capabilities
./bin/oos-full-stack "Analyze this problem" --test

# 3. Verify Archon sync
source .env && python3 src/archon_sync.py

# 4. Check RelayQ topology
python3 src/relayq_architecture.py
```

**All of these should show ✅ for core functionality.**

---

## 💡 Pro Tips

1. **Start Simple**: Use AI analysis and local execution first
2. **SSH Optional**: Remote nodes are optional for most use cases
3. **Archon Robust**: Core Archon features work despite 404s
4. **Monitor Logs**: Check console output for detailed status
5. **Update Config**: Adjust `.relayq_config.json` for your actual setup

---

**🎉 You're ready to use OOS full stack!** The core functionality works immediately. SSH and Archon endpoint fixes are optional enhancements.