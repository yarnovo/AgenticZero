"""文件系统模块核心接口和基础类"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class FileType(Enum):
    """文件类型枚举"""

    FILE = "file"
    DIRECTORY = "directory"
    SYMLINK = "symlink"
    UNKNOWN = "unknown"


@dataclass
class FileInfo:
    """文件信息数据类"""

    path: str
    name: str
    size: int
    file_type: FileType
    created_time: datetime
    modified_time: datetime
    accessed_time: datetime
    permissions: int
    owner: str | None = None
    group: str | None = None
    is_readable: bool = True
    is_writable: bool = True
    is_executable: bool = False


class FileSystemInterface(ABC):
    """文件系统抽象接口"""

    @abstractmethod
    def exists(self, path: str) -> bool:
        """检查文件或目录是否存在"""
        pass

    @abstractmethod
    def is_file(self, path: str) -> bool:
        """检查是否为文件"""
        pass

    @abstractmethod
    def is_dir(self, path: str) -> bool:
        """检查是否为目录"""
        pass

    @abstractmethod
    def get_info(self, path: str) -> FileInfo:
        """获取文件或目录信息"""
        pass

    @abstractmethod
    def list_dir(self, path: str, recursive: bool = False) -> list[FileInfo]:
        """列出目录内容"""
        pass

    @abstractmethod
    def read_text(self, path: str, encoding: str = "utf-8") -> str:
        """读取文件文本内容"""
        pass

    @abstractmethod
    def read_bytes(self, path: str) -> bytes:
        """读取文件二进制内容"""
        pass

    @abstractmethod
    def write_text(
        self, path: str, content: str, encoding: str = "utf-8", create_dirs: bool = True
    ) -> None:
        """写入文本内容到文件"""
        pass

    @abstractmethod
    def write_bytes(self, path: str, content: bytes, create_dirs: bool = True) -> None:
        """写入二进制内容到文件"""
        pass

    @abstractmethod
    def append_text(self, path: str, content: str, encoding: str = "utf-8") -> None:
        """追加文本内容到文件"""
        pass

    @abstractmethod
    def create_dir(
        self, path: str, parents: bool = True, exist_ok: bool = True
    ) -> None:
        """创建目录"""
        pass

    @abstractmethod
    def remove_file(self, path: str) -> None:
        """删除文件"""
        pass

    @abstractmethod
    def remove_dir(self, path: str, recursive: bool = False) -> None:
        """删除目录"""
        pass

    @abstractmethod
    def copy_file(self, src: str, dst: str, overwrite: bool = False) -> None:
        """复制文件"""
        pass

    @abstractmethod
    def copy_dir(self, src: str, dst: str, overwrite: bool = False) -> None:
        """复制目录"""
        pass

    @abstractmethod
    def move(self, src: str, dst: str, overwrite: bool = False) -> None:
        """移动文件或目录"""
        pass

    @abstractmethod
    def rename(self, src: str, dst: str) -> None:
        """重命名文件或目录"""
        pass

    @abstractmethod
    def get_size(self, path: str) -> int:
        """获取文件或目录大小"""
        pass

    @abstractmethod
    def chmod(self, path: str, mode: int) -> None:
        """修改文件权限"""
        pass

    @abstractmethod
    def search(self, path: str, pattern: str, recursive: bool = True) -> list[FileInfo]:
        """搜索文件"""
        pass


class FileManager:
    """文件管理器主类"""

    def __init__(self, filesystem: FileSystemInterface):
        """初始化文件管理器

        Args:
            filesystem: 文件系统实现实例
        """
        self._filesystem = filesystem

    @property
    def filesystem(self) -> FileSystemInterface:
        """获取文件系统实例"""
        return self._filesystem

    def switch_filesystem(self, filesystem: FileSystemInterface) -> None:
        """切换文件系统实现"""
        self._filesystem = filesystem

    # 委托方法到文件系统实现
    def exists(self, path: str) -> bool:
        """检查文件或目录是否存在"""
        return self._filesystem.exists(path)

    def is_file(self, path: str) -> bool:
        """检查是否为文件"""
        return self._filesystem.is_file(path)

    def is_dir(self, path: str) -> bool:
        """检查是否为目录"""
        return self._filesystem.is_dir(path)

    def get_info(self, path: str) -> FileInfo:
        """获取文件或目录信息"""
        return self._filesystem.get_info(path)

    def list_dir(self, path: str, recursive: bool = False) -> list[FileInfo]:
        """列出目录内容"""
        return self._filesystem.list_dir(path, recursive)

    def read_text(self, path: str, encoding: str = "utf-8") -> str:
        """读取文件文本内容"""
        return self._filesystem.read_text(path, encoding)

    def read_bytes(self, path: str) -> bytes:
        """读取文件二进制内容"""
        return self._filesystem.read_bytes(path)

    def write_text(
        self, path: str, content: str, encoding: str = "utf-8", create_dirs: bool = True
    ) -> None:
        """写入文本内容到文件"""
        self._filesystem.write_text(path, content, encoding, create_dirs)

    def write_bytes(self, path: str, content: bytes, create_dirs: bool = True) -> None:
        """写入二进制内容到文件"""
        self._filesystem.write_bytes(path, content, create_dirs)

    def append_text(self, path: str, content: str, encoding: str = "utf-8") -> None:
        """追加文本内容到文件"""
        self._filesystem.append_text(path, content, encoding)

    def create_dir(
        self, path: str, parents: bool = True, exist_ok: bool = True
    ) -> None:
        """创建目录"""
        self._filesystem.create_dir(path, parents, exist_ok)

    def remove_file(self, path: str) -> None:
        """删除文件"""
        self._filesystem.remove_file(path)

    def remove_dir(self, path: str, recursive: bool = False) -> None:
        """删除目录"""
        self._filesystem.remove_dir(path, recursive)

    def copy_file(self, src: str, dst: str, overwrite: bool = False) -> None:
        """复制文件"""
        self._filesystem.copy_file(src, dst, overwrite)

    def copy_dir(self, src: str, dst: str, overwrite: bool = False) -> None:
        """复制目录"""
        self._filesystem.copy_dir(src, dst, overwrite)

    def move(self, src: str, dst: str, overwrite: bool = False) -> None:
        """移动文件或目录"""
        self._filesystem.move(src, dst, overwrite)

    def rename(self, src: str, dst: str) -> None:
        """重命名文件或目录"""
        self._filesystem.rename(src, dst)

    def get_size(self, path: str) -> int:
        """获取文件或目录大小"""
        return self._filesystem.get_size(path)

    def chmod(self, path: str, mode: int) -> None:
        """修改文件权限"""
        self._filesystem.chmod(path, mode)

    def search(self, path: str, pattern: str, recursive: bool = True) -> list[FileInfo]:
        """搜索文件"""
        return self._filesystem.search(path, pattern, recursive)

    # 便捷方法
    def ensure_dir(self, path: str) -> None:
        """确保目录存在，不存在则创建"""
        if not self.exists(path):
            self.create_dir(path)

    def safe_remove(self, path: str) -> bool:
        """安全删除文件或目录，返回是否成功"""
        try:
            if not self.exists(path):
                return False

            if self.is_file(path):
                self.remove_file(path)
            elif self.is_dir(path):
                self.remove_dir(path, recursive=True)
            return True
        except Exception:
            return False

    def get_dir_tree(self, path: str, max_depth: int = -1) -> dict[str, Any]:
        """获取目录树结构"""
        if not self.is_dir(path):
            raise ValueError(f"路径不是目录: {path}")

        def build_tree(current_path: str, current_depth: int) -> dict[str, Any]:
            if max_depth >= 0 and current_depth > max_depth:
                return {}

            tree = {"type": "directory", "children": {}}
            try:
                items = self.list_dir(current_path)
                for item in items:
                    name = item.name
                    item_path = item.path

                    if item.file_type == FileType.DIRECTORY:
                        tree["children"][name] = build_tree(
                            item_path, current_depth + 1
                        )
                    else:
                        tree["children"][name] = {
                            "type": item.file_type.value,
                            "size": item.size,
                            "modified_time": item.modified_time.isoformat(),
                        }
            except Exception:
                pass

            return tree

        return build_tree(path, 0)
