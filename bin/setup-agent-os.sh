#!/bin/bash
# setup-agent-os.sh - Set up Agent-OS integration for a project
set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OOS_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATES_DIR="$OOS_ROOT/templates/agent-os"

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
Usage: $0 [OPTIONS] [PROJECT_DIR]

Set up Agent-OS integration for a project.

OPTIONS:
    -h, --help          Show this help message
    -f, --force         Overwrite existing files
    -g, --global        Set up global user configuration
    --dry-run          Show what would be done without making changes

EXAMPLES:
    $0                  # Set up Agent-OS in current directory
    $0 /path/to/project # Set up Agent-OS in specific directory
    $0 --global         # Set up global user configuration
    $0 --dry-run        # Preview changes

EOF
}

# Parse command line arguments
FORCE=false
GLOBAL=false
DRY_RUN=false
PROJECT_DIR="${PWD}"

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
        -g|--global)
            GLOBAL=true
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
            PROJECT_DIR="$1"
            shift
            ;;
    esac
done

# Validate project directory
if [[ "$GLOBAL" == false ]]; then
    if [[ ! -d "$PROJECT_DIR" && "$DRY_RUN" == false ]]; then
        log_error "Project directory does not exist: $PROJECT_DIR"
        exit 1
    fi

    # Convert to absolute path (only if directory exists)
    if [[ -d "$PROJECT_DIR" ]]; then
        PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"
    fi
    log_info "Setting up Agent-OS in: $PROJECT_DIR"
else
    PROJECT_DIR="$HOME"
    log_info "Setting up global Agent-OS configuration"
fi

# Check if templates exist
if [[ ! -d "$TEMPLATES_DIR" ]]; then
    log_error "Templates directory not found: $TEMPLATES_DIR"
    exit 1
fi

# Function to copy file with safety checks
copy_file() {
    local src="$1"
    local dest="$2"
    local description="$3"

    if [[ "$DRY_RUN" == true ]]; then
        log_info "[DRY RUN] Would copy: $description"
        return 0
    fi

    # Create destination directory if it doesn't exist
    local dest_dir="$(dirname "$dest")"
    if [[ ! -d "$dest_dir" ]]; then
        mkdir -p "$dest_dir"
        log_info "Created directory: $dest_dir"
    fi

    # Check if destination exists
    if [[ -f "$dest" ]]; then
        if [[ "$FORCE" == true ]]; then
            # Create backup
            cp "$dest" "$dest.backup.$(date +%Y%m%d_%H%M%S)"
            log_warning "Backed up existing file: $dest"
        else
            log_warning "File already exists (use --force to overwrite): $dest"
            return 0
        fi
    fi

    # Copy the file
    cp "$src" "$dest"
    log_success "Created: $description"
}

# Function to create directory structure
create_directory() {
    local dir="$1"
    local description="$2"

    if [[ "$DRY_RUN" == true ]]; then
        log_info "[DRY RUN] Would create directory: $description"
        return 0
    fi

    if [[ ! -d "$dir" ]]; then
        mkdir -p "$dir"
        log_success "Created directory: $description"
    else
        log_info "Directory already exists: $description"
    fi
}

# Function to set up project-specific Agent-OS files
setup_project() {
    local project_dir="$1"

    log_info "Setting up project-specific Agent-OS configuration..."

    # Create .agent-os directory
    local agent_os_dir="$project_dir/.agent-os"
    create_directory "$agent_os_dir" ".agent-os configuration directory"

    # Copy project-level templates
    copy_file "$TEMPLATES_DIR/AGENT.md" "$agent_os_dir/AGENT.md" "Agent operating instructions"
    copy_file "$TEMPLATES_DIR/PREFERRED_STACK.md" "$agent_os_dir/PREFERRED_STACK.md" "Preferred stack configuration"
    copy_file "$TEMPLATES_DIR/MIRROR_CONTRACT.md" "$agent_os_dir/MIRROR_CONTRACT.md" "Mirror contract specification"
    copy_file "$TEMPLATES_DIR/RUNBOOK.md" "$agent_os_dir/RUNBOOK.md" "Operational runbook"

    # Create data directory structure
    local data_dir="$project_dir/data"
    create_directory "$data_dir" "Data directory"
    create_directory "$data_dir/backups" "Backups directory"

    # Create .env.template if it doesn't exist
    local env_template="$project_dir/.env.template"
    if [[ ! -f "$env_template" && "$DRY_RUN" == false ]]; then
        cat > "$env_template" << 'EOF'
# Agent-OS Configuration
ATLAS_DB_PATH=./data/atlas.db
GOOGLE_SHEETS_CREDENTIALS_FILE=./config/sheets-credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id_here

# OOS Integration
ARCHON_URL=http://localhost:8051
ARCHON_PROJECT_ID=your_project_id_here

# Monitoring
ALERT_EMAIL=your_email@example.com
HEALTH_CHECK_INTERVAL=900  # 15 minutes

# Backup Configuration
BACKUP_RETENTION_DAYS=30
BACKUP_LOCAL_PATH=./data/backups
EOF
        log_success "Created: .env.template"
    fi

    # Add to .gitignore if it exists
    local gitignore="$project_dir/.gitignore"
    if [[ -f "$gitignore" && "$DRY_RUN" == false ]]; then
        # Check if Agent-OS entries are already present
        if ! grep -q "# Agent-OS" "$gitignore"; then
            cat >> "$gitignore" << 'EOF'

# Agent-OS
.env
data/atlas.db*
data/backups/
config/sheets-credentials.json
*.log
EOF
            log_success "Updated: .gitignore with Agent-OS entries"
        else
            log_info ".gitignore already contains Agent-OS entries"
        fi
    fi
}

# Function to set up global user configuration
setup_global() {
    local home_dir="$1"

    log_info "Setting up global Agent-OS configuration..."

    # Create ~/.agent-os directory
    local global_agent_os_dir="$home_dir/.agent-os"
    create_directory "$global_agent_os_dir" "Global .agent-os configuration directory"

    # Copy global templates
    copy_file "$TEMPLATES_DIR/global/GLOBAL_RULES.md" "$global_agent_os_dir/GLOBAL_RULES.md" "Global agent rules"
    copy_file "$TEMPLATES_DIR/global/STACK_PREFERENCES.md" "$global_agent_os_dir/STACK_PREFERENCES.md" "Global stack preferences"
    copy_file "$TEMPLATES_DIR/global/LEARNING_PATTERNS.md" "$global_agent_os_dir/LEARNING_PATTERNS.md" "Global learning patterns"

    # Create config directory
    create_directory "$global_agent_os_dir/config" "Global configuration directory"

    # Create a sample global config file
    local global_config="$global_agent_os_dir/config/global.env"
    if [[ ! -f "$global_config" && "$DRY_RUN" == false ]]; then
        cat > "$global_config" << 'EOF'
# Global Agent-OS Configuration

# Default Archon server
DEFAULT_ARCHON_URL=http://localhost:8051

# Default notification settings
DEFAULT_ALERT_EMAIL=your_email@example.com

# Default backup settings
DEFAULT_BACKUP_RETENTION_DAYS=30

# Learning system settings
LEARNING_ENFORCEMENT=true
LEARNING_REVIEW_REQUIRED=true
EOF
        log_success "Created: Global configuration file"
    fi
}

# Function to create basic SQLite setup script
create_db_setup() {
    local project_dir="$1"

    if [[ "$DRY_RUN" == true ]]; then
        log_info "[DRY RUN] Would create database setup script"
        return 0
    fi

    local setup_script="$project_dir/bin/setup-atlas-db.sh"
    local bin_dir="$(dirname "$setup_script")"

    create_directory "$bin_dir" "bin directory"

    if [[ ! -f "$setup_script" ]]; then
        cat > "$setup_script" << 'EOF'
#!/bin/bash
# setup-atlas-db.sh - Initialize Atlas SQLite database
set -euo pipefail

# Load environment variables
if [[ -f .env ]]; then
    source .env
fi

# Default database path
DB_PATH="${ATLAS_DB_PATH:-./data/atlas.db}"
DB_DIR="$(dirname "$DB_PATH")"

# Create data directory
mkdir -p "$DB_DIR"

# Initialize database if it doesn't exist
if [[ ! -f "$DB_PATH" ]]; then
    echo "Initializing Atlas database: $DB_PATH"

    sqlite3 "$DB_PATH" << 'SQL'
-- Enable WAL mode for concurrency
PRAGMA journal_mode=WAL;

-- Set timeouts for reliability
PRAGMA busy_timeout=30000;

-- Optimize for read-heavy workload
PRAGMA cache_size=10000;
PRAGMA synchronous=NORMAL;

-- Projects table
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tasks table
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES projects(id),
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'todo',
    assignee TEXT DEFAULT 'User',
    priority INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    approved_at DATETIME,
    approved_by TEXT
);

-- Approvals table (human loop)
CREATE TABLE approvals (
    id TEXT PRIMARY KEY,
    item_type TEXT NOT NULL,
    item_id TEXT NOT NULL,
    action TEXT NOT NULL,
    payload JSON NOT NULL,
    status TEXT DEFAULT 'pending',
    requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reviewed_at DATETIME,
    reviewed_by TEXT,
    notes TEXT
);

-- Runs table (execution tracking)
CREATE TABLE runs (
    id TEXT PRIMARY KEY,
    task_id TEXT REFERENCES tasks(id),
    command TEXT NOT NULL,
    status TEXT DEFAULT 'running',
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    output TEXT,
    error_log TEXT
);

-- Create indexes for performance
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_approvals_status ON approvals(status);
CREATE INDEX idx_runs_task_id ON runs(task_id);
CREATE INDEX idx_runs_status ON runs(status);

-- Insert sample data
INSERT INTO projects (id, name, description) VALUES
('proj-001', 'Sample Project', 'A sample project to demonstrate Agent-OS integration');

INSERT INTO tasks (id, project_id, title, description, status) VALUES
('task-001', 'proj-001', 'Set up Agent-OS', 'Complete Agent-OS integration setup', 'done');

SQL

    echo "Database initialized successfully!"
    echo "Location: $DB_PATH"

    # Verify the setup
    echo "Verifying database setup..."
    sqlite3 "$DB_PATH" "SELECT name FROM sqlite_master WHERE type='table';"

else
    echo "Database already exists: $DB_PATH"
    echo "To reinitialize, delete the database file and run this script again."
fi
EOF
        chmod +x "$setup_script"
        log_success "Created: Database setup script"
    fi
}

# Main execution
main() {
    log_info "Agent-OS Setup Script"
    log_info "===================="

    # Validate templates directory
    if [[ ! -d "$TEMPLATES_DIR" ]]; then
        log_error "Templates directory not found. Please run this script from the OOS root directory."
        exit 1
    fi

    # Set up based on mode
    if [[ "$GLOBAL" == true ]]; then
        setup_global "$PROJECT_DIR"
    else
        setup_project "$PROJECT_DIR"
        create_db_setup "$PROJECT_DIR"
    fi

    # Summary
    echo
    log_success "Agent-OS setup complete!"

    if [[ "$DRY_RUN" == true ]]; then
        log_info "This was a dry run. No files were actually created."
    else
        if [[ "$GLOBAL" == true ]]; then
            log_info "Global configuration created in: $HOME/.agent-os/"
            log_info "Next steps:"
            log_info "1. Review and customize global configuration files"
            log_info "2. Set up your default Archon server URL"
            log_info "3. Configure notification preferences"
        else
            log_info "Project configuration created in: $PROJECT_DIR/.agent-os/"
            log_info "Next steps:"
            log_info "1. Copy .env.template to .env and configure values"
            log_info "2. Run ./bin/setup-atlas-db.sh to initialize database"
            log_info "3. Review and customize Agent-OS configuration files"
            log_info "4. Set up Google Sheets integration (see MIRROR_CONTRACT.md)"
        fi
    fi
}

# Run main function
main "$@"