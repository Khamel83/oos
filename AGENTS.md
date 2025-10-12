# Project Overview
This is a Python project using modern tooling for consistency and reproducibility.

# Setup and Build
- Python version: 3.12+ (managed by uv)
- Package manager: uv (unified Python package manager)
- Run `uv sync` to install dependencies
- Run `uv run pytest` to execute tests

# Development Environment
- Use VS Code Dev Container for consistent environment (.devcontainer/)
- Docker required for containerized development
- All dependencies locked in uv.lock for reproducibility

# Code Style and Formatting
- Use ruff for linting and formatting (replaces Black, isort, Flake8)
- Run `uv run ruff check .` for linting
- Run `uv run ruff format .` for formatting
- Type checking with mypy: `uv run mypy src/`
- Line length: 88 characters (Black-compatible)

# Testing
- Framework: pytest with coverage reporting
- Run tests: `uv run pytest`
- Run with coverage: `uv run pytest --cov=src`
- All tests in tests/ directory
- Target: 80%+ code coverage

# Commit and PR Guidelines
- Pre-commit hooks enforce code quality (run automatically)
- Manual run: `uv run pre-commit run --all-files`
- All PRs require passing CI checks (GitHub Actions)
- Write clear commit messages describing changes

# CI/CD
- GitHub Actions runs on all pushes and PRs
- Tests run on Python 3.10, 3.11, and 3.12
- Checks: ruff linting, mypy type checking, pytest with coverage
- Badge status visible in README

# Architecture
- Source code: src/ directory
- Tests: tests/ directory
- Configuration: pyproject.toml (unified config)
- Dependencies: managed by uv, locked in uv.lock
