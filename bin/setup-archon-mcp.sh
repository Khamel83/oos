#!/bin/bash

echo "=========================================="
echo "OOS ARCHON MCP SETUP"
echo "=========================================="
echo ""

# Configuration
ARCHON_IP="100.103.45.61"
ARCHON_PORT="8051"
ARCHON_ENDPOINT="http://${ARCHON_IP}:${ARCHON_PORT}/mcp"

echo "🔧 Setting up Archon MCP connection..."
echo "Endpoint: $ARCHON_ENDPOINT"
echo ""

# Check if claude command exists
if ! command -v claude &> /dev/null; then
    echo "❌ Claude Code not found in PATH"
    echo "Please install Claude Code first"
    exit 1
fi

echo "✅ Claude Code found"

# Remove any existing archon config
echo "🧹 Removing any existing Archon MCP configuration..."
claude mcp remove archon 2>/dev/null || true

# Add new config with direct IP
echo "➕ Adding Archon MCP server..."
if claude mcp add --transport http archon "$ARCHON_ENDPOINT"; then
    echo "✅ Archon MCP server added successfully"
else
    echo "❌ Failed to add Archon MCP server"
    exit 1
fi

echo ""
echo "🧪 Testing connection..."

# Test connection
if claude mcp list | grep -q "✓ Connected"; then
    echo "✅ Archon MCP connected successfully!"
    echo ""
    echo "📊 Connection Status:"
    claude mcp list | grep archon
    echo ""
    echo "🎉 Setup complete! You can now use Archon tools in Claude Code."
    echo ""
    echo "Next steps:"
    echo "1. Run: ./bin/test_archon_integration.sh"
    echo "2. Test in Claude Code: 'Search my Archon knowledge base for OOS'"
    echo "3. Create OOS project in Archon if needed"
    echo ""
    echo "📚 Documentation:"
    echo "- Integration guide: docs/ARCHON_INTEGRATION.md"
    echo "- Firewall fix: docs/ARCHON_OCI_FIREWALL_FIX.md"
else
    echo "❌ Archon MCP connection failed"
    echo ""
    echo "🔍 Troubleshooting:"
    echo "1. Check if Archon server is running on Oracle VM"
    echo "2. Verify VM IP address is correct: $ARCHON_IP"
    echo "3. Check if port $ARCHON_PORT is accessible"
    echo ""
    echo "Run: curl -I $ARCHON_ENDPOINT"
    echo "Expected: HTTP 200, 400, or 405 response"
    echo ""
    echo "See docs/ARCHON_OCI_FIREWALL_FIX.md for detailed troubleshooting"
    exit 1
fi