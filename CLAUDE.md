# AgenticZero 项目记忆

## 代码检查命令

### 重要：编写代码前的准备
在编写或修改代码前，建议先查看相关配置文件以了解项目规范：
- `ruff.toml` - 代码风格和 lint 规则配置
- `pyrightconfig.json` - 类型检查配置
- `pyproject.toml` - 项目依赖和工具配置

了解这些配置可以帮助你在编写代码时就遵循项目规范，减少后续检查报错，提高开发效率。

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

## 测试编写规范

### 1. 使用 pytest 框架
所有测试必须使用 pytest 框架编写，不要创建可独立运行的测试脚本。

### 2. 必须添加 pytest 标记
- 所有测试函数必须添加适当的 `@pytest.mark` 装饰器
- 异步测试必须添加 `@pytest.mark.asyncio`
- 按测试类型添加标记：
  - `@pytest.mark.unit` - 单元测试
  - `@pytest.mark.integration` - 集成测试
  - `@pytest.mark.slow` - 慢速测试

### 3. 测试文件规范
- 测试文件必须以 `test_` 开头或 `_test` 结尾
- 测试函数必须以 `test_` 开头
- 测试类必须以 `Test` 开头

### 4. 禁止使用 main 函数
- **不要**在测试文件中添加 `if __name__ == "__main__"` 块
- **不要**创建 `main()` 函数来运行测试
- 测试只能通过 pytest 执行

### 5. 测试执行方式
- 运行所有测试：`make test` 或 `pytest`
- 运行特定标记的测试：`pytest -m unit`
- 运行特定文件：`pytest path/to/test_file.py -v`
- 运行特定测试：`pytest path/to/test_file.py::test_function -v`

### 6. 示例
```python
import pytest

@pytest.mark.unit
def test_simple_function():
    """测试简单函数"""
    assert 1 + 1 == 2

@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_function():
    """测试异步函数"""
    result = await some_async_function()
    assert result is not None

# 不要添加以下代码：
# if __name__ == "__main__":
#     pytest.main([__file__])
```