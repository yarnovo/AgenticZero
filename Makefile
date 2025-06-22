.PHONY: help test lint type-check format format-check clean install dev-install all check

# 默认目标
.DEFAULT_GOAL := help

# 帮助命令
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

# 安装依赖
install:
	uv sync --no-dev

dev-install:
	uv sync

# 运行测试
test:
	uv run pytest

# 以最小输出运行测试
test-quiet:
	uv run pytest -q

# 运行特定测试文件
test-file:
	@read -p "Enter test file path: " filepath; \
	uv run pytest $$filepath -v

# 代码检查
lint:
	uv run ruff check .

# 代码检查并自动修复
lint-fix:
	uv run ruff check --fix .

# 类型检查
type-check:
	uv run pyright

# 格式化代码
format:
	uv run ruff format .

# 检查格式化但不做更改
format-check:
	uv run ruff format --check .

# 运行所有检查
check: format-check lint type-check test

# 运行所有格式化和检查
all: format lint-fix type-check test

# 清理
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

# 测试监听模式
test-watch:
	uv run pytest-watch

# 以详细输出运行测试
test-verbose:
	uv run pytest -vv

# 仅运行快速测试
test-fast:
	uv run pytest -m "not slow"

# 运行覆盖率报告
coverage:
	uv run pytest --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

# 在浏览器中打开覆盖率报告 (Linux/WSL)
coverage-open: coverage
	@if command -v xdg-open > /dev/null; then \
		xdg-open htmlcov/index.html; \
	elif command -v open > /dev/null; then \
		open htmlcov/index.html; \
	else \
		echo "Please open htmlcov/index.html in your browser"; \
	fi