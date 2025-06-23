"""本地文件系统实现"""

import fnmatch
import os
import shutil
from datetime import datetime
from pathlib import Path

from .core import FileInfo, FileSystemInterface, FileType
from .exceptions import (
    DirectoryNotEmptyError,
    FileAlreadyExistsError,
    FileNotFoundError,
    InvalidPathError,
    PermissionError,
)


class LocalFileSystem(FileSystemInterface):
    """本地文件系统实现"""

    def __init__(self, base_path: str | None = None):
        """初始化本地文件系统

        Args:
            base_path: 基础路径，所有操作都在此路径下进行。如果为None，则可以访问整个文件系统
        """
        self._base_path = None
        if base_path:
            self._base_path = Path(base_path).resolve()
            if not self._base_path.exists():
                raise FileNotFoundError(str(self._base_path))
            if not self._base_path.is_dir():
                raise InvalidPathError(str(self._base_path), "基础路径必须是目录")

    def _resolve_path(self, path: str) -> Path:
        """解析路径"""
        p = Path(path)
        if self._base_path:
            if p.is_absolute():
                # 检查是否在基础路径下
                try:
                    p.resolve().relative_to(self._base_path)
                except ValueError:
                    raise InvalidPathError(path, "路径超出基础路径范围")
            else:
                p = self._base_path / p

        return p.resolve()

    def _get_file_type(self, path: Path) -> FileType:
        """获取文件类型"""
        if path.is_symlink():
            return FileType.SYMLINK
        elif path.is_file():
            return FileType.FILE
        elif path.is_dir():
            return FileType.DIRECTORY
        else:
            return FileType.UNKNOWN

    def _path_to_file_info(self, path: Path) -> FileInfo:
        """将Path对象转换为FileInfo"""
        if not path.exists():
            raise FileNotFoundError(str(path))

        stat_info = path.stat()
        file_type = self._get_file_type(path)

        return FileInfo(
            path=str(path),
            name=path.name,
            size=stat_info.st_size if file_type == FileType.FILE else 0,
            file_type=file_type,
            created_time=datetime.fromtimestamp(stat_info.st_ctime),
            modified_time=datetime.fromtimestamp(stat_info.st_mtime),
            accessed_time=datetime.fromtimestamp(stat_info.st_atime),
            permissions=stat_info.st_mode,
            is_readable=os.access(path, os.R_OK),
            is_writable=os.access(path, os.W_OK),
            is_executable=os.access(path, os.X_OK),
        )

    def exists(self, path: str) -> bool:
        """检查文件或目录是否存在"""
        try:
            resolved_path = self._resolve_path(path)
            return resolved_path.exists()
        except (InvalidPathError, OSError):
            return False

    def is_file(self, path: str) -> bool:
        """检查是否为文件"""
        try:
            resolved_path = self._resolve_path(path)
            return resolved_path.is_file()
        except (InvalidPathError, OSError):
            return False

    def is_dir(self, path: str) -> bool:
        """检查是否为目录"""
        try:
            resolved_path = self._resolve_path(path)
            return resolved_path.is_dir()
        except (InvalidPathError, OSError):
            return False

    def get_info(self, path: str) -> FileInfo:
        """获取文件或目录信息"""
        resolved_path = self._resolve_path(path)
        return self._path_to_file_info(resolved_path)

    def list_dir(self, path: str, recursive: bool = False) -> list[FileInfo]:
        """列出目录内容"""
        resolved_path = self._resolve_path(path)

        if not resolved_path.exists():
            raise FileNotFoundError(str(resolved_path))

        if not resolved_path.is_dir():
            raise InvalidPathError(str(resolved_path), "不是目录")

        result = []

        try:
            if recursive:
                for item in resolved_path.rglob("*"):
                    try:
                        result.append(self._path_to_file_info(item))
                    except (OSError, PermissionError):
                        continue
            else:
                for item in resolved_path.iterdir():
                    try:
                        result.append(self._path_to_file_info(item))
                    except (OSError, PermissionError):
                        continue
        except OSError as e:
            raise PermissionError(str(resolved_path), "列出目录") from e

        return sorted(result, key=lambda x: (x.file_type.value, x.name.lower()))

    def read_text(self, path: str, encoding: str = "utf-8") -> str:
        """读取文件文本内容"""
        resolved_path = self._resolve_path(path)

        if not resolved_path.exists():
            raise FileNotFoundError(str(resolved_path))

        if not resolved_path.is_file():
            raise InvalidPathError(str(resolved_path), "不是文件")

        try:
            return resolved_path.read_text(encoding=encoding)
        except OSError as e:
            raise PermissionError(str(resolved_path), "读取文件") from e
        except UnicodeDecodeError as e:
            raise InvalidPathError(str(resolved_path), f"编码错误: {e}")

    def read_bytes(self, path: str) -> bytes:
        """读取文件二进制内容"""
        resolved_path = self._resolve_path(path)

        if not resolved_path.exists():
            raise FileNotFoundError(str(resolved_path))

        if not resolved_path.is_file():
            raise InvalidPathError(str(resolved_path), "不是文件")

        try:
            return resolved_path.read_bytes()
        except OSError as e:
            raise PermissionError(str(resolved_path), "读取文件") from e

    def write_text(
        self, path: str, content: str, encoding: str = "utf-8", create_dirs: bool = True
    ) -> None:
        """写入文本内容到文件"""
        resolved_path = self._resolve_path(path)

        if create_dirs:
            resolved_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            resolved_path.write_text(content, encoding=encoding)
        except OSError as e:
            raise PermissionError(str(resolved_path), "写入文件") from e

    def write_bytes(self, path: str, content: bytes, create_dirs: bool = True) -> None:
        """写入二进制内容到文件"""
        resolved_path = self._resolve_path(path)

        if create_dirs:
            resolved_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            resolved_path.write_bytes(content)
        except OSError as e:
            raise PermissionError(str(resolved_path), "写入文件") from e

    def append_text(self, path: str, content: str, encoding: str = "utf-8") -> None:
        """追加文本内容到文件"""
        resolved_path = self._resolve_path(path)

        try:
            with resolved_path.open("a", encoding=encoding) as f:
                f.write(content)
        except OSError as e:
            raise PermissionError(str(resolved_path), "追加到文件") from e

    def create_dir(
        self, path: str, parents: bool = True, exist_ok: bool = True
    ) -> None:
        """创建目录"""
        resolved_path = self._resolve_path(path)

        if resolved_path.exists() and not exist_ok:
            raise FileAlreadyExistsError(str(resolved_path))

        try:
            resolved_path.mkdir(parents=parents, exist_ok=exist_ok)
        except OSError as e:
            raise PermissionError(str(resolved_path), "创建目录") from e

    def remove_file(self, path: str) -> None:
        """删除文件"""
        resolved_path = self._resolve_path(path)

        if not resolved_path.exists():
            raise FileNotFoundError(str(resolved_path))

        if not resolved_path.is_file():
            raise InvalidPathError(str(resolved_path), "不是文件")

        try:
            resolved_path.unlink()
        except OSError as e:
            raise PermissionError(str(resolved_path), "删除文件") from e

    def remove_dir(self, path: str, recursive: bool = False) -> None:
        """删除目录"""
        resolved_path = self._resolve_path(path)

        if not resolved_path.exists():
            raise FileNotFoundError(str(resolved_path))

        if not resolved_path.is_dir():
            raise InvalidPathError(str(resolved_path), "不是目录")

        try:
            if recursive:
                shutil.rmtree(resolved_path)
            else:
                resolved_path.rmdir()
        except OSError as e:
            if "Directory not empty" in str(e):
                raise DirectoryNotEmptyError(str(resolved_path)) from e
            raise PermissionError(str(resolved_path), "删除目录") from e

    def copy_file(self, src: str, dst: str, overwrite: bool = False) -> None:
        """复制文件"""
        src_path = self._resolve_path(src)
        dst_path = self._resolve_path(dst)

        if not src_path.exists():
            raise FileNotFoundError(str(src_path))

        if not src_path.is_file():
            raise InvalidPathError(str(src_path), "不是文件")

        if dst_path.exists() and not overwrite:
            raise FileAlreadyExistsError(str(dst_path))

        try:
            # 确保目标目录存在
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
        except OSError as e:
            raise PermissionError(str(dst_path), "复制文件") from e

    def copy_dir(self, src: str, dst: str, overwrite: bool = False) -> None:
        """复制目录"""
        src_path = self._resolve_path(src)
        dst_path = self._resolve_path(dst)

        if not src_path.exists():
            raise FileNotFoundError(str(src_path))

        if not src_path.is_dir():
            raise InvalidPathError(str(src_path), "不是目录")

        if dst_path.exists() and not overwrite:
            raise FileAlreadyExistsError(str(dst_path))

        try:
            if dst_path.exists():
                shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path)
        except OSError as e:
            raise PermissionError(str(dst_path), "复制目录") from e

    def move(self, src: str, dst: str, overwrite: bool = False) -> None:
        """移动文件或目录"""
        src_path = self._resolve_path(src)
        dst_path = self._resolve_path(dst)

        if not src_path.exists():
            raise FileNotFoundError(str(src_path))

        if dst_path.exists() and not overwrite:
            raise FileAlreadyExistsError(str(dst_path))

        try:
            # 确保目标目录存在
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            if dst_path.exists() and overwrite:
                if dst_path.is_dir():
                    shutil.rmtree(dst_path)
                else:
                    dst_path.unlink()
            shutil.move(str(src_path), str(dst_path))
        except OSError as e:
            raise PermissionError(str(dst_path), "移动文件") from e

    def rename(self, src: str, dst: str) -> None:
        """重命名文件或目录"""
        src_path = self._resolve_path(src)
        dst_path = self._resolve_path(dst)

        if not src_path.exists():
            raise FileNotFoundError(str(src_path))

        if dst_path.exists():
            raise FileAlreadyExistsError(str(dst_path))

        try:
            src_path.rename(dst_path)
        except OSError as e:
            raise PermissionError(str(dst_path), "重命名") from e

    def get_size(self, path: str) -> int:
        """获取文件或目录大小"""
        resolved_path = self._resolve_path(path)

        if not resolved_path.exists():
            raise FileNotFoundError(str(resolved_path))

        if resolved_path.is_file():
            return resolved_path.stat().st_size
        elif resolved_path.is_dir():
            total_size = 0
            try:
                for item in resolved_path.rglob("*"):
                    if item.is_file():
                        try:
                            total_size += item.stat().st_size
                        except (OSError, PermissionError):
                            continue
            except (OSError, PermissionError):
                pass
            return total_size
        else:
            return 0

    def chmod(self, path: str, mode: int) -> None:
        """修改文件权限"""
        resolved_path = self._resolve_path(path)

        if not resolved_path.exists():
            raise FileNotFoundError(str(resolved_path))

        try:
            resolved_path.chmod(mode)
        except OSError as e:
            raise PermissionError(str(resolved_path), "修改权限") from e

    def search(self, path: str, pattern: str, recursive: bool = True) -> list[FileInfo]:
        """搜索文件"""
        resolved_path = self._resolve_path(path)

        if not resolved_path.exists():
            raise FileNotFoundError(str(resolved_path))

        if not resolved_path.is_dir():
            raise InvalidPathError(str(resolved_path), "不是目录")

        result = []

        try:
            if recursive:
                for item in resolved_path.rglob("*"):
                    if fnmatch.fnmatch(item.name, pattern):
                        try:
                            result.append(self._path_to_file_info(item))
                        except (OSError, PermissionError):
                            continue
            else:
                for item in resolved_path.iterdir():
                    if fnmatch.fnmatch(item.name, pattern):
                        try:
                            result.append(self._path_to_file_info(item))
                        except (OSError, PermissionError):
                            continue
        except OSError as e:
            raise PermissionError(str(resolved_path), "搜索文件") from e

        return sorted(result, key=lambda x: (x.file_type.value, x.name.lower()))
