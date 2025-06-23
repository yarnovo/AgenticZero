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

## Frontend 组件安装规范

### 组件选择优先级（严格按此顺序）
1. **Shadcn-ui 组件优先**：优先使用 shadcn-ui 框架组件
2. **外部组件库**：如果 shadcn-ui 没有，查看其他知名组件库
3. **自定义组件**：只有在前两者都没有时才自定义实现

### Shadcn-ui 使用规范
- **基本安装命令**：`npx shadcn@latest add <component-name>`
- **配置文件**：`components.json`（已配置）
- **重要提醒**：部分组件需要额外依赖或特殊安装步骤
- **必须查看官网**：安装前务必访问 [ui.shadcn.com](https://ui.shadcn.com) 查看具体组件的安装说明
- **不要造轮子**：基础 UI 控件必须使用组件库，禁止自定义实现

### 已安装的 shadcn-ui 组件
查看已安装的组件列表：`frontend/components/ui/` 目录

### 组件使用示例
```tsx
// ✅ 正确：使用 shadcn-ui 组件
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'

// ❌ 错误：自定义基础 UI 组件
// const CustomAlert = () => <div className="alert">...</div>

// ❌ 错误：直接安装其他 UI 库而不考虑 shadcn-ui
// import { Radio } from 'antd'
```

### 查找和安装新组件流程
1. **查看 shadcn-ui**：访问 [ui.shadcn.com](https://ui.shadcn.com) 查找组件
2. **阅读安装说明**：仔细阅读组件页面的 Installation 部分
3. **检查额外依赖**：某些组件可能需要额外的 npm 包或配置
4. **按步骤安装**：严格按照官网说明执行，不只是简单的 add 命令
5. **验证安装**：确保组件和所有依赖都正确安装
6. **如果没有合适组件**：考虑 Radix UI、Headless UI 等无样式组件库
7. **最后选择**：只有在前面都没有时才自定义实现

### 常见复杂组件安装示例
- **Date Picker**：需要额外安装 date-fns 或 day.js
- **Charts**：需要安装 recharts 或其他图表库
- **Form**：需要安装 react-hook-form 和 zod
- **Table**：可能需要 @tanstack/react-table