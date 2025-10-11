#!/bin/bash

echo "=========================================="
echo "OOS ARCHON INTEGRATION TEST SUITE"
echo "=========================================="
echo ""

# Test 1: Check Claude Code is installed
echo "TEST 1: Claude Code Installation"
echo "-----------------------------------"
if command -v claude &> /dev/null; then
    echo "✅ Claude Code is installed"
    claude --version 2>&1 || echo "Version check failed"
else
    echo "❌ Claude Code not found in PATH"
fi
echo ""

# Test 2: Check MCP servers
echo "TEST 2: MCP Server Connection"
echo "-----------------------------------"
echo "Running: claude mcp list"
claude mcp list 2>&1 || echo "❌ Failed to list MCP servers"
echo ""

# Test 3: Check if Archon is in MCP list
echo "TEST 3: Archon MCP Registration"
echo "-----------------------------------"
if claude mcp list 2>&1 | grep -i "archon"; then
    echo "✅ Archon found in MCP servers"
else
    echo "❌ Archon NOT found in MCP servers"
    echo "Expected to see: archon: http://100.103.45.61:8051/mcp (HTTP) - ✓ Connected"
fi
echo ""

# Test 4: Check OOS directory structure
echo "TEST 4: OOS Directory Structure"
echo "-----------------------------------"
if [ -f "README.md" ]; then
    echo "✅ README.md exists"
else
    echo "❌ README.md not found (are you in OOS directory?)"
fi

if [ -f "CLAUDE.md" ] || [ -f ".claude/CLAUDE.md" ]; then
    echo "✅ CLAUDE.md exists"
else
    echo "⚠️  CLAUDE.md not found"
fi

if [ -f "docs/ARCHON_INTEGRATION.md" ]; then
    echo "✅ docs/ARCHON_INTEGRATION.md exists"
else
    echo "❌ docs/ARCHON_INTEGRATION.md NOT found"
fi
echo ""

# Test 5: Check .clauderc
echo "TEST 5: Claude Configuration"
echo "-----------------------------------"
if [ -f ".clauderc" ]; then
    echo "✅ .clauderc exists"
    echo "Contents:"
    cat .clauderc
else
    echo "⚠️  .clauderc not found"
fi
echo ""

# Test 6: Check CLAUDE.md for Archon references
echo "TEST 6: CLAUDE.md Archon References"
echo "-----------------------------------"
if [ -f "CLAUDE.md" ]; then
    if grep -i "archon" CLAUDE.md > /dev/null 2>&1; then
        echo "✅ CLAUDE.md mentions Archon"
        echo "First mention:"
        grep -i "archon" CLAUDE.md | head -n 3
    else
        echo "❌ CLAUDE.md does NOT mention Archon"
    fi
elif [ -f ".claude/CLAUDE.md" ]; then
    if grep -i "archon" .claude/CLAUDE.md > /dev/null 2>&1; then
        echo "✅ .claude/CLAUDE.md mentions Archon"
        echo "First mention:"
        grep -i "archon" .claude/CLAUDE.md | head -n 3
    else
        echo "❌ .claude/CLAUDE.md does NOT mention Archon"
    fi
else
    echo "⚠️  No CLAUDE.md file found"
fi
echo ""

# Test 7: Test Archon endpoint connectivity
echo "TEST 7: Archon Endpoint Connectivity"
echo "-----------------------------------"
echo "Testing direct IP: http://100.103.45.61:8051/mcp"
if command -v curl &> /dev/null; then
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://100.103.45.61:8051/mcp 2>&1)
    if [ "$response" = "400" ] || [ "$response" = "200" ] || [ "$response" = "405" ]; then
        echo "✅ Archon endpoint responding (HTTP $response)"
    else
        echo "❌ Archon endpoint not responding (HTTP $response)"
    fi

    echo "Testing domain: http://archon.khamel.com:8051/mcp"
    response_domain=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://archon.khamel.com:8051/mcp 2>&1)
    if [ "$response_domain" = "400" ] || [ "$response_domain" = "200" ] || [ "$response_domain" = "405" ]; then
        echo "✅ Domain endpoint also responding (HTTP $response_domain)"
        echo "⚠️  Consider switching back to domain name in MCP config"
    else
        echo "❌ Domain endpoint blocked by OCI firewall (HTTP $response_domain)"
        echo "ℹ️  See docs/ARCHON_OCI_FIREWALL_FIX.md for firewall configuration"
    fi
else
    echo "⚠️  curl not available, skipping connectivity test"
fi
echo ""

# Test 8: Check if archon tools are available in Claude Code
echo "TEST 8: Archon Tools Availability Check"
echo "-----------------------------------"
echo "This test requires Claude Code interaction."
echo "Run this command manually in Claude Code:"
echo ""
echo "  /mcp"
echo ""
echo "Look for archon tools like:"
echo "  - archon_query_knowledge"
echo "  - archon_list_tasks"
echo "  - archon_read_project"
echo ""

# Test 9: Check Claude config location
echo "TEST 9: Claude Configuration Location"
echo "-----------------------------------"
if [ -d "$HOME/Library/Application Support/Claude" ]; then
    echo "✅ Claude config directory exists (macOS)"
    echo "Location: $HOME/Library/Application Support/Claude"
elif [ -d "$HOME/.config/claude" ]; then
    echo "✅ Claude config directory exists (Linux)"
    echo "Location: $HOME/.config/claude"
elif [ -d "$APPDATA/Claude" ]; then
    echo "✅ Claude config directory exists (Windows)"
    echo "Location: $APPDATA/Claude"
else
    echo "⚠️  Claude config directory not found in standard locations"
fi
echo ""

# Summary
echo "=========================================="
echo "SUMMARY & NEXT STEPS"
echo "=========================================="
echo ""
echo "COPY ALL OUTPUT ABOVE AND SHARE WITH CLAUDE"
echo ""
echo "Key things to check:"
echo "1. Is Archon in the MCP server list?"
echo "2. Does docs/ARCHON_INTEGRATION.md exist?"
echo "3. Does CLAUDE.md reference Archon?"
echo "4. Can Archon endpoint be reached?"
echo ""
echo "If any tests failed, Claude will tell you how to fix them."
echo ""