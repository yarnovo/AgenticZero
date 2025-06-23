# 文件系统模块 (Filesystem)

## 简介

文件系统模块是一个提供统一文件系统操作API的Python库。它通过抽象层设计，支持多种文件系统后端（本地文件系统、云存储等），为应用程序提供一致、可靠的文件操作接口。

## 核心特性

### 🎯 统一API接口
- 提供一致的文件操作API，屏蔽底层文件系统差异
- 支持文件和目录的创建、读取、写入、删除、复制、移动等操作
- 统一的异常处理机制

### 🔧 可扩展架构
- 基于抽象接口设计，易于扩展新的文件系统后端
- 插件化架构，支持自定义文件系统实现
- 内置本地文件系统实现，可作为其他实现的参考

### 🛡️ 安全可靠
- 路径安全验证，防止路径遍历攻击
- 完善的错误处理和异常机制
- 支持基础路径限制，增强安全性

### 📊 丰富功能
- 文件信息获取（大小、时间戳、权限等）
- 目录树遍历和搜索
- 文件匹配和过滤
- 批量操作支持

## 安装使用

### 基本用法

```python
from src.filesystem import FileManager, LocalFileSystem

# 初始化文件管理器
fs = LocalFileSystem("/path/to/workspace")  # 限制在指定目录
manager = FileManager(fs)

# 文件操作
manager.write_text("hello.txt", "Hello, World!")
content = manager.read_text("hello.txt")
print(content)  # 输出: Hello, World!

# 目录操作
manager.create_dir("documents/projects")
files = manager.list_dir("documents", recursive=True)

# 文件搜索
py_files = manager.search(".", "*.py", recursive=True)
```

### 高级用法

```python
# 获取文件信息
info = manager.get_info("hello.txt")
print(f"文件大小: {info.size} bytes")
print(f"修改时间: {info.modified_time}")
print(f"是否可读: {info.is_readable}")

# 批量操作
files_to_create = [
    ("file1.txt", "内容1"),
    ("file2.txt", "内容2"),
    ("dir1/file3.txt", "内容3"),
]

for filename, content in files_to_create:
    manager.write_text(filename, content)

# 目录树结构
tree = manager.get_dir_tree(".")
print(tree)

# 安全删除
success = manager.safe_remove("old_file.txt")
if success:
    print("文件删除成功")
```

## API参考

### FileManager类

文件管理器主类，提供统一的文件操作接口。

#### 构造方法
- `FileManager(filesystem: FileSystemInterface)` - 使用指定的文件系统创建管理器

#### 文件操作方法
- `exists(path: str) -> bool` - 检查文件/目录是否存在
- `is_file(path: str) -> bool` - 检查是否为文件
- `is_dir(path: str) -> bool` - 检查是否为目录
- `get_info(path: str) -> FileInfo` - 获取文件/目录信息
- `read_text(path: str, encoding: str = 'utf-8') -> str` - 读取文本文件
- `read_bytes(path: str) -> bytes` - 读取二进制文件
- `write_text(path: str, content: str, encoding: str = 'utf-8', create_dirs: bool = True) -> None` - 写入文本文件
- `write_bytes(path: str, content: bytes, create_dirs: bool = True) -> None` - 写入二进制文件
- `append_text(path: str, content: str, encoding: str = 'utf-8') -> None` - 追加文本内容

#### 目录操作方法
- `list_dir(path: str, recursive: bool = False) -> List[FileInfo]` - 列出目录内容
- `create_dir(path: str, parents: bool = True, exist_ok: bool = True) -> None` - 创建目录
- `remove_file(path: str) -> None` - 删除文件
- `remove_dir(path: str, recursive: bool = False) -> None` - 删除目录

#### 文件管理方法
- `copy_file(src: str, dst: str, overwrite: bool = False) -> None` - 复制文件
- `copy_dir(src: str, dst: str, overwrite: bool = False) -> None` - 复制目录
- `move(src: str, dst: str, overwrite: bool = False) -> None` - 移动文件/目录
- `rename(src: str, dst: str) -> None` - 重命名文件/目录

#### 辅助方法
- `get_size(path: str) -> int` - 获取文件/目录大小
- `chmod(path: str, mode: int) -> None` - 修改权限
- `search(path: str, pattern: str, recursive: bool = True) -> List[FileInfo]` - 搜索文件
- `ensure_dir(path: str) -> None` - 确保目录存在
- `safe_remove(path: str) -> bool` - 安全删除文件/目录
- `get_dir_tree(path: str, max_depth: int = -1) -> Dict[str, Any]` - 获取目录树结构

### LocalFileSystem类

本地文件系统实现。

#### 构造方法
- `LocalFileSystem(base_path: Optional[str] = None)` - 创建本地文件系统
  - `base_path`: 基础路径，所有操作限制在此路径下。为None时不限制路径

### FileInfo数据类

文件信息数据类，包含文件的详细信息。

#### 属性
- `path: str` - 文件路径
- `name: str` - 文件名
- `size: int` - 文件大小（字节）
- `file_type: FileType` - 文件类型（FILE, DIRECTORY, SYMLINK, UNKNOWN）
- `created_time: datetime` - 创建时间
- `modified_time: datetime` - 修改时间
- `accessed_time: datetime` - 访问时间
- `permissions: int` - 权限
- `is_readable: bool` - 是否可读
- `is_writable: bool` - 是否可写
- `is_executable: bool` - 是否可执行

## 异常处理

模块定义了完善的异常体系：

- `FileManagerError` - 基础异常类
- `FileNotFoundError` - 文件不存在异常
- `PermissionError` - 权限不足异常
- `DirectoryNotEmptyError` - 目录非空异常
- `FileAlreadyExistsError` - 文件已存在异常
- `InvalidPathError` - 无效路径异常

```python
from src.filesystem.exceptions import FileNotFoundError, PermissionError

try:
    content = manager.read_text("nonexistent.txt")
except FileNotFoundError as e:
    print(f"文件不存在: {e.path}")
except PermissionError as e:
    print(f"权限不足: {e.operation} - {e.path}")
```

## 扩展开发

### 自定义文件系统实现

要实现自定义的文件系统后端，需要继承`FileSystemInterface`接口：

```python
from src.filesystem.core import FileSystemInterface

class MyCustomFileSystem(FileSystemInterface):
    def exists(self, path: str) -> bool:
        # 实现检查文件是否存在的逻辑
        pass
    
    def read_text(self, path: str, encoding: str = 'utf-8') -> str:
        # 实现读取文本文件的逻辑
        pass
    
    # 实现其他必需的方法...

# 使用自定义文件系统
custom_fs = MyCustomFileSystem()
manager = FileManager(custom_fs)
```

### 云存储支持示例

```python
class S3FileSystem(FileSystemInterface):
    def __init__(self, bucket_name: str, aws_config: dict):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3', **aws_config)
    
    def exists(self, path: str) -> bool:
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=path)
            return True
        except ClientError:
            return False
    
    # 实现其他方法...
```

## 演示示例

### 运行基础演示

```bash
cd src/filesystem/examples
python basic_demo.py
```

### 运行性能比较

```bash
cd src/filesystem/examples  
python filesystem_comparison.py
```

## 测试

运行测试套件：

```bash
# 运行所有测试
pytest src/filesystem/tests/ -v

# 运行特定测试
pytest src/filesystem/tests/test_core.py -v
pytest src/filesystem/tests/test_local_filesystem.py -v

# 运行单元测试
pytest src/filesystem/tests/ -m unit -v

# 运行集成测试
pytest src/filesystem/tests/ -m integration -v
```

## 最佳实践

### 1. 路径安全
```python
# 使用基础路径限制操作范围
fs = LocalFileSystem("/safe/workspace")
manager = FileManager(fs)

# 避免直接使用用户输入的路径
# 应该进行验证和清理
```

### 2. 异常处理
```python
# 总是处理可能的异常
try:
    content = manager.read_text(user_file)
except FileNotFoundError:
    print("文件不存在")
except PermissionError:
    print("没有权限访问文件")
except Exception as e:
    print(f"未知错误: {e}")
```

### 3. 资源管理
```python
# 对于大文件操作，考虑使用流式处理
# 或者分块读取以避免内存问题

# 及时清理临时文件
if manager.exists("temp_file.txt"):
    manager.safe_remove("temp_file.txt")
```

### 4. 性能优化
```python
# 批量操作比单个操作更高效
files_to_create = [...]
for filename, content in files_to_create:
    manager.write_text(filename, content)

# 使用递归列表获取完整目录结构
all_files = manager.list_dir(".", recursive=True)
```

## 许可证

本模块遵循项目许可证。

## 贡献

欢迎提交Issue和Pull Request来改进这个模块。

## 更新日志

### v1.0.0
- 初始版本发布
- 实现基础文件操作API
- 支持本地文件系统
- 完整的测试覆盖
- 详细的文档和示例