# slash-command-consistency-fix

A Python project with OOS modular architecture.

## Development Setup

```bash
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
uv run python -m slash-command-consistency-fix.main
```

## OOS Integration

This project uses OOS modular architecture:

- `/modules` - Run individual modules
- `/dev-setup` - Complete environment validation
- `/pre-commit` - Pre-commit validation workflow

## Project Structure

```
slash-command-consistency-fix/
├── src/slash-command-consistency-fix/          # Main package
├── tests/                      # Test files
├── docs/                       # Documentation
├── pyproject.toml             # Project configuration
└── README.md                  # This file
```
