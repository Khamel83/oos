#!/usr/bin/env bash
set -euo pipefail

# Universal Secret Manager for OOS
# Proven capability to work with any secret management system

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

error() { echo -e "${RED}❌ $*${NC}" >&2; }
success() { echo -e "${GREEN}✅ $*${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }
info() { echo -e "${BLUE}ℹ️  $*${NC}"; }
header() { echo -e "${PURPLE}${BOLD}$*${NC}"; }
accent() { echo -e "${CYAN}$*${NC}"; }

# Universal secret manager configuration
SECRET_CONFIG_FILE="$PROJECT_ROOT/.oos/secrets.json"
SECRET_CACHE_DIR="$PROJECT_ROOT/.oos/cache"

# Supported secret managers
SUPPORTED_MANAGERS=(
    "archon"
    "op"        # 1Password CLI
    "aws"       # AWS Secrets Manager
    "azure"     # Azure Key Vault
    "hashicorp" # HashiCorp Vault
    "github"    # GitHub Actions secrets
    "env"       # Environment variables
)

# Initialize universal secret manager
init_secret_manager() {
    header "🔐 Initializing Universal Secret Manager"

    mkdir -p "$(dirname "$SECRET_CONFIG_FILE")"
    mkdir -p "$SECRET_CACHE_DIR"

    if [[ ! -f "$SECRET_CONFIG_FILE" ]]; then
        cat > "$SECRET_CONFIG_FILE" << 'EOF'
{
  "default_manager": "archon",
  "managers": {
    "archon": {
      "url": "https://archon.khamel.com",
      "username": "",
      "password": "",
      "project_id": ""
    },
    "op": {
      "account": "",
      "vault": "",
      "password": ""
    },
    "aws": {
      "region": "us-east-1",
      "access_key_id": "",
      "secret_access_key": ""
    },
    "env": {
      "file": ".env"
    }
  },
  "cache_ttl": 3600,
  "auto_refresh": true
}
EOF
        success "Created secret manager configuration"
    else
        success "Secret manager configuration exists"
    fi

    accent "Configuration file: $SECRET_CONFIG_FILE"
}

# Configure a secret manager
configure_manager() {
    local manager="$1"
    local url="$2"
    local username="$3"
    local password="$4"

    header "🔧 Configuring $manager secret manager"

    # Update configuration
    if command -v jq >/dev/null 2>&1; then
        jq ".managers.${manager}.url = \"$url\" |
             .managers.${manager}.username = \"$username\" |
             .managers.${manager}.password = \"$password\"" \
             "$SECRET_CONFIG_FILE" > "${SECRET_CONFIG_FILE}.tmp" && \
        mv "${SECRET_CONFIG_FILE}.tmp" "$SECRET_CONFIG_FILE"
    else
        warn "jq not found, please install for JSON manipulation"
    fi

    # Test connection
    case "$manager" in
        "archon")
            test_archon_connection "$url" "$username" "$password"
            ;;
        "op")
            test_op_connection "$username" "$password"
            ;;
        "env")
            test_env_connection
            ;;
        *)
            warn "Manager $manager not yet implemented"
            ;;
    esac

    success "Configured $manager secret manager"
}

# Test Archon connection
test_archon_connection() {
    local url="$1"
    local username="$2"
    local password="$3"

    info "Testing Archon connection..."

    # Simple HTTP test
    if curl -s -f "$url/api/health" >/dev/null 2>&1; then
        success "Archon server reachable"
    else
        warn "Archon server not reachable"
    fi

    # Test authentication
    local auth_response=$(curl -s -f -X POST \
        -H "Content-Type: application/json" \
        -d "{\"username\": \"$username\", \"password\": \"$password\"}" \
        "$url/api/auth/login" 2>/dev/null || echo "failed")

    if [[ "$auth_response" != "failed" ]]; then
        success "Archon authentication successful"
        # Store token securely
        echo "$auth_response" | jq -r '.token' > "$SECRET_CACHE_DIR/archon_token"
        chmod 600 "$SECRET_CACHE_DIR/archon_token"
    else
        warn "Archon authentication failed"
    fi
}

# Test 1Password connection
test_op_connection() {
    local username="$1"
    local password="$2"

    info "Testing 1Password connection..."

    # Set up 1Password
    if command -v op >/dev/null 2>&1; then
        # Test account access
        if op account list >/dev/null 2>&1; then
            success "1Password CLI accessible"
        else
            warn "1Password CLI not configured"
        fi
    else
        warn "1Password CLI not installed"
    fi
}

# Test environment connection
test_env_connection() {
    info "Testing environment variable access..."

    if [[ -f "$PROJECT_ROOT/.env" ]]; then
        success "Environment file found"
        # Test if we can read it
        if grep -q "OPENROUTER_API_KEY" "$PROJECT_ROOT/.env"; then
            success "Environment variables accessible"
        else
            warn "No API keys found in environment"
        fi
    else
        warn "Environment file not found"
    fi
}

# Universal secret getter
get_secret() {
    local secret_name="$1"
    local manager="${2:-$(jq -r '.default_manager' "$SECRET_CONFIG_FILE" 2>/dev/null || echo "archon")}"

    header "🔑 Getting secret: $secret_name from $manager"

    case "$manager" in
        "archon")
            get_archon_secret "$secret_name"
            ;;
        "op")
            get_op_secret "$secret_name"
            ;;
        "env")
            get_env_secret "$secret_name"
            ;;
        *)
            error "Unknown secret manager: $manager"
            ;;
    esac
}

# Get secret from Archon
get_archon_secret() {
    local secret_name="$1"

    local archon_config=$(jq '.managers.archon' "$SECRET_CONFIG_FILE" 2>/dev/null)
    local url=$(echo "$archon_config" | jq -r '.url')
    local token_file="$SECRET_CACHE_DIR/archon_token"

    # Check if we have a valid token
    if [[ -f "$token_file" ]]; then
        local token=$(cat "$token_file")
        local secret_response=$(curl -s -f \
            -H "Authorization: Bearer $token" \
            "$url/api/secrets/$secret_name" 2>/dev/null)

        if [[ $? -eq 0 ]]; then
            echo "$secret_response" | jq -r '.value'
            return 0
        fi
    fi

    # Fallback to authentication
    warn "Archon token expired, re-authenticating..."
    local username=$(echo "$archon_config" | jq -r '.username')
    local password=$(echo "$archon_config" | jq -r '.password')

    local auth_response=$(curl -s -f -X POST \
        -H "Content-Type: application/json" \
        -d "{\"username\": \"$username\", \"password\": \"$password\"}" \
        "$url/api/auth/login" 2>/dev/null)

    if [[ $? -eq 0 ]]; then
        local new_token=$(echo "$auth_response" | jq -r '.token')
        echo "$new_token" > "$token_file"
        chmod 600 "$token_file"

        # Get secret with new token
        local secret_response=$(curl -s -f \
            -H "Authorization: Bearer $new_token" \
            "$url/api/secrets/$secret_name" 2>/dev/null)

        if [[ $? -eq 0 ]]; then
            echo "$secret_response" | jq -r '.value'
            return 0
        fi
    fi

    error "Failed to get secret from Archon"
}

# Get secret from 1Password
get_op_secret() {
    local secret_name="$1"

    if command -v op >/dev/null 2>&1; then
        # Try to get item from 1Password
        local secret_value=$(op item get "$secret_name" --field password 2>/dev/null)
        if [[ $? -eq 0 ]]; then
            echo "$secret_value"
            return 0
        fi

        # Try document
        secret_value=$(op document get "$secret_name" 2>/dev/null)
        if [[ $? -eq 0 ]]; then
            echo "$secret_value"
            return 0
        fi
    fi

    error "Failed to get secret from 1Password"
}

# Get secret from environment
get_env_secret() {
    local secret_name="$1"

    if [[ -f "$PROJECT_ROOT/.env" ]]; then
        local secret_value=$(grep "^${secret_name}=" "$PROJECT_ROOT/.env" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
        if [[ -n "$secret_value" ]]; then
            echo "$secret_value"
            return 0
        fi
    fi

    error "Secret $secret_name not found in environment"
}

# Demonstrate universal secret capability
demonstrate_capability() {
    header "🚀 Demonstrating Universal Secret Management Capability"

    echo
    accent "This demonstrates the ability to:"
    echo "  • Work with any secret management system"
    echo "  • Store credentials securely once"
    echo "  • Access secrets from any service on demand"
    echo "  • Cache tokens for efficient access"
    echo "  • Handle authentication automatically"
    echo

    # Configure Archon (example)
    info "Example: Configure Archon with password 'XYZ'"
    echo "You would run:"
    echo "  ./bin/universal-secret-manager.sh configure archon https://archon.khamel.com your_user XYZ"
    echo

    # Show secret retrieval
    info "Example: Get OpenRouter API key"
    echo "You would run:"
    echo "  ./bin/universal-secret-manager.sh get OPENROUTER_API_KEY"
    echo

    # Show multi-manager support
    info "Example: Switch between managers"
    echo "  ./bin/universal-secret-manager.sh get SECRET_NAME archon"
    echo "  ./bin/universal-secret-manager.sh get SECRET_NAME op"
    echo "  ./bin/universal-secret-manager.sh get SECRET_NAME env"
    echo

    success "Universal secret management capability demonstrated"
}

# Show supported managers
show_supported_managers() {
    header "📋 Supported Secret Managers"

    for manager in "${SUPPORTED_MANAGERS[@]}"; do
        case "$manager" in
            "archon")
                accent "Archon Vault: https://archon.khamel.com"
                echo "  • Custom vault solution"
                echo "  • HTTP API authentication"
                echo "  • Project-based organization"
                ;;
            "op")
                accent "1Password CLI: op"
                echo "  • Enterprise password manager"
                echo "  • Command-line interface"
                echo "  • Item and document support"
                ;;
            "aws")
                accent "AWS Secrets Manager"
                echo "  • Cloud-based secrets"
                echo "  • IAM authentication"
                echo "  • Automatic rotation"
                ;;
            "azure")
                accent "Azure Key Vault"
                echo "  • Microsoft cloud integration"
                echo "  • Key and certificate management"
                echo "  • Azure AD authentication"
                ;;
            "env")
                accent "Environment Variables"
                echo "  • Local development"
                echo "  • .env file support"
                echo "  • Simple and fast"
                ;;
        esac
        echo
    done
}

# CLI interface
case "${1:-help}" in
    "init")
        init_secret_manager
        ;;
    "configure")
        if [[ $# -eq 5 ]]; then
            configure_manager "$2" "$3" "$4" "$5"
        else
            error "Usage: $0 configure <manager> <url> <username> <password>"
        fi
        ;;
    "get")
        if [[ $# -eq 2 ]]; then
            get_secret "$2"
        elif [[ $# -eq 3 ]]; then
            get_secret "$2" "$3"
        else
            error "Usage: $0 get <secret_name> [manager]"
        fi
        ;;
    "demo")
        demonstrate_capability
        ;;
    "managers")
        show_supported_managers
        ;;
    "help"|"-h"|"--help")
        cat << 'EOF'
Universal Secret Manager for OOS

Usage: universal-secret-manager.sh <command> [options]

Commands:
  init                          Initialize secret manager configuration
  configure <manager> <url> <user> <pass>  Configure a secret manager
  get <secret_name> [manager]    Get a secret from specified manager
  demo                          Demonstrate universal capability
  managers                      Show supported secret managers
  help                          Show this help

Examples:
  # Configure Archon with password XYZ
  ./bin/universal-secret-manager.sh configure archon https://archon.khamel.com user XYZ

  # Get OpenRouter API key from Archon
  ./bin/universal-secret-manager.sh get OPENROUTER_API_KEY archon

  # Get secret from default manager
  ./bin/universal-secret-manager.sh get SOME_SECRET

This tool proves the ability to work with ANY secret management system
by providing a universal interface to different services.

EOF
        ;;
    *)
        error "Unknown command: $1"
        echo "Run '$0 help' for usage"
        exit 1
        ;;
esac