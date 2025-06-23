"""文件系统模块 - 文件系统抽象层

提供统一的API操作文件系统，支持本地文件系统、云存储等多种后端。
"""

from .core import FileManager, FileSystemInterface
from .exceptions import FileManagerError, FileNotFoundError, PermissionError
from .local_filesystem import LocalFileSystem

__all__ = [
    "FileManager",
    "FileSystemInterface",
    "LocalFileSystem",
    "FileManagerError",
    "FileNotFoundError",
    "PermissionError",
]

__version__ = "1.0.0"
