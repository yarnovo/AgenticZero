# MCP 模块开发指南

## 临时目录的使用

### 什么是临时目录？

在测试和开发中，我们使用 Python 的 `tempfile.TemporaryDirectory()` 来创建临时目录。这是 Python 标准库提供的功能，它会：

1. **自动创建**：在系统的临时文件目录中创建一个唯一的临时目录
   - Linux/Mac: 通常在 `/tmp/` 目录下
   - Windows: 通常在 `C:\Users\<用户名>\AppData\Local\Temp\` 目录下

2. **自动清理**：当 `with` 语句块结束时，临时目录及其所有内容会被自动删除

### 为什么使用临时目录？

1. **隔离性**：每个测试都在独立的目录中运行，避免相互干扰
2. **清洁性**：测试结束后自动清理，不会在项目目录中留下垃圾文件
3. **安全性**：避免意外覆盖或修改项目中的重要文件
4. **并发性**：多个测试可以同时运行而不会冲突

### 使用示例

```python
import tempfile

# 在测试中使用临时目录
def test_file_operations():
    with tempfile.TemporaryDirectory() as tmpdir:
        # tmpdir 是一个字符串，包含临时目录的路径
        # 例如: /tmp/tmpx1y2z3a4
        
        # 在临时目录中创建文件
        file_path = os.path.join(tmpdir, "test.txt")
        with open(file_path, "w") as f:
            f.write("test content")
        
        # 测试结束后，tmpdir 及其所有内容会被自动删除
```

### MCP 模块中的应用

1. **PythonFileManager**：
   ```python
   # 在测试中，总是传入临时目录作为 base_dir
   file_manager = PythonFileManager(base_dir=tmpdir)
   ```

2. **GraphManager**：
   ```python
   # GraphManager 也使用临时目录存储图文件
   graph_manager = GraphManager(base_path=tmpdir)
   ```

3. **服务创建**：
   ```python
   # 创建 Python 服务时，指定临时目录
   await service_manager.handle_call_tool(
       "service_create",
       {
           "service_type": "python",
           "service_id": "py_service",
           "config": {"base_dir": tmpdir}  # 重要：指定临时目录
       }
   )
   ```

### 注意事项

1. **始终在测试中使用临时目录**：避免在项目目录中创建测试文件
2. **传递配置参数**：创建服务时，确保传递正确的目录配置
3. **不要硬编码路径**：使用相对路径或配置的路径，而不是硬编码的绝对路径

### 调试技巧

如果需要查看临时目录的内容进行调试：

```python
import tempfile
import time

with tempfile.TemporaryDirectory() as tmpdir:
    print(f"临时目录位置: {tmpdir}")
    
    # 进行文件操作...
    
    # 暂停以便查看目录内容
    input("按 Enter 键继续（这将删除临时目录）...")
```

这样可以在临时目录被删除前查看其内容，有助于调试文件相关的问题。