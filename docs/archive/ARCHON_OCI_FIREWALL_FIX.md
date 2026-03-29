# Archon OCI Firewall Configuration Guide

## 🚨 CRITICAL ISSUE RESOLVED

**Problem**: Archon MCP server running on Oracle OCI VM was unreachable via domain name due to firewall blocking port 8051.

**Root Cause**: OCI Security Lists blocking external access to port 8051.

**Solution**: Use direct IP address for MCP connection until firewall is properly configured.

## ✅ Working Configuration

### Current Working Setup:
- **Archon Server**: Running on Oracle OCI VM `100.103.45.61:8051`
- **MCP Endpoint**: `http://100.103.45.61:8051/mcp` ✅ WORKING
- **Domain Issue**: `http://archon.khamel.com:8051/mcp` ❌ BLOCKED BY FIREWALL

### Claude MCP Configuration:
```bash
# Remove any broken configs
claude mcp remove archon

# Add working direct IP config
claude mcp add --transport http archon http://100.103.45.61:8051/mcp

# Verify connection
claude mcp list
# Should show: archon: http://100.103.45.61:8051/mcp (HTTP) - ✓ Connected
```

## 🔒 Permanent Fix: Configure OCI Security Lists

To use the domain name `archon.khamel.com:8051`, configure OCI firewall:

### Option 1: OCI Console (Recommended)

1. **Go to OCI Console** → **Networking** → **Virtual Cloud Networks**
2. **Find your VCN** → **Security Lists** → **Default Security List**
3. **Add Ingress Rule:**
   - **Source Type**: CIDR
   - **Source CIDR**: `0.0.0.0/0`
   - **IP Protocol**: TCP
   - **Source Port Range**: All
   - **Destination Port Range**: `8051`
   - **Description**: "Archon MCP Server External Access"

### Option 2: OCI CLI

```bash
# Get compartment and VCN IDs
oci iam compartment list --all
oci network vcn list --compartment-id <compartment-id>

# Add security rule for port 8051
oci network security-list update \
  --security-list-id <security-list-id> \
  --ingress-security-rules '[
    {
      "source": "0.0.0.0/0",
      "protocol": "6",
      "tcpOptions": {
        "destinationPortRange": {
          "min": 8051,
          "max": 8051
        }
      },
      "description": "Archon MCP Server"
    }
  ]'
```

### Option 3: SSH to VM and Check Local Firewall

```bash
# SSH to your Oracle VM
ssh ubuntu@100.103.45.61

# Check if local firewall is also blocking
sudo iptables -L -n | grep 8051

# If port not open locally, add rule
sudo iptables -I INPUT -p tcp --dport 8051 -j ACCEPT

# Make persistent (Ubuntu/Debian)
sudo iptables-save > /etc/iptables/rules.v4

# For Oracle Linux/RHEL with firewalld
sudo firewall-cmd --permanent --add-port=8051/tcp
sudo firewall-cmd --reload
```

## 🧪 Verification Steps

### Test 1: Direct IP (Should Work Now)
```bash
curl -I http://100.103.45.61:8051/mcp
# Expected: HTTP/1.1 200 OK or similar success response
```

### Test 2: Domain (Will work after OCI firewall fix)
```bash
curl -I http://archon.khamel.com:8051/mcp
# Expected: HTTP/1.1 200 OK (after OCI Security List update)
```

### Test 3: OOS Integration Test
```bash
./bin/test_archon_integration.sh
# Expected: ✅ Archon found in MCP servers, ✅ Archon endpoint responding
```

## 📋 Configuration History

### What Happened:
1. **Archon MCP server configured** to listen on `0.0.0.0:8051` ✅
2. **All MCP tools registered** successfully ✅
3. **OCI VCN Security Lists** blocking external port 8051 access ❌
4. **Domain resolution working** (`archon.khamel.com` → `141.148.146.79`) ✅
5. **Connection timeouts** on port 8051 via domain name ❌

### Diagnostic Results:
```
✅ ping archon.khamel.com → SUCCESS (141.148.146.79)
❌ nc -zv archon.khamel.com 8051 → TIMEOUT
❌ curl http://archon.khamel.com:8051/mcp → TIMEOUT
✅ curl https://archon.khamel.com → SUCCESS (Caddy web server)
✅ claude mcp add archon http://100.103.45.61:8051/mcp → SUCCESS
```

## 🚀 Migration Path

### Phase 1: Immediate Fix (DONE)
- ✅ Use direct IP address: `http://100.103.45.61:8051/mcp`
- ✅ Update Claude MCP configuration
- ✅ Verify connection working

### Phase 2: Proper Domain Setup (TODO)
- Configure OCI Security Lists to allow port 8051
- Test domain access: `http://archon.khamel.com:8051/mcp`
- Update MCP config back to domain name
- Update all documentation

### Phase 3: SSL/TLS Setup (FUTURE)
- Configure SSL certificate for port 8051
- Update to `https://archon.khamel.com:8051/mcp`
- Enhanced security configuration

## 🔄 Automation Scripts

### Quick Setup Script
```bash
#!/bin/bash
# bin/setup-archon-mcp.sh

echo "Setting up Archon MCP connection..."

# Remove any existing config
claude mcp remove archon 2>/dev/null || true

# Add direct IP config (always works)
claude mcp add --transport http archon http://100.103.45.61:8051/mcp

# Verify connection
if claude mcp list | grep -q "✓ Connected"; then
    echo "✅ Archon MCP connected successfully!"
    echo "Run: ./bin/test_archon_integration.sh to verify full integration"
else
    echo "❌ Archon MCP connection failed"
    echo "Check if Archon server is running on Oracle VM"
fi
```

## 📚 Related Documentation

- **OOS Archon Integration**: `docs/ARCHON_INTEGRATION.md`
- **Server Setup Guide**: `docs/ARCHON_SERVER_SETUP.md`
- **Integration Testing**: `bin/test_archon_integration.sh`

## 🔮 Future Improvements

1. **Dynamic Endpoint Detection**: Auto-detect if domain or IP should be used
2. **Health Check Monitoring**: Automatic failover between domain/IP endpoints
3. **SSL Certificate Automation**: Let's Encrypt for port 8051
4. **Load Balancing**: Multiple Archon instances for redundancy

---

**RESOLVED**: Archon MCP connection now working with direct IP address. Domain access will work after OCI Security List configuration.