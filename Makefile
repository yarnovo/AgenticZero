.PHONY: help test lint type-check format format-check clean install dev-install all check api api-dev api-reload frontend-dev frontend-build frontend-start frontend-install frontend-clean

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
	@echo ""
	@echo "API commands:"
	@echo "  make api           Run API server in production mode"
	@echo "  make api-dev       Run API server in development mode with reload"
	@echo "  make api-reload    Run API server with auto-reload (alias for api-dev)"
	@echo ""
	@echo "Frontend commands:"
	@echo "  make frontend-install  Install frontend dependencies"
	@echo "  make frontend-dev      Run frontend in development mode"
	@echo "  make frontend-build    Build frontend for production"
	@echo "  make frontend-start    Start frontend in production mode"
	@echo "  make frontend-clean    Clean frontend build files"

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

# API 相关命令
# 生产模式运行 API
api:
	uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# 开发模式运行 API（带自动重载）
api-dev:
	uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# 自动重载模式的别名
api-reload: api-dev

# 前端相关命令
# 安装前端依赖
frontend-install:
	cd frontend && npm install

# 开发模式运行前端
frontend-dev:
	cd frontend && npm run dev

# 构建前端
frontend-build:
	cd frontend && npm run build

# 生产模式运行前端
frontend-start:
	cd frontend && npm run start

# 清理前端构建文件
frontend-clean:
	cd frontend && rm -rf .next node_modules