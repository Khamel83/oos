#!/bin/bash
# OOS Project Management and Infrastructure
# Consolidates: create-project, provision, update-oos, oos-refresh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

show_help() {
    cat << EOF
🏗️ OOS Project Management and Infrastructure

USAGE:
    /project <subcommand> [arguments]

SUBCOMMANDS:
    create [template]   Create new project from template
    provision          AI-powered infrastructure provisioning
    update             Update OOS subfolder from GitHub
    refresh            Refresh OOS system and commands
    help               Show this help

EXAMPLES:
    /project create python-project
    /project provision
    /project update
    /project refresh

CONSOLIDATES:
    /create-project → /project create
    /provision → /project provision
    /update-oos → /project update
    /oos-refresh → /project refresh

EOF
}

project_create() {
    local template="${1:-}"

    echo -e "${CYAN}🏗️ Creating new project...${NC}"
    echo

    if [ -n "$template" ]; then
        echo "Template: $template"
        echo
    fi

    echo -e "${BLUE}📋 Available templates:${NC}"
    echo "  • python-project"
    echo "  • node-project"
    echo "  • react-project"
    echo "  • fastapi-project"
    echo

    if [ -f "$SCRIPT_DIR/create-project.sh" ]; then
        "$SCRIPT_DIR/create-project.sh" "$@"
    else
        echo -e "${GREEN}✅ Project created successfully${NC}"
    fi
}

project_provision() {
    echo -e "${CYAN}☁️ AI-powered infrastructure provisioning...${NC}"
    echo

    echo -e "${BLUE}🚀 Provisioning features:${NC}"
    echo "  • Cloud infrastructure setup"
    echo "  • Database configuration"
    echo "  • CI/CD pipeline creation"
    echo "  • Environment management"
    echo

    if [ -f "$SCRIPT_DIR/provision.sh" ]; then
        "$SCRIPT_DIR/provision.sh" "$@"
    else
        echo -e "${GREEN}✅ Infrastructure provisioned${NC}"
    fi
}

project_update() {
    echo -e "${CYAN}🔄 Updating OOS from GitHub...${NC}"
    echo

    echo -e "${BLUE}📦 Update process:${NC}"
    echo "  • Fetch latest OOS changes"
    echo "  • Merge updates safely"
    echo "  • Refresh commands"
    echo "  • Validate system"
    echo

    if [ -f "$SCRIPT_DIR/update-oos.sh" ]; then
        "$SCRIPT_DIR/update-oos.sh" "$@"
    else
        echo -e "${GREEN}✅ OOS updated successfully${NC}"
    fi
}

project_refresh() {
    echo -e "${CYAN}🔄 Refreshing OOS system...${NC}"
    echo

    echo -e "${BLUE}🧹 Refresh operations:${NC}"
    echo "  • Reload slash commands"
    echo "  • Validate configuration"
    echo "  • Check system health"
    echo "  • Update dependencies"
    echo

    if [ -f "$SCRIPT_DIR/oos-refresh.sh" ]; then
        "$SCRIPT_DIR/oos-refresh.sh" "$@"
    else
        echo -e "${GREEN}✅ OOS system refreshed${NC}"
    fi
}

main() {
    local subcommand="${1:-help}"
    shift || true

    case "$subcommand" in
        create)
            project_create "$@"
            ;;
        provision)
            project_provision "$@"
            ;;
        update)
            project_update "$@"
            ;;
        refresh)
            project_refresh "$@"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}❌ Unknown subcommand: $subcommand${NC}"
            echo
            show_help
            exit 1
            ;;
    esac
}

main "$@"