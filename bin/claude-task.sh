#!/bin/bash
# OOS Task Management - Real Implementation
# Uses the actual Python CLI (src/oos_task_system/cli.py)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if we're in the OOS repo (has task system)
if [[ ! -d "$PROJECT_ROOT/src/oos_task_system" ]]; then
    echo -e "${YELLOW}⚠️  Task system not available in this project${NC}"
    echo "   This is a lightweight OOS install (commands only)"
    echo "   For full task system, use the OOS repository"
    exit 0
fi

# Check if dependencies are installed
if [[ ! -d "$PROJECT_ROOT/.venv" ]]; then
    echo -e "${RED}❌ Dependencies not installed${NC}"
    echo "   Run: uv sync"
    exit 1
fi

# Check if uv is available
if ! command -v uv &> /dev/null; then
    # Fallback to .venv/bin/python
    PYTHON_CMD="$PROJECT_ROOT/.venv/bin/python"
else
    # Use uv run (preferred)
    PYTHON_CMD="uv run python"
fi

# Run the actual task CLI
cd "$PROJECT_ROOT"
exec $PYTHON_CMD -m src.oos_task_system.cli "$@"