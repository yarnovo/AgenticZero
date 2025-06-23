"""不同文件系统实现的比较演示"""

import tempfile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from ..core import FileInfo, FileManager, FileSystemInterface, FileType


class MemoryFileSystem(FileSystemInterface):
    """内存文件系统实现示例（用于演示）"""

    def __init__(self):
        # 简化的内存存储结构
        self._files = {}  # path -> content
        self._dirs = {"/"}  # 目录集合
        self._metadata = {}  # path -> metadata

    def _normalize_path(self, path: str) -> str:
        """标准化路径"""
        if not path.startswith("/"):
            path = "/" + path
        return path

    def exists(self, path: str) -> bool:
        path = self._normalize_path(path)
        return path in self._files or path in self._dirs

    def is_file(self, path: str) -> bool:
        path = self._normalize_path(path)
        return path in self._files

    def is_dir(self, path: str) -> bool:
        path = self._normalize_path(path)
        return path in self._dirs

    def get_info(self, path: str) -> FileInfo:
        from datetime import datetime

        path = self._normalize_path(path)

        if not self.exists(path):
            raise FileNotFoundError(f"路径不存在: {path}")

        name = path.split("/")[-1] or "/"
        now = datetime.now()

        if self.is_file(path):
            content = self._files[path]
            size = (
                len(content.encode("utf-8"))
                if isinstance(content, str)
                else len(content)
            )
            file_type = FileType.FILE
        else:
            size = 0
            file_type = FileType.DIRECTORY

        return FileInfo(
            path=path,
            name=name,
            size=size,
            file_type=file_type,
            created_time=now,
            modified_time=now,
            accessed_time=now,
            permissions=0o755,
            is_readable=True,
            is_writable=True,
            is_executable=False,
        )

    def list_dir(self, path: str, recursive: bool = False) -> list[FileInfo]:
        path = self._normalize_path(path)

        if not self.is_dir(path):
            raise ValueError(f"不是目录: {path}")

        result = []
        prefix = path if path.endswith("/") else path + "/"

        # 查找直接子项
        children = set()

        # 检查文件
        for file_path in self._files:
            if file_path.startswith(prefix):
                relative = file_path[len(prefix) :]
                if "/" not in relative:  # 直接子文件
                    children.add(file_path)
                elif recursive:
                    children.add(file_path)

        # 检查目录
        for dir_path in self._dirs:
            if dir_path.startswith(prefix) and dir_path != path:
                relative = dir_path[len(prefix) :]
                if "/" not in relative.rstrip("/"):  # 直接子目录
                    children.add(dir_path)
                elif recursive:
                    children.add(dir_path)

        for child_path in children:
            try:
                result.append(self.get_info(child_path))
            except Exception:
                continue

        return sorted(result, key=lambda x: (x.file_type.value, x.name))

    def read_text(self, path: str, encoding: str = "utf-8") -> str:
        path = self._normalize_path(path)

        if not self.is_file(path):
            raise ValueError(f"不是文件: {path}")

        content = self._files[path]
        if isinstance(content, bytes):
            return content.decode(encoding)
        return content

    def read_bytes(self, path: str) -> bytes:
        path = self._normalize_path(path)

        if not self.is_file(path):
            raise ValueError(f"不是文件: {path}")

        content = self._files[path]
        if isinstance(content, str):
            return content.encode("utf-8")
        return content

    def write_text(
        self, path: str, content: str, encoding: str = "utf-8", create_dirs: bool = True
    ) -> None:
        path = self._normalize_path(path)

        if create_dirs:
            # 创建必要的父目录
            parts = path.split("/")[:-1]
            current = ""
            for part in parts:
                if part:  # 跳过空字符串
                    current = current + "/" + part
                    if current not in self._dirs:
                        self._dirs.add(current)

        self._files[path] = content

    def write_bytes(self, path: str, content: bytes, create_dirs: bool = True) -> None:
        path = self._normalize_path(path)

        if create_dirs:
            # 创建必要的父目录
            parts = path.split("/")[:-1]
            current = ""
            for part in parts:
                if part:
                    current = current + "/" + part
                    if current not in self._dirs:
                        self._dirs.add(current)

        self._files[path] = content

    def append_text(self, path: str, content: str, encoding: str = "utf-8") -> None:
        path = self._normalize_path(path)

        if path in self._files:
            existing = self._files[path]
            if isinstance(existing, bytes):
                existing = existing.decode(encoding)
            self._files[path] = existing + content
        else:
            self._files[path] = content

    def create_dir(
        self, path: str, parents: bool = True, exist_ok: bool = True
    ) -> None:
        path = self._normalize_path(path)

        if path in self._dirs and not exist_ok:
            raise FileExistsError(f"目录已存在: {path}")

        if parents:
            # 创建父目录
            parts = path.split("/")
            current = ""
            for part in parts:
                if part:
                    current = current + "/" + part
                    self._dirs.add(current)
        else:
            self._dirs.add(path)

    def remove_file(self, path: str) -> None:
        path = self._normalize_path(path)

        if path not in self._files:
            raise FileNotFoundError(f"文件不存在: {path}")

        del self._files[path]

    def remove_dir(self, path: str, recursive: bool = False) -> None:
        path = self._normalize_path(path)

        if path not in self._dirs:
            raise FileNotFoundError(f"目录不存在: {path}")

        # 检查是否有子项
        prefix = path if path.endswith("/") else path + "/"
        has_children = False

        for file_path in self._files:
            if file_path.startswith(prefix):
                if recursive:
                    del self._files[file_path]
                else:
                    has_children = True
                    break

        for dir_path in list(self._dirs):
            if dir_path.startswith(prefix) and dir_path != path:
                if recursive:
                    self._dirs.remove(dir_path)
                else:
                    has_children = True
                    break

        if has_children and not recursive:
            raise OSError("目录不为空")

        self._dirs.remove(path)

    def copy_file(self, src: str, dst: str, overwrite: bool = False) -> None:
        src = self._normalize_path(src)
        dst = self._normalize_path(dst)

        if src not in self._files:
            raise FileNotFoundError(f"源文件不存在: {src}")

        if dst in self._files and not overwrite:
            raise FileExistsError(f"目标文件已存在: {dst}")

        self._files[dst] = self._files[src]

    def copy_dir(self, src: str, dst: str, overwrite: bool = False) -> None:
        # 简化实现
        raise NotImplementedError("内存文件系统暂未实现目录复制")

    def move(self, src: str, dst: str, overwrite: bool = False) -> None:
        src = self._normalize_path(src)
        dst = self._normalize_path(dst)

        if src in self._files:
            self.copy_file(src, dst, overwrite)
            self.remove_file(src)
        elif src in self._dirs:
            # 简化的目录移动
            if dst in self._dirs and not overwrite:
                raise FileExistsError(f"目标目录已存在: {dst}")
            self._dirs.add(dst)
            self._dirs.remove(src)

    def rename(self, src: str, dst: str) -> None:
        self.move(src, dst, overwrite=False)

    def get_size(self, path: str) -> int:
        path = self._normalize_path(path)

        if path in self._files:
            content = self._files[path]
            if isinstance(content, str):
                return len(content.encode("utf-8"))
            return len(content)
        elif path in self._dirs:
            total = 0
            prefix = path if path.endswith("/") else path + "/"
            for file_path, content in self._files.items():
                if file_path.startswith(prefix):
                    if isinstance(content, str):
                        total += len(content.encode("utf-8"))
                    else:
                        total += len(content)
            return total
        else:
            raise FileNotFoundError(f"路径不存在: {path}")

    def chmod(self, path: str, mode: int) -> None:
        # 内存文件系统不支持权限修改
        pass

    def search(self, path: str, pattern: str, recursive: bool = True) -> list[FileInfo]:
        import fnmatch

        path = self._normalize_path(path)
        result = []

        items = self.list_dir(path, recursive)
        for item in items:
            if fnmatch.fnmatch(item.name, pattern):
                result.append(item)

        return result


def filesystem_comparison_demo():
    """文件系统实现比较演示"""
    print("=== 文件系统实现比较演示 ===\n")

    # 测试数据
    test_files = [
        ("test1.txt", "这是测试文件1的内容"),
        ("dir1/test2.txt", "这是测试文件2的内容"),
        ("dir1/subdir/test3.txt", "这是测试文件3的内容"),
    ]

    print("1. 本地文件系统测试")
    with tempfile.TemporaryDirectory() as temp_dir:
        local_fs = LocalFileSystem(temp_dir)
        test_filesystem(local_fs, "本地文件系统", test_files)

    print("\n2. 内存文件系统测试")
    memory_fs = MemoryFileSystem()
    test_filesystem(memory_fs, "内存文件系统", test_files)


def test_filesystem(fs: FileSystemInterface, name: str, test_files: list[tuple]):
    """测试文件系统实现"""
    print(f"\n--- {name} ---")

    manager = FileManager(fs)

    try:
        # 创建测试文件
        print("  创建测试文件...")
        for filename, content in test_files:
            manager.write_text(filename, content)
        print("  ✓ 文件创建完成")

        # 列出文件
        print("  列出文件:")
        files = manager.list_dir(".", recursive=True)
        for file_info in files:
            if file_info.file_type == FileType.FILE:
                print(f"    - {file_info.path} ({file_info.size} bytes)")

        # 读取文件
        print("  读取文件内容:")
        for filename, expected_content in test_files:
            try:
                content = manager.read_text(filename)
                status = "✓" if content == expected_content else "✗"
                print(f"    {status} {filename}")
            except Exception as e:
                print(f"    ✗ {filename}: {e}")

        # 搜索文件
        print("  搜索.txt文件:")
        txt_files = manager.search(".", "*.txt")
        for file_info in txt_files:
            print(f"    - {file_info.name}")

        # 获取总大小
        total_size = manager.get_size(".")
        print(f"  总大小: {total_size} bytes")

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")


def performance_comparison():
    """性能比较演示"""
    print("\n=== 性能比较演示 ===\n")

    import time

    # 创建大量文件进行性能测试
    file_count = 100
    test_content = "这是用于性能测试的内容 " * 10

    print(f"创建 {file_count} 个文件的性能对比:\n")

    # 本地文件系统
    print("1. 本地文件系统")
    with tempfile.TemporaryDirectory() as temp_dir:
        local_fs = LocalFileSystem(temp_dir)
        local_manager = FileManager(local_fs)

        start_time = time.time()
        for i in range(file_count):
            local_manager.write_text(f"file_{i:03d}.txt", test_content)
        local_time = time.time() - start_time

        print(f"   创建时间: {local_time:.4f} 秒")

        # 读取测试
        start_time = time.time()
        for i in range(file_count):
            content = local_manager.read_text(f"file_{i:03d}.txt")
        read_time = time.time() - start_time
        print(f"   读取时间: {read_time:.4f} 秒")

    # 内存文件系统
    print("\n2. 内存文件系统")
    memory_fs = MemoryFileSystem()
    memory_manager = FileManager(memory_fs)

    start_time = time.time()
    for i in range(file_count):
        memory_manager.write_text(f"file_{i:03d}.txt", test_content)
    memory_time = time.time() - start_time

    print(f"   创建时间: {memory_time:.4f} 秒")

    # 读取测试
    start_time = time.time()
    for i in range(file_count):
        _ = memory_manager.read_text(f"file_{i:03d}.txt")
    memory_read_time = time.time() - start_time
    print(f"   读取时间: {memory_read_time:.4f} 秒")

    # 性能比较
    print("\n性能比较:")
    print(f"   内存文件系统创建文件比本地文件系统快 {local_time / memory_time:.1f} 倍")
    print(
        f"   内存文件系统读取文件比本地文件系统快 {read_time / memory_read_time:.1f} 倍"
    )


if __name__ == "__main__":
    from ..local_filesystem import LocalFileSystem

    filesystem_comparison_demo()
    performance_comparison()
