.PHONY: help test lint type-check format format-check clean install dev-install all check api api-dev api-reload frontend-dev frontend-build frontend-start frontend-install frontend-clean frontend-lint storybook storybook-build db-generate db-push db-migrate db-migrate-deploy db-migrate-reset db-studio db-seed db-format db-validate

# 默认目标
.DEFAULT_GOAL := help

# 帮助命令
help:
	@echo "=== 可用命令 ==="
	@echo ""
	@echo "基础命令:"
	@echo "  make install       安装生产环境依赖"
	@echo "  make dev-install   安装所有依赖（包括开发依赖）"
	@echo "  make test          运行测试并生成覆盖率报告"
	@echo "  make lint          运行 ruff 代码检查"
	@echo "  make type-check    运行 pyright 类型检查"
	@echo "  make format        使用 ruff 格式化代码"
	@echo "  make format-check  检查代码格式（不修改）"
	@echo "  make check         运行所有检查 (lint, type-check, format-check, test)"
	@echo "  make clean         清理缓存和构建文件"
	@echo "  make all           运行格式化、lint 修复、类型检查和测试"
	@echo ""
	@echo "API 相关命令:"
	@echo "  make api           生产模式运行 API 服务器"
	@echo "  make api-dev       开发模式运行 API 服务器（带自动重载）"
	@echo "  make api-reload    自动重载模式运行 API（api-dev 的别名）"
	@echo ""
	@echo "前端相关命令:"
	@echo "  make frontend-install  安装前端依赖"
	@echo "  make frontend-dev      开发模式运行前端"
	@echo "  make frontend-build    构建前端生产版本"
	@echo "  make frontend-start    生产模式运行前端"
	@echo "  make frontend-lint     运行前端代码检查"
	@echo "  make frontend-clean    清理前端构建文件"
	@echo ""
	@echo "Storybook 相关命令:"
	@echo "  make storybook         启动 Storybook 开发服务器"
	@echo "  make storybook-build   构建 Storybook 静态文件"
	@echo ""
	@echo "数据库相关命令:"
	@echo "  make db-generate       生成 Prisma 客户端"
	@echo "  make db-push           推送数据库架构变更"
	@echo "  make db-migrate        创建并应用开发环境迁移"
	@echo "  make db-migrate-deploy 部署生产环境迁移"
	@echo "  make db-migrate-reset  重置数据库和迁移"
	@echo "  make db-studio         打开 Prisma Studio 数据库管理界面"
	@echo "  make db-seed           运行数据库种子脚本"
	@echo "  make db-format         格式化 Prisma schema 文件"
	@echo "  make db-validate       验证 Prisma schema 文件"

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

# 运行前端代码检查
frontend-lint:
	cd frontend && npm run lint

# Storybook 相关命令
# 启动 Storybook 开发服务器
storybook:
	cd frontend && npm run storybook

# 构建 Storybook 静态文件
storybook-build:
	cd frontend && npm run build-storybook

# 数据库相关命令
# 生成 Prisma 客户端
db-generate:
	cd frontend && npm run db:generate

# 推送数据库架构变更
db-push:
	cd frontend && npm run db:push

# 创建并应用开发环境迁移
db-migrate:
	cd frontend && npm run db:migrate

# 部署生产环境迁移
db-migrate-deploy:
	cd frontend && npm run db:migrate:deploy

# 重置数据库和迁移
db-migrate-reset:
	cd frontend && npm run db:migrate:reset

# 打开 Prisma Studio 数据库管理界面
db-studio:
	cd frontend && npm run db:studio

# 运行数据库种子脚本
db-seed:
	cd frontend && npm run db:seed

# 格式化 Prisma schema 文件
db-format:
	cd frontend && npm run db:format

# 验证 Prisma schema 文件
db-validate:
	cd frontend && npm run db:validate