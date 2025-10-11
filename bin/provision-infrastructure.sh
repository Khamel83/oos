#!/bin/bash

# OOS AI-Powered Infrastructure Provisioning
# Generates and deploys infrastructure based on natural language descriptions

set -e

echo "🚀 OOS AI Infrastructure Provisioning"
echo "====================================="

# Configuration
PROVISION_DIR="$HOME/oos-provisioned"
TEMPLATES_DIR="$(dirname "$0")/../templates/infrastructure"
DOMAIN_BASE="${DOMAIN_BASE:-khamel.com}"

# Create directories
mkdir -p "$PROVISION_DIR"
mkdir -p "$TEMPLATES_DIR"

# Parse arguments
PROJECT_NAME=""
DESCRIPTION=""
DOMAIN=""
STACK=""
MODE="preview"

while [[ $# -gt 0 ]]; do
    case $1 in
        --name)
            PROJECT_NAME="$2"
            shift 2
            ;;
        --description)
            DESCRIPTION="$2"
            shift 2
            ;;
        --domain)
            DOMAIN="$2"
            shift 2
            ;;
        --stack)
            STACK="$2"
            shift 2
            ;;
        --deploy)
            MODE="deploy"
            shift
            ;;
        --preview)
            MODE="preview"
            shift
            ;;
        *)
            if [ -z "$DESCRIPTION" ]; then
                DESCRIPTION="$1"
            fi
            shift
            ;;
    esac
done

# Validate inputs
if [ -z "$DESCRIPTION" ]; then
    echo "❌ Please provide a project description"
    echo ""
    echo "Usage: $0 'description of what you want to build' [options]"
    echo ""
    echo "Examples:"
    echo "  $0 'React blog with PostgreSQL database'"
    echo "  $0 'FastAPI service with Redis cache' --name api-service"
    echo "  $0 'Full-stack ecommerce app' --domain shop.khamel.com --deploy"
    echo ""
    echo "Options:"
    echo "  --name NAME          Project name (auto-generated if not provided)"
    echo "  --domain DOMAIN      Custom domain (auto-generated subdomain if not provided)"
    echo "  --stack STACK        Technology stack preference (detected from description)"
    echo "  --deploy             Actually deploy (default: preview only)"
    echo "  --preview            Preview mode only (default)"
    exit 1
fi

# Auto-generate project name if not provided
if [ -z "$PROJECT_NAME" ]; then
    PROJECT_NAME=$(echo "$DESCRIPTION" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g' | cut -c1-30)
fi

# Auto-generate domain if not provided
if [ -z "$DOMAIN" ]; then
    DOMAIN="${PROJECT_NAME}.${DOMAIN_BASE}"
fi

PROJECT_DIR="$PROVISION_DIR/$PROJECT_NAME"

echo "📋 Provisioning Details:"
echo "  Description: $DESCRIPTION"
echo "  Project: $PROJECT_NAME"
echo "  Domain: $DOMAIN"
echo "  Mode: $MODE"
echo ""

# Create project directory
mkdir -p "$PROJECT_DIR"

# Generate infrastructure with AI
echo "🤖 Generating infrastructure with AI..."

# Create the AI prompt for infrastructure generation
ai_prompt="Generate Docker Compose infrastructure for: $DESCRIPTION

Requirements:
- Project name: $PROJECT_NAME
- Domain: $DOMAIN
- Include all necessary services (database, cache, etc.)
- Add Traefik reverse proxy with automatic SSL
- Include environment variables file
- Add proper networking and volumes
- Include monitoring with Prometheus/Grafana if complex
- Generate README.md with setup instructions

Please provide:
1. docker-compose.yml
2. .env template
3. Traefik configuration
4. README.md with setup instructions
5. Any additional configuration files needed

Make it production-ready with proper security, networking, and monitoring."

# Use Claude to generate the infrastructure
if command -v claude &> /dev/null; then
    echo "Generating infrastructure configuration..."

    # Generate docker-compose.yml
    echo "📦 Generating Docker Compose configuration..."
    echo "Generate a production-ready docker-compose.yml for: $DESCRIPTION. Include Traefik reverse proxy with SSL, proper networking, and all necessary services." | claude --print --output-format=text > "$PROJECT_DIR/docker-compose.yml.generated"

    # Generate .env template
    echo "🔧 Generating environment configuration..."
    echo "Generate a .env template file for the infrastructure: $DESCRIPTION. Include all necessary environment variables with example values and security best practices." | claude --print --output-format=text > "$PROJECT_DIR/.env.template"

    # Generate README
    echo "📚 Generating documentation..."
    echo "Generate a comprehensive README.md for deploying: $DESCRIPTION. Include setup instructions, environment configuration, deployment steps, and troubleshooting." | claude --print --output-format=text > "$PROJECT_DIR/README.md"

    # Generate Traefik config
    echo "🔀 Generating reverse proxy configuration..."
    echo "Generate Traefik configuration for domain $DOMAIN with automatic SSL for: $DESCRIPTION" | claude --print --output-format=text > "$PROJECT_DIR/traefik.yml.generated"

else
    echo "❌ Claude Code not found. Using template-based generation..."

    # Fallback: Use templates
    cat > "$PROJECT_DIR/docker-compose.yml" << EOF
version: '3.8'

services:
  # Generated for: $DESCRIPTION
  # Domain: $DOMAIN
  # Project: $PROJECT_NAME

  # TODO: Customize this based on your requirements
  app:
    image: nginx:alpine
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.${PROJECT_NAME}.rule=Host(\`${DOMAIN}\`)"
      - "traefik.http.routers.${PROJECT_NAME}.tls.certresolver=letsencrypt"
    networks:
      - traefik

  traefik:
    image: traefik:v3.0
    command:
      - "--api.dashboard=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.email=admin@${DOMAIN_BASE}"
      - "--certificatesresolvers.letsencrypt.acme.storage=/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./acme.json:/acme.json
    networks:
      - traefik

networks:
  traefik:
    external: false
EOF

    cat > "$PROJECT_DIR/.env" << EOF
# Environment configuration for: $DESCRIPTION
# Project: $PROJECT_NAME
# Domain: $DOMAIN

# Basic configuration
PROJECT_NAME=$PROJECT_NAME
DOMAIN=$DOMAIN

# Add your specific environment variables here
# DATABASE_URL=
# REDIS_URL=
# API_KEY=
EOF

    cat > "$PROJECT_DIR/README.md" << EOF
# $PROJECT_NAME

$DESCRIPTION

## Quick Start

1. Configure environment:
   \`\`\`bash
   cp .env.template .env
   # Edit .env with your configuration
   \`\`\`

2. Deploy:
   \`\`\`bash
   docker-compose up -d
   \`\`\`

3. Access: https://$DOMAIN

## Generated by OOS Infrastructure Provisioning
EOF
fi

echo "✅ Infrastructure generated in: $PROJECT_DIR"

# Show what was generated
echo ""
echo "📁 Generated files:"
find "$PROJECT_DIR" -type f | sed 's|'"$PROJECT_DIR"'/|  |'

if [ "$MODE" = "preview" ]; then
    echo ""
    echo "🔍 PREVIEW MODE - No deployment performed"
    echo ""
    echo "📋 Next steps:"
    echo "  1. Review generated files in: $PROJECT_DIR"
    echo "  2. Customize configuration as needed"
    echo "  3. Deploy with: $0 '$DESCRIPTION' --deploy"
    echo ""
    echo "🚀 Quick deploy:"
    echo "  cd $PROJECT_DIR && docker-compose up -d"

elif [ "$MODE" = "deploy" ]; then
    echo ""
    echo "🚀 DEPLOY MODE - Starting deployment..."

    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker not found. Please install Docker first."
        exit 1
    fi

    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo "❌ Docker Compose not found. Please install Docker Compose first."
        exit 1
    fi

    # Navigate to project directory and deploy
    cd "$PROJECT_DIR"

    echo "📦 Pulling images and starting services..."
    if docker compose version &> /dev/null; then
        docker compose up -d
    else
        docker-compose up -d
    fi

    echo ""
    echo "✅ Deployment completed!"
    echo "🌐 Your application should be available at: https://$DOMAIN"
    echo "📊 Monitor with: docker-compose logs -f"
    echo ""
fi

echo "💡 Pro tips:"
echo "  - Generated infrastructure is in: $PROJECT_DIR"
echo "  - Customize docker-compose.yml as needed"
echo "  - Check logs: docker-compose logs -f"
echo "  - Stop: docker-compose down"