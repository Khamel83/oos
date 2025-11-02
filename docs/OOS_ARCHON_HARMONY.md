# 🤝 OOS + Archon Harmony Guide

## Security Partnership: Zero-Trust + Secrets Management

After multiple security failures, OOS now embraces a **zero-trust security model** that works in harmony with **Archon secrets management**.

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   OOS Code      │    │  Pre-commit      │    │   Archon Vault  │
│   Repository    │───▶│  Security        │───▶│   Secrets Store │
│   (No Secrets)  │    │  Validation      │    │   (Truth Source)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### OOS Responsibilities
- **Zero secrets in code** - Never store credentials in repository
- **Pre-commit validation** - Block any attempt to commit secrets
- **Industry-standard tools** - GitGuardian + detect-secrets
- **Security monitoring** - Continuous scanning and validation

### Archon Responsibilities
- **Secure secrets storage** - Encrypted vault with access controls
- **Runtime secret injection** - Provide secrets to applications when needed
- **Access management** - Control who can access which secrets
- **Audit logging** - Track all secret access and usage

## How They Work Together

### 1. Development Workflow
```bash
# Developer works on OOS code (no secrets in repo)
vim src/my_app.py

# Uses environment variables that reference Archon
export OPENROUTER_API_KEY  # Will be loaded from Archon at runtime

# Pre-commit hooks validate no secrets in changes
git add .
git commit -m "feat: new feature"
# ✅ Security validation passes
```

### 2. Runtime Integration
```python
# OOS application at runtime
import os
from archon_client import get_secret

# Get secret from Archon vault
api_key = get_secret("OPENROUTER_API_KEY")

# Or use environment variable injected by Archon
api_key = os.getenv("OPENROUTER_API_KEY")
```

### 3. Deployment Workflow
```bash
# Deploy OOS application
./bin/deploy-app.sh

# Deployment script:
# 1. No secrets in codebase
# 2. Fetch secrets from Archon
# 3. Inject into runtime environment
# 4. Start application
```

## Security Standards

### OOS Code Standards
- ✅ **No hardcoded secrets** anywhere in repository
- ✅ **Environment variable references** only
- ✅ **Fake keys in documentation** using standardized patterns
- ✅ **Pre-commit validation** on every commit
- ✅ **Archon integration** for runtime secrets

### Archon Integration Standards
- 🔐 **Secure vault storage** with encryption
- 🔑 **Access control** based on user roles
- 📋 **Audit logging** of all secret access
- 🔄 **Automatic rotation** capabilities
- 🌐 **Runtime injection** into applications

## Configuration Examples

### OOS Configuration (.env)
```bash
# .env file (gitignored)
# Secrets are managed by Archon

# Archon integration
ARCHON_VAULT_URL="https://archon.khamel.com"
ARCHON_PROJECT_ID="your-project-id"

# Runtime secrets (loaded from Archon)
# OPENROUTER_API_KEY=  # Loaded by Archon at runtime
# PERPLEXITY_API_KEY=   # Loaded by Archon at runtime
```

### OOS Application Code
```python
# src/config.py
import os
from archon_client import ArchonClient

class SecureConfig:
    def __init__(self):
        self.archon = ArchonClient(
            vault_url=os.getenv("ARCHON_VAULT_URL"),
            project_id=os.getenv("ARCHON_PROJECT_ID")
        )

    def get_api_key(self, key_name: str) -> str:
        """Get secret from Archon vault"""
        return self.archon.get_secret(key_name)

    def get_openrouter_key(self) -> str:
        """Get OpenRouter API key from Archon"""
        return self.get_api_key("OPENROUTER_API_KEY")
```

### Documentation Standards
```markdown
# Example in documentation
```bash
# ✅ CORRECT - Use environment variable reference
export OPENROUTER_API_KEY  # Loaded from Archon

# ✅ CORRECT - Use fake key in examples
OPENROUTER_API_KEY="sk-or-v1-FAKE0000000000000000000000000000000000000000000000000000"

# ❌ WRONG - Never use real keys
OPENROUTER_API_KEY="sk-or-v1-[real_key_here]"
```

## Setup Instructions

### 1. Install Industry-Standard Security
```bash
# Install GitGuardian ggshield + detect-secrets + pre-commit
./setup-industry-security.sh

# Verify installation
pre-commit run --all-files
```

### 2. Configure Archon Integration
```bash
# Set up Archon vault access
export ARCHON_VAULT_PASSWORD="your-vault-password"

# Test Archon connection
./bin/test-archon-connection.sh

# Store secrets in Archon
# Visit: https://archon.khamel.com/vault
```

### 3. Validate Security Setup
```bash
# Test security validation
echo "OPENROUTER_API_KEY=\"sk-or-v1-FAKE0000000000000000000000000000000000000000000000000000\"" > test.txt
git add test.txt
git commit -m "test: security validation"
# ✅ Should pass with fake key

# Test with real-looking key
echo "OPENROUTER_API_KEY=\"sk-or-v1-1234567890abcdef1234567890abcdef1234567890abcdef1234567890\"" > test.txt
git add test.txt
git commit -m "test: security validation"
# ❌ Should be blocked
```

## Best Practices

### Development
1. **Never type real API keys** in any file
2. **Use Archon vault** for all secret storage
3. **Test security validation** regularly
4. **Review security logs** for any issues
5. **Keep Archon credentials** secure

### Documentation
1. **Use fake keys** in all examples
2. **Include Archon instructions** in setup guides
3. **Add security warnings** to API documentation
4. **Reference this harmony guide** frequently

### Operations
1. **Monitor Archon access logs**
2. **Rotate secrets regularly** via Archon
3. **Audit OOS repository** for any accidentally committed secrets
4. **Update security tools** regularly

## Troubleshooting

### Pre-commit Issues
```bash
# If pre-commit hooks fail
./bin/validate-no-secrets.sh --verbose

# If secrets detected
grep -r "sk-or-v1-" . --exclude-dir=.git
# Remove any real keys found
```

### Archon Connection Issues
```bash
# Test Archon connection
curl -H "Authorization: Bearer $ARCHON_VAULT_PASSWORD" \
     https://archon.khamel.com/api/health

# Verify project access
curl -H "Authorization: Bearer $ARCHON_VAULT_PASSWORD" \
     https://archon.khamel.com/api/projects
```

### Runtime Issues
```bash
# Check if secrets are available
./bin/check-runtime-secrets.sh

# Validate Archon integration
./bin/test-archon-integration.py
```

## Security Validation Commands

```bash
# Comprehensive security check
./bin/audit-security.sh

# Validate no secrets in repository
./bin/validate-no-secrets.sh

# Test pre-commit hooks
pre-commit run --all-files

# Check Archon integration
./bin/test-archon-connection.sh
```

## Benefits of This Approach

### Security Benefits
- ✅ **Zero secrets in code** - Eliminates exposure risk
- ✅ **Industry-standard tools** - Proven security patterns
- ✅ **Automated validation** - Prevents human error
- ✅ **Audit trail** - Complete visibility into secret access

### Development Benefits
- ✅ **No more API key rotation pain** - Archon handles it
- ✅ **Clear separation of concerns** - Code vs secrets
- ✅ **Automated security validation** - No manual checking needed
- ✅ **Industry best practices** - Standard security patterns

### Operational Benefits
- ✅ **Centralized secrets management** - Archon as single source of truth
- ✅ **Automated secret injection** - No manual configuration
- ✅ **Access control** - Granular permissions per secret
- ✅ **Compliance ready** - Audit logs and access tracking

## Conclusion

This OOS + Archon harmony provides:

1. **Zero-trust security** - OOS never stores secrets
2. **Industry-standard validation** - GitGuardian + detect-secrets
3. **Secure secrets management** - Archon vault integration
4. **Automated protection** - Pre-commit hooks + validation
5. **Complete audit trail** - Both code changes and secret access

Together, they create a secure development environment that prevents the API key exposure incidents of the past while providing a seamless developer experience.

---

**Trust Level**: Zero-trust (proven by industry standards)
**Security Level**: Enterprise-grade (GitGuardian + Archon)
**Maintenance**: Automated validation + monitoring
**Recovery**: Complete - No more secret exposure incidents