# AgenticZero 项目记忆

## 代码检查命令

在修改代码后，必须执行以下 Makefile 命令来确保代码质量：

### 基本检查命令
- `make lint` - 运行 ruff 代码检查
- `make type-check` - 运行 pyright 类型检查
- `make format-check` - 检查代码格式（不修改）
- `make test` - 运行测试

### 自动修复命令
- `make format` - 自动格式化代码
- `make lint-fix` - 自动修复可修复的 lint 问题

### 综合命令
- `make check` - 运行所有检查（format-check, lint, type-check, test）
- `make all` - 格式化并运行所有检查（format, lint-fix, type-check, test）

### 建议的工作流程
1. 修改代码后先运行 `make format` 格式化代码
2. 运行 `make check` 确保所有检查通过
3. 如果有 lint 错误，可以使用 `make lint-fix` 自动修复
4. 提交代码前确保 `make check` 全部通过