#!/bin/bash
# OOS Archon Knowledge Base and Project Management
# Consolidates: archon-research, archon-status

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
📊 Archon Knowledge Base and Project Management

USAGE:
    /archon <subcommand> [arguments]

SUBCOMMANDS:
    research <query>    Search knowledge base for information
    status              Show current project and task status
    search <query>      Search projects and tasks
    help                Show this help

EXAMPLES:
    /archon research "slash command patterns"
    /archon status
    /archon search "authentication"

ARCHON MCP INTEGRATION:
    This command requires Archon MCP server connection.
    Uses: rag_search_knowledge_base, find_projects, find_tasks

CONSOLIDATES:
    /archon-research → /archon research
    /archon-status → /archon status

EOF
}

archon_research() {
    local query="$*"

    if [ -z "$query" ]; then
        echo -e "${RED}❌ Please provide a search query${NC}"
        echo "Usage: /archon research <query>"
        return 1
    fi

    echo -e "${CYAN}🔍 Researching: \"$query\"${NC}"
    echo

    # This would typically call the MCP tools
    # For now, provide helpful output
    echo -e "${BLUE}📚 Searching knowledge base...${NC}"
    echo "Query: $query"
    echo
    echo -e "${GREEN}💡 This will integrate with Archon MCP tools:${NC}"
    echo "  • mcp__archon__rag_search_knowledge_base"
    echo "  • mcp__archon__search_code_examples"
    echo
    echo -e "${YELLOW}⚠️  MCP integration pending - use original /archon-research for now${NC}"
}

archon_status() {
    echo -e "${CYAN}📊 Archon Project Status${NC}"
    echo "=========================="
    echo

    echo -e "${BLUE}🎯 Current Projects:${NC}"
    echo "  • OOS Slash Command Consolidation (active)"
    echo "  • Personal Operational Intelligence System (completed)"
    echo

    echo -e "${BLUE}📋 Active Tasks:${NC}"
    echo "  • Create unified command implementation scripts (doing)"
    echo "  • Test consolidated commands (todo)"
    echo

    echo -e "${GREEN}💡 This will integrate with Archon MCP tools:${NC}"
    echo "  • mcp__archon__find_projects"
    echo "  • mcp__archon__find_tasks"
    echo
    echo -e "${YELLOW}⚠️  MCP integration pending - use original /archon-status for now${NC}"
}

archon_search() {
    local query="$*"

    if [ -z "$query" ]; then
        echo -e "${RED}❌ Please provide a search query${NC}"
        echo "Usage: /archon search <query>"
        return 1
    fi

    echo -e "${CYAN}🔍 Searching projects and tasks: \"$query\"${NC}"
    echo

    echo -e "${GREEN}💡 This will search across:${NC}"
    echo "  • Project titles and descriptions"
    echo "  • Task titles and descriptions"
    echo "  • Documentation content"
    echo
    echo -e "${YELLOW}⚠️  MCP integration pending${NC}"
}

main() {
    local subcommand="${1:-help}"
    shift || true

    case "$subcommand" in
        research)
            archon_research "$@"
            ;;
        status)
            archon_status "$@"
            ;;
        search)
            archon_search "$@"
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