.PHONY: help test lint type-check format format-check clean install dev-install all check

# Default target
.DEFAULT_GOAL := help

# Help command
help:
	@echo "Available commands:"
	@echo "  make install       Install production dependencies"
	@echo "  make dev-install   Install all dependencies (including dev)"
	@echo "  make test          Run tests with coverage"
	@echo "  make lint          Run ruff linter"
	@echo "  make type-check    Run pyright type checker"
	@echo "  make format        Format code with ruff"
	@echo "  make format-check  Check code formatting without changes"
	@echo "  make check         Run all checks (lint, type-check, format-check, test)"
	@echo "  make clean         Clean up cache and build files"
	@echo "  make all           Run format, lint, type-check, and test"

# Install dependencies
install:
	uv sync --no-dev

dev-install:
	uv sync

# Run tests
test:
	uv run pytest

# Run tests with minimal output
test-quiet:
	uv run pytest -q

# Run specific test file
test-file:
	@read -p "Enter test file path: " filepath; \
	uv run pytest $$filepath -v

# Lint code
lint:
	uv run ruff check .

# Lint and auto-fix
lint-fix:
	uv run ruff check --fix .

# Type check
type-check:
	uv run pyright

# Format code
format:
	uv run ruff format .

# Check formatting without making changes
format-check:
	uv run ruff format --check .

# Run all checks
check: format-check lint type-check test

# Run all formatting and checks
all: format lint-fix type-check test

# Clean up
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '.pytest_cache' -exec rm -rf {} +
	find . -type d -name '.ruff_cache' -exec rm -rf {} +
	find . -type d -name '.mypy_cache' -exec rm -rf {} +
	find . -type d -name 'htmlcov' -exec rm -rf {} +
	find . -type f -name '.coverage' -delete
	find . -type f -name 'coverage.xml' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	find . -type d -name 'build' -exec rm -rf {} +
	find . -type d -name 'dist' -exec rm -rf {} +

# Watch mode for tests
test-watch:
	uv run pytest-watch

# Run tests with verbose output
test-verbose:
	uv run pytest -vv

# Run only fast tests
test-fast:
	uv run pytest -m "not slow"

# Run coverage report
coverage:
	uv run pytest --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

# Open coverage report in browser (Linux/WSL)
coverage-open: coverage
	@if command -v xdg-open > /dev/null; then \
		xdg-open htmlcov/index.html; \
	elif command -v open > /dev/null; then \
		open htmlcov/index.html; \
	else \
		echo "Please open htmlcov/index.html in your browser"; \
	fi