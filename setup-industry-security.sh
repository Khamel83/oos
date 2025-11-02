#!/usr/bin/env bash
set -euo pipefail

# Install Industry-Standard Security Tools
# GitGuardian ggshield + detect-secrets + pre-commit framework

echo "🔧 Installing Industry-Standard Security Tools for OOS"
echo "Working in harmony with Archon secrets management"
echo

# Install pre-commit framework
echo "1. Installing pre-commit framework..."
pip install pre-commit

# Install GitGuardian ggshield (industry standard)
echo "2. Installing GitGuardian ggshield..."
pip install ggshield

# Install detect-secrets (Yelp's solution)
echo "3. Installing detect-secrets..."
pip install detect-secrets

# Create secrets baseline
echo "4. Creating secrets baseline..."
detect-secrets scan --baseline .secrets.baseline || true

# Install pre-commit hooks
echo "5. Installing pre-commit hooks..."
pre-commit install

echo "✅ Industry-standard security tools installed"
echo
echo "🔒 Security Features Active:"
echo " • GitGuardian ggshield (350+ secret types)"
echo " • detect-secrets (entropy-based detection)"
echo " • OOS zero-trust validation"
echo " • Pre-commit protection"
echo " • Archon integration support"
echo
echo "🏗️ Next Steps:"
echo "1. Store secrets in Archon: https://archon.khamel.com/vault"
echo "2. Test security: git add . && git commit -m 'test security'"
echo "3. Verify no secrets in repository"
echo
echo "📚 Reference:"
echo " • docs/INDUSTRY_SECURITY_STANDARDS.md"
echo " • docs/SECURITY_INCIDENT_POSTMORTEM.md"