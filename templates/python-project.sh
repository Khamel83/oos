#!/usr/bin/env bash
# Template: python-project
# Purpose: Bootstrap a Python project with OOS modular architecture
# Input: project_name [project_path]
# Output: Complete Python project with OOS integration

set -euo pipefail

PROJECT_NAME="$1"
PROJECT_PATH="${2:-$PROJECT_NAME}"

if [[ -z "$PROJECT_NAME" ]]; then
    echo "Usage: $0 <project_name> [project_path]"
    exit 1
fi

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}${BLUE}🐍 Creating Python Project: $PROJECT_NAME${NC}"
echo "============================================"

# Create project structure
echo -e "${BLUE}📁 Creating project structure...${NC}"
mkdir -p "$PROJECT_PATH"/{src,tests,docs}
cd "$PROJECT_PATH"

# Create pyproject.toml
echo -e "${BLUE}📝 Creating pyproject.toml...${NC}"
cat > pyproject.toml << EOF
[project]
name = "$PROJECT_NAME"
version = "0.1.0"
description = "A Python project with OOS modular architecture"
authors = [{name = "Your Name", email = "your.email@example.com"}]
dependencies = []
requires-python = ">=3.9"

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "ruff>=0.1.0",
    "black>=23.0",
    "mypy>=1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src --cov-report=term-missing"

[tool.ruff]
line-length = 88
target-version = "py39"

[tool.black]
line-length = 88
target-version = ['py39']

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
EOF

# Create main module
echo -e "${BLUE}🐍 Creating main module...${NC}"
mkdir -p "src/$PROJECT_NAME"
cat > "src/$PROJECT_NAME/__init__.py" << EOF
"""$PROJECT_NAME: A Python project with OOS modular architecture."""

__version__ = "0.1.0"
EOF

cat > "src/$PROJECT_NAME/main.py" << EOF
"""Main module for $PROJECT_NAME."""


def hello_world() -> str:
    """Return a greeting message."""
    return "Hello from $PROJECT_NAME!"


def main() -> None:
    """Main entry point."""
    print(hello_world())


if __name__ == "__main__":
    main()
EOF

# Create tests
echo -e "${BLUE}🧪 Creating tests...${NC}"
cat > "tests/__init__.py" << EOF
"""Tests for $PROJECT_NAME."""
EOF

cat > "tests/test_main.py" << EOF
"""Tests for main module."""

from $PROJECT_NAME.main import hello_world


def test_hello_world():
    """Test hello_world function."""
    result = hello_world()
    assert "Hello from $PROJECT_NAME" in result
    assert isinstance(result, str)
EOF

# Create README
echo -e "${BLUE}📖 Creating README...${NC}"
cat > README.md << EOF
# $PROJECT_NAME

A Python project with OOS modular architecture.

## Development Setup

\`\`\`bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run tests
uv run pytest

# Run linting
uv run ruff check src tests

# Format code
uv run black src tests

# Run the application
uv run python -m $PROJECT_NAME.main
\`\`\`

## OOS Integration

This project uses OOS modular architecture:

- \`/modules\` - Run individual modules
- \`/dev-setup\` - Complete environment validation
- \`/pre-commit\` - Pre-commit validation workflow

## Project Structure

\`\`\`
$PROJECT_NAME/
├── src/$PROJECT_NAME/          # Main package
├── tests/                      # Test files
├── docs/                       # Documentation
├── pyproject.toml             # Project configuration
└── README.md                  # This file
\`\`\`
EOF

# Create .gitignore
echo -e "${BLUE}📝 Creating .gitignore...${NC}"
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*\$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
oos-env/

# Testing
.tox/
.coverage
.pytest_cache/
htmlcov/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
EOF

echo -e "${GREEN}✅ Python project '$PROJECT_NAME' created successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. cd $PROJECT_PATH"
echo "2. uv sync                    # Install dependencies"
echo "3. /dev-setup                 # Validate environment (if OOS available)"
echo "4. uv run pytest             # Run tests"
echo "5. Start coding!"

exit 0