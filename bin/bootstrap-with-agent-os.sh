#!/bin/bash
# bootstrap-with-agent-os.sh - Enhanced OOS bootstrap with Agent-OS integration
set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OOS_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Usage information
usage() {
    cat << EOF
Usage: $0 [OPTIONS] [PROJECT_NAME] [PROJECT_DIR]

Bootstrap a new project with OOS and Agent-OS integration.

OPTIONS:
    -h, --help          Show this help message
    -f, --force         Overwrite existing files
    --agent-os-only     Only set up Agent-OS (skip standard OOS)
    --dry-run          Show what would be done without making changes

ARGUMENTS:
    PROJECT_NAME        Name of the project (optional, will prompt)
    PROJECT_DIR         Directory to create project in (optional, defaults to ./PROJECT_NAME)

EXAMPLES:
    $0 my-project               # Create project with standard OOS + Agent-OS
    $0 --agent-os-only ./       # Add Agent-OS to existing project
    $0 --dry-run my-project     # Preview what would be created

EOF
}

# Parse command line arguments
FORCE=false
AGENT_OS_ONLY=false
DRY_RUN=false
PROJECT_NAME=""
PROJECT_DIR=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        --agent-os-only)
            AGENT_OS_ONLY=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -*)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
        *)
            if [[ -z "$PROJECT_NAME" ]]; then
                PROJECT_NAME="$1"
            elif [[ -z "$PROJECT_DIR" ]]; then
                PROJECT_DIR="$1"
            else
                log_error "Too many arguments"
                usage
                exit 1
            fi
            shift
            ;;
    esac
done

# Get project name if not provided
if [[ -z "$PROJECT_NAME" && "$AGENT_OS_ONLY" == false ]]; then
    read -p "Enter project name: " PROJECT_NAME
    if [[ -z "$PROJECT_NAME" ]]; then
        log_error "Project name is required"
        exit 1
    fi
fi

# Set default project directory
if [[ -z "$PROJECT_DIR" ]]; then
    if [[ "$AGENT_OS_ONLY" == true ]]; then
        PROJECT_DIR="$(pwd)"
    else
        PROJECT_DIR="$(pwd)/$PROJECT_NAME"
    fi
fi

# Convert to absolute path
PROJECT_DIR="$(cd "$(dirname "$PROJECT_DIR")" && pwd)/$(basename "$PROJECT_DIR")"

# Validation
if [[ "$AGENT_OS_ONLY" == false && "$DRY_RUN" == false ]]; then
    if [[ -d "$PROJECT_DIR" && "$FORCE" == false ]]; then
        log_error "Project directory already exists: $PROJECT_DIR"
        log_info "Use --force to overwrite or choose a different name"
        exit 1
    fi
fi

# Function to run standard OOS bootstrap
run_standard_bootstrap() {
    local project_name="$1"
    local project_dir="$2"

    log_info "Running standard OOS bootstrap..."

    # Check if standard bootstrap script exists
    local bootstrap_script="$OOS_ROOT/scripts/bootstrap_enhanced.sh"
    if [[ ! -f "$bootstrap_script" ]]; then
        log_warning "Standard bootstrap script not found: $bootstrap_script"
        log_info "Creating basic project structure..."

        if [[ "$DRY_RUN" == false ]]; then
            # Create basic project structure
            mkdir -p "$project_dir"
            cd "$project_dir"

            # Create basic files
            echo "# $project_name" > README.md
            echo "node_modules/" > .gitignore
            echo "dist/" >> .gitignore
            echo ".env" >> .gitignore

            # Create basic package.json if it doesn't exist
            if [[ ! -f "package.json" ]]; then
                cat > package.json << EOF
{
  "name": "$(echo "$project_name" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')",
  "version": "1.0.0",
  "description": "$project_name",
  "main": "index.js",
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "keywords": [],
  "author": "",
  "license": "MIT"
}
EOF
            fi
        fi
        return 0
    fi

    # Run the existing bootstrap script
    if [[ "$DRY_RUN" == true ]]; then
        log_info "[DRY RUN] Would run: $bootstrap_script --verbose $project_name $project_dir"
    else
        if [[ "$FORCE" == true ]]; then
            "$bootstrap_script" --verbose --force "$project_name" "$project_dir"
        else
            "$bootstrap_script" --verbose "$project_name" "$project_dir"
        fi
    fi
}

# Function to run Agent-OS setup
run_agent_os_setup() {
    local project_dir="$1"

    log_info "Setting up Agent-OS integration..."

    local agent_os_script="$OOS_ROOT/bin/setup-agent-os.sh"
    if [[ ! -f "$agent_os_script" ]]; then
        log_error "Agent-OS setup script not found: $agent_os_script"
        return 1
    fi

    # Run Agent-OS setup
    local args=""
    if [[ "$FORCE" == true ]]; then
        args="$args --force"
    fi
    if [[ "$DRY_RUN" == true ]]; then
        args="$args --dry-run"
    fi

    "$agent_os_script" $args "$project_dir"
}

# Function to create enhanced integration script
create_integration_script() {
    local project_dir="$1"

    if [[ "$DRY_RUN" == true ]]; then
        log_info "[DRY RUN] Would create integration script"
        return 0
    fi

    local script_path="$project_dir/bin/init-full-system.sh"
    local bin_dir="$(dirname "$script_path")"

    # Create bin directory if it doesn't exist
    mkdir -p "$bin_dir"

    # Create comprehensive initialization script
    cat > "$script_path" << 'EOF'
#!/bin/bash
# init-full-system.sh - Initialize complete OOS + Agent-OS system
set -euo pipefail

echo "🚀 Initializing complete OOS + Agent-OS system..."

# Check prerequisites
if ! command -v sqlite3 &> /dev/null; then
    echo "❌ sqlite3 is required but not installed"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ python3 is required but not installed"
    exit 1
fi

# 1. Set up environment if not exists
if [[ ! -f .env ]]; then
    echo "📝 Creating environment file from template..."
    if [[ -f .env.template ]]; then
        cp .env.template .env
        echo "✅ Created .env from template"
        echo "⚠️  Please edit .env with your specific configuration"
    else
        echo "❌ No .env.template found"
    fi
fi

# 2. Initialize database
echo "🗄️  Initializing Atlas database..."
if [[ -f bin/setup-atlas-db.sh ]]; then
    ./bin/setup-atlas-db.sh
else
    echo "⚠️  No database setup script found"
fi

# 3. Set up global Agent-OS configuration
echo "🌐 Setting up global Agent-OS configuration..."
if command -v "$OOS_ROOT/bin/setup-agent-os.sh" &> /dev/null; then
    "$OOS_ROOT/bin/setup-agent-os.sh" --global
else
    echo "⚠️  Global Agent-OS setup script not found"
fi

# 4. Run health check
echo "🏥 Running health check..."
if [[ -f bin/agent-os-health.py ]]; then
    python3 bin/agent-os-health.py --verbose
else
    echo "⚠️  Health check script not found"
fi

# 5. Create Archon project (if configured)
echo "📋 Creating Archon project..."
if [[ -f bin/create_archon_project.sh ]]; then
    echo "Run: ./bin/create_archon_project.sh \"Project Name\" \"Description\""
else
    echo "⚠️  Archon project creation script not found"
fi

echo
echo "✅ System initialization complete!"
echo
echo "📖 Next steps:"
echo "1. Edit .env with your configuration"
echo "2. Review .agent-os/ documentation"
echo "3. Set up Google Sheets integration (see MIRROR_CONTRACT.md)"
echo "4. Create your first Archon project"
echo "5. Start developing with Agent-OS guidance!"
EOF

    chmod +x "$script_path"
    log_success "Created: Complete system initialization script"
}

# Function to create enhanced README
create_enhanced_readme() {
    local project_dir="$1"
    local project_name="$2"

    if [[ "$DRY_RUN" == true ]]; then
        log_info "[DRY RUN] Would enhance README"
        return 0
    fi

    local readme_path="$project_dir/README.md"

    # Check if README already has Agent-OS section
    if [[ -f "$readme_path" ]] && grep -q "Agent-OS" "$readme_path"; then
        log_info "README already contains Agent-OS section"
        return 0
    fi

    # Add Agent-OS section to README
    cat >> "$readme_path" << EOF

## 🤖 Agent-OS Integration

This project is integrated with Agent-OS for spec-driven development and human-in-the-loop automation.

### Quick Start

1. **Initialize the system**:
   \`\`\`bash
   ./bin/init-full-system.sh
   \`\`\`

2. **Check system health**:
   \`\`\`bash
   python3 bin/agent-os-health.py --verbose
   \`\`\`

3. **Review agent specifications**:
   - [Agent Operating Instructions](.agent-os/AGENT.md)
   - [Preferred Stack Configuration](.agent-os/PREFERRED_STACK.md)
   - [Mirror Contract Specification](.agent-os/MIRROR_CONTRACT.md)
   - [Operational Runbook](.agent-os/RUNBOOK.md)

### Architecture

- **Source of Truth**: SQLite database at \`./data/atlas.db\`
- **Human Interface**: Google Sheets for approvals and monitoring
- **Read-Only Access**: Datasette (via SSH tunnel)
- **Direct Editing**: sqlite-web (via SSH tunnel for maintenance)
- **Automation**: systemd timers for sync and backup
- **Backups**: Local + OCI Block Volume snapshots

### Development Workflow

1. **Check current tasks**: Query SQLite or check Google Sheets
2. **Update task status**: Mark as 'doing' when starting
3. **Follow agent specifications**: See \`.agent-os/AGENT.md\`
4. **Request approvals**: Use Google Sheets for critical changes
5. **Complete tasks**: Mark as 'review' or 'done' when finished

### Monitoring

- **Health checks**: \`python3 bin/agent-os-health.py\`
- **Database status**: \`sqlite3 data/atlas.db "SELECT * FROM tasks WHERE status='doing';"\`
- **Recent activity**: Check Google Sheets or Datasette interface
- **System logs**: \`journalctl -u atlas-*\` for systemd services

### Learning System

This project participates in cross-project learning:
- Global patterns: \`~/.agent-os/LEARNING_PATTERNS.md\`
- Project lessons: \`.agent-os/LESSONS.md\` (create as needed)
- Archon knowledge base: Searchable examples and documentation

### Support

- **Documentation**: \`.agent-os/\` directory contains all specifications
- **Health issues**: Run health check script for diagnostics
- **Operational procedures**: See \`.agent-os/RUNBOOK.md\`
- **Learning resources**: Review global Agent-OS patterns
EOF

    log_success "Enhanced README with Agent-OS documentation"
}

# Main execution
main() {
    log_info "OOS + Agent-OS Bootstrap"
    log_info "======================="

    if [[ "$DRY_RUN" == true ]]; then
        log_warning "DRY RUN MODE - No files will be created"
    fi

    # Step 1: Standard OOS bootstrap (unless Agent-OS only)
    if [[ "$AGENT_OS_ONLY" == false ]]; then
        run_standard_bootstrap "$PROJECT_NAME" "$PROJECT_DIR"
    fi

    # Step 2: Agent-OS setup
    run_agent_os_setup "$PROJECT_DIR"

    # Step 3: Enhanced integration components
    if [[ "$AGENT_OS_ONLY" == false ]]; then
        create_integration_script "$PROJECT_DIR"
        create_enhanced_readme "$PROJECT_DIR" "$PROJECT_NAME"
    fi

    # Summary
    echo
    log_success "Bootstrap complete!"

    if [[ "$DRY_RUN" == true ]]; then
        log_info "This was a dry run. No files were actually created."
    else
        log_info "Project created: $PROJECT_DIR"

        if [[ "$AGENT_OS_ONLY" == false ]]; then
            log_info ""
            log_info "🚀 Quick start:"
            log_info "  cd $PROJECT_DIR"
            log_info "  ./bin/init-full-system.sh"
            log_info ""
            log_info "📖 Documentation:"
            log_info "  .agent-os/AGENT.md          - How agents should work"
            log_info "  .agent-os/PREFERRED_STACK.md - Technology choices"
            log_info "  .agent-os/MIRROR_CONTRACT.md - Sheets integration"
            log_info "  .agent-os/RUNBOOK.md        - Operations procedures"
        else
            log_info ""
            log_info "✅ Agent-OS integration added to existing project"
            log_info "📖 Review .agent-os/ directory for specifications"
        fi
    fi
}

# Run main function
main "$@"