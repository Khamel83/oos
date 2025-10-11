# MCP Connection Troubleshooting Guide

## 🚨 Common MCP Connection Issues

This document provides permanent solutions for the most common MCP (Model Context Protocol) connection problems in OOS.

## Issue #1: Server Name Mismatch

### Problem
```
Failed to reconnect to oos
```

### Root Cause
The MCP server name in `.claude/mcp_servers.json` doesn't match what the client expects.

**Common mismatches:**
- Config: `"oos-context-engineering"` → Client expects: `"oos"`
- Config: `"my-project-server"` → Client expects: `"my-project"`

### Permanent Solution
✅ **Rule: Always use simple, predictable server names**

```json
{
  "oos": {
    "command": "python3",
    "args": ["mcp_server.py"],
    "cwd": "/home/ubuntu/dev/oos"
  }
}
```

**Never use:** `oos-context-engineering`, `my-project-mcp`, `project-server`
**Always use:** `oos`, `my-project`, `app-name`

### Auto-Fix Script
```bash
#!/bin/bash
# bin/fix-mcp-server-name.sh
set -euo pipefail

# Fix common server name mismatches
if [[ -f ".claude/mcp_servers.json" ]]; then
    sed -i 's/"oos-context-engineering"/"oos"/g' .claude/mcp_servers.json
    sed -i 's/"my-project-server"/"my-project"/g' .claude/mcp_servers.json
    echo "✅ Fixed MCP server name in .claude/mcp_servers.json"
fi
```

## Issue #2: Missing MCP Configuration

### Problem
```
Error: No MCP servers configured
```

### Root Cause
`.claude/mcp_servers.json` doesn't exist or is malformed.

### Permanent Solution
✅ **Template-based MCP configuration**

Create `bin/setup-mcp-config.sh`:
```bash
#!/bin/bash
# bin/setup-mcp-config.sh
set -euo pipefail

PROJECT_NAME="${1:-$(basename "$(pwd)")}"
CONFIG_DIR=".claude"
CONFIG_FILE="$CONFIG_DIR/mcp_servers.json"

# Create config directory
mkdir -p "$CONFIG_DIR"

# Generate proper MCP configuration
cat > "$CONFIG_FILE" << EOF
{
  "${PROJECT_NAME}": {
    "command": "python3",
    "args": ["mcp_server.py"],
    "cwd": "$(pwd)",
    "env": {
      "PYTHONPATH": "$(pwd)/src:$(pwd)/venv/lib/python3.12/site-packages"
    }
  }
}
EOF

echo "✅ Created MCP configuration for project: $PROJECT_NAME"
```

## Issue #3: Python Path Issues

### Problem
```
ModuleNotFoundError: No module named 'mcp_server'
```

### Root Cause
Incorrect `PYTHONPATH` in MCP server configuration.

### Permanent Solution
✅ **Dynamic Python path detection**

Update MCP config generation:
```bash
#!/bin/bash
# Auto-detect Python paths
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
VENV_PATH="venv/lib/python${PYTHON_VERSION}/site-packages"

# Verify paths exist
if [[ ! -d "src" ]]; then
    echo "⚠️  Warning: src directory not found"
fi

if [[ ! -d "$VENV_PATH" ]]; then
    echo "⚠️  Warning: Virtual environment not found at $VENV_PATH"
    VENV_PATH="venv/lib/python3.12/site-packages"  # Fallback
fi
```

## Issue #4: MCP Server Not Running

### Problem
```
Connection refused to MCP server
```

### Root Cause
MCP server process failed to start or crashed.

### Permanent Solution
✅ **MCP server health monitoring**

Create `bin/mcp-health-check.sh`:
```bash
#!/bin/bash
# bin/mcp-health-check.sh
set -euo pipefail

PROJECT_NAME="${1:-$(basename "$(pwd)")}"
CONFIG_FILE=".claude/mcp_servers.json"

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "❌ MCP configuration missing: $CONFIG_FILE"
    exit 1
fi

# Check if MCP server is accessible
if command -v claude &> /dev/null; then
    if claude mcp list | grep -q "$PROJECT_NAME"; then
        echo "✅ MCP server '$PROJECT_NAME' is connected"
    else
        echo "❌ MCP server '$PROJECT_NAME' not connected"
        echo "Run: claude mcp add $PROJECT_NAME python3 mcp_server.py"
        exit 1
    fi
else
    echo "❌ Claude CLI not found"
    exit 1
fi
```

## Issue #5: Environment Variable Mismatches

### Problem
MCP server runs but can't access project resources.

### Root Cause
Missing or incorrect environment variables in MCP config.

### Permanent Solution
✅ **Environment validation**

Create `bin/validate-mcp-env.sh`:
```bash
#!/bin/bash
# bin/validate-mcp-env.sh
set -euo pipefail

CONFIG_FILE=".claude/mcp_servers.json"
PROJECT_NAME="${1:-$(basename "$(pwd)")}"

# Extract environment from config
if [[ -f "$CONFIG_FILE" ]]; then
    PYTHONPATH=$(jq -r ".\"$PROJECT_NAME\".env.PYTHONPATH" "$CONFIG_FILE" 2>/dev/null || echo "")
    CWD=$(jq -r ".\"$PROJECT_NAME\".cwd" "$CONFIG_FILE" 2>/dev/null || echo "")

    # Validate paths
    if [[ -n "$CWD" && ! -d "$CWD" ]]; then
        echo "❌ CWD directory not found: $CWD"
        exit 1
    fi

    if [[ -n "$PYTHONPATH" ]]; then
        IFS=':' read -ra PATHS <<< "$PYTHONPATH"
        for path in "${PATHS[@]}"; do
            if [[ ! -d "$path" ]]; then
                echo "⚠️  PYTHONPATH directory not found: $path"
            fi
        done
    fi

    echo "✅ MCP environment validated"
fi
```

## 🛠️ Comprehensive MCP Setup Script

### One-Command MCP Fix
Create `bin/setup-mcp.sh`:
```bash
#!/bin/bash
# bin/setup-mcp.sh - Complete MCP setup and validation
set -euo pipefail

PROJECT_NAME="${1:-$(basename "$(pwd)")}"
CONFIG_DIR=".claude"
CONFIG_FILE="$CONFIG_DIR/mcp_servers.json"

echo "🔧 Setting up MCP for project: $PROJECT_NAME"

# 1. Fix server name issues
if [[ -f "$CONFIG_FILE" ]]; then
    echo "📝 Fixing server name..."
    sed -i 's/"oos-context-engineering"/"oos"/g' "$CONFIG_FILE"
    sed -i 's/"my-project-server"/"my-project"/g' "$CONFIG_FILE"
fi

# 2. Create proper configuration if missing
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "📝 Creating MCP configuration..."
    mkdir -p "$CONFIG_DIR"

    # Detect Python environment
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    VENV_PATH="venv/lib/python${PYTHON_VERSION}/site-packages"

    if [[ ! -d "$VENV_PATH" ]]; then
        VENV_PATH="venv/lib/python3.12/site-packages"
    fi

    cat > "$CONFIG_FILE" << EOF
{
  "${PROJECT_NAME}": {
    "command": "python3",
    "args": ["mcp_server.py"],
    "cwd": "$(pwd)",
    "env": {
      "PYTHONPATH": "$(pwd)/src:$VENV_PATH"
    }
  }
}
EOF
fi

# 3. Validate configuration
echo "🔍 Validating MCP configuration..."
python3 -c "import json; json.load(open('$CONFIG_FILE'))" || {
    echo "❌ Invalid JSON in MCP configuration"
    exit 1
}

# 4. Check MCP server file
if [[ ! -f "mcp_server.py" ]]; then
    echo "⚠️  Warning: mcp_server.py not found"
fi

# 5. Test with Claude CLI
if command -v claude &> /dev/null; then
    echo "🔗 Testing MCP connection..."
    if claude mcp list | grep -q "$PROJECT_NAME"; then
        echo "✅ MCP server '$PROJECT_NAME' is connected"
    else
        echo "🔗 Adding MCP server to Claude..."
        claude mcp add "$PROJECT_NAME" python3 mcp_server.py --cwd "$(pwd)" || {
            echo "❌ Failed to add MCP server"
            echo "Manual command: claude mcp add $PROJECT_NAME python3 mcp_server.py"
        }
    fi
else
    echo "⚠️  Claude CLI not found - skipping connection test"
fi

echo "✅ MCP setup complete"
```

## 🔄 Integration with OOS Bootstrap

### Add to Bootstrap Process
Update `scripts/bootstrap.sh`:
```bash
# Near end of bootstrap, add MCP setup
echo "🔗 Setting up MCP connection..."
./bin/setup-mcp.sh "$PROJECT_NAME"

# Validate MCP works
if ./bin/mcp-health-check.sh "$PROJECT_NAME"; then
    echo "✅ MCP connection verified"
else
    echo "⚠️  MCP connection issues detected - see docs/MCP_TROUBLESHOOTING.md"
fi
```

## 📋 MCP Troubleshooting Checklist

### Quick Diagnosis
Run this script for comprehensive MCP health check:
```bash
#!/bin/bash
# bin/mcp-diagnose.sh
echo "🔍 MCP Connection Diagnosis"
echo "=========================="

PROJECT_NAME="${1:-$(basename "$(pwd)")}"
CONFIG_FILE=".claude/mcp_servers.json"

echo "📁 Checking configuration file..."
if [[ -f "$CONFIG_FILE" ]]; then
    echo "✅ Config file exists"
    echo "📝 Server name: $(jq -r "keys[0]" "$CONFIG_FILE")"
else
    echo "❌ Config file missing"
fi

echo ""
echo "🐍 Checking Python environment..."
if command -v python3 &> /dev/null; then
    echo "✅ Python3 available: $(python3 --version)"
else
    echo "❌ Python3 not found"
fi

echo ""
echo "🔗 Checking Claude CLI..."
if command -v claude &> /dev/null; then
    echo "✅ Claude CLI available"
    echo "📋 Connected servers:"
    claude mcp list || echo "❌ Failed to list MCP servers"
else
    echo "❌ Claude CLI not found"
fi

echo ""
echo "📁 Checking project structure..."
[[ -d "src" ]] && echo "✅ src directory exists" || echo "⚠️  src directory missing"
[[ -f "mcp_server.py" ]] && echo "✅ mcp_server.py exists" || echo "⚠️  mcp_server.py missing"
[[ -d "venv" ]] && echo "✅ Virtual environment exists" || echo "⚠️  Virtual environment missing"

echo ""
echo "🔧 Suggested fixes:"
echo "1. Run: ./bin/setup-mcp.sh $PROJECT_NAME"
echo "2. Run: ./bin/mcp-health-check.sh $PROJECT_NAME"
echo "3. Read: docs/MCP_TROUBLESHOOTING.md"
```

## 🚀 Best Practices for MCP Connections

### Development Guidelines

1. **Always use simple server names** - match project directory name
2. **Include MCP setup in bootstrap** - prevent configuration drift
3. **Validate paths dynamically** - handle different Python versions
4. **Provide clear error messages** - help users self-diagnose
5. **Document common issues** - create permanent reference materials

### Production Readiness

1. **Add MCP health checks to CI/CD**
2. **Monitor MCP server uptime**
3. **Version MCP configuration**
4. **Test MCP connection after deployments**
5. **Maintain troubleshooting documentation**

## 📞 Getting Help

If MCP issues persist:

1. **Run diagnostics**: `./bin/mcp-diagnose.sh`
2. **Check logs**: `claude --mcp-debug`
3. **Verify configuration**: `python3 -c "import json; print(json.load(open('.claude/mcp_servers.json')))"`
4. **Test manually**: `claude mcp add test-server python3 mcp_server.py`
5. **Consult this document**: `docs/MCP_TROUBLESHOOTING.md`

---

## Summary

The most common MCP issue is **server name mismatch**. The permanent solution is:

1. ✅ Use simple, predictable server names (match project directory)
2. ✅ Include MCP setup in OOS bootstrap
3. ✅ Provide diagnostic and fix scripts
4. ✅ Document common issues with clear solutions

This approach prevents the "Failed to reconnect to oos" error from recurring.