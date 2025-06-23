"""核心模块测试"""

from datetime import datetime

import pytest

from ..core import FileInfo, FileManager, FileSystemInterface, FileType
from ..exceptions import FileNotFoundError


class MockFileSystem(FileSystemInterface):
    """用于测试的模拟文件系统"""

    def __init__(self):
        self.files = {}
        self.dirs = {"/"}

    def exists(self, path: str) -> bool:
        return path in self.files or path in self.dirs

    def is_file(self, path: str) -> bool:
        return path in self.files

    def is_dir(self, path: str) -> bool:
        return path in self.dirs

    def get_info(self, path: str) -> FileInfo:
        if not self.exists(path):
            raise FileNotFoundError(path)

        name = path.split("/")[-1] or "/"
        now = datetime.now()

        if self.is_file(path):
            size = len(self.files[path])
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
        )

    def list_dir(self, path: str, recursive: bool = False) -> list:
        return []

    def read_text(self, path: str, encoding: str = "utf-8") -> str:
        if path not in self.files:
            raise FileNotFoundError(path)
        return self.files[path]

    def read_bytes(self, path: str) -> bytes:
        if path not in self.files:
            raise FileNotFoundError(path)
        return self.files[path].encode("utf-8")

    def write_text(
        self, path: str, content: str, encoding: str = "utf-8", create_dirs: bool = True
    ) -> None:
        self.files[path] = content

    def write_bytes(self, path: str, content: bytes, create_dirs: bool = True) -> None:
        self.files[path] = content.decode("utf-8")

    def append_text(self, path: str, content: str, encoding: str = "utf-8") -> None:
        if path in self.files:
            self.files[path] += content
        else:
            self.files[path] = content

    def create_dir(
        self, path: str, parents: bool = True, exist_ok: bool = True
    ) -> None:
        self.dirs.add(path)

    def remove_file(self, path: str) -> None:
        if path not in self.files:
            raise FileNotFoundError(path)
        del self.files[path]

    def remove_dir(self, path: str, recursive: bool = False) -> None:
        if path not in self.dirs:
            raise FileNotFoundError(path)
        self.dirs.remove(path)

    def copy_file(self, src: str, dst: str, overwrite: bool = False) -> None:
        if src not in self.files:
            raise FileNotFoundError(src)
        self.files[dst] = self.files[src]

    def copy_dir(self, src: str, dst: str, overwrite: bool = False) -> None:
        pass

    def move(self, src: str, dst: str, overwrite: bool = False) -> None:
        if src in self.files:
            self.files[dst] = self.files[src]
            del self.files[src]

    def rename(self, src: str, dst: str) -> None:
        self.move(src, dst)

    def get_size(self, path: str) -> int:
        if path in self.files:
            return len(self.files[path])
        return 0

    def chmod(self, path: str, mode: int) -> None:
        pass

    def search(self, path: str, pattern: str, recursive: bool = True) -> list:
        return []


@pytest.mark.unit
class TestFileManager:
    """FileManager类测试"""

    def setup_method(self):
        """测试前设置"""
        self.mock_fs = MockFileSystem()
        self.manager = FileManager(self.mock_fs)

    def test_init(self):
        """测试初始化"""
        assert self.manager.filesystem == self.mock_fs

    def test_switch_filesystem(self):
        """测试切换文件系统"""
        new_fs = MockFileSystem()
        self.manager.switch_filesystem(new_fs)
        assert self.manager.filesystem == new_fs

    def test_exists(self):
        """测试exists方法"""
        self.mock_fs.files["/test.txt"] = "content"
        assert self.manager.exists("/test.txt") is True
        assert self.manager.exists("/nonexistent.txt") is False

    def test_is_file(self):
        """测试is_file方法"""
        self.mock_fs.files["/test.txt"] = "content"
        assert self.manager.is_file("/test.txt") is True
        assert self.manager.is_file("/nonexistent.txt") is False

    def test_is_dir(self):
        """测试is_dir方法"""
        self.mock_fs.dirs.add("/test_dir")
        assert self.manager.is_dir("/test_dir") is True
        assert self.manager.is_dir("/nonexistent_dir") is False

    def test_read_text(self):
        """测试read_text方法"""
        test_content = "测试内容"
        self.mock_fs.files["/test.txt"] = test_content

        result = self.manager.read_text("/test.txt")
        assert result == test_content

    def test_read_text_file_not_found(self):
        """测试读取不存在文件"""
        with pytest.raises(FileNotFoundError):
            self.manager.read_text("/nonexistent.txt")

    def test_write_text(self):
        """测试write_text方法"""
        test_content = "新的测试内容"
        self.manager.write_text("/new_file.txt", test_content)

        assert self.mock_fs.files["/new_file.txt"] == test_content

    def test_append_text(self):
        """测试append_text方法"""
        # 先写入初始内容
        initial_content = "初始内容"
        self.manager.write_text("/test.txt", initial_content)

        # 追加内容
        append_content = "\n追加内容"
        self.manager.append_text("/test.txt", append_content)

        result = self.manager.read_text("/test.txt")
        assert result == initial_content + append_content

    def test_create_dir(self):
        """测试创建目录"""
        self.manager.create_dir("/new_dir")
        assert "/new_dir" in self.mock_fs.dirs

    def test_remove_file(self):
        """测试删除文件"""
        self.mock_fs.files["/test.txt"] = "content"
        self.manager.remove_file("/test.txt")
        assert "/test.txt" not in self.mock_fs.files

    def test_remove_file_not_found(self):
        """测试删除不存在的文件"""
        with pytest.raises(FileNotFoundError):
            self.manager.remove_file("/nonexistent.txt")

    def test_copy_file(self):
        """测试复制文件"""
        test_content = "测试内容"
        self.mock_fs.files["/source.txt"] = test_content

        self.manager.copy_file("/source.txt", "/dest.txt")

        assert self.mock_fs.files["/dest.txt"] == test_content
        assert self.mock_fs.files["/source.txt"] == test_content  # 原文件仍存在

    def test_move_file(self):
        """测试移动文件"""
        test_content = "测试内容"
        self.mock_fs.files["/source.txt"] = test_content

        self.manager.move("/source.txt", "/dest.txt")

        assert self.mock_fs.files["/dest.txt"] == test_content
        assert "/source.txt" not in self.mock_fs.files  # 原文件被移动

    def test_get_size(self):
        """测试获取文件大小"""
        test_content = "测试内容"
        self.mock_fs.files["/test.txt"] = test_content

        size = self.manager.get_size("/test.txt")
        assert size == len(test_content)

    def test_ensure_dir_exists(self):
        """测试ensure_dir - 目录已存在"""
        self.mock_fs.dirs.add("/existing_dir")
        self.manager.ensure_dir("/existing_dir")
        # 不应该抛出异常

    def test_ensure_dir_not_exists(self):
        """测试ensure_dir - 目录不存在"""
        self.manager.ensure_dir("/new_dir")
        assert "/new_dir" in self.mock_fs.dirs

    def test_safe_remove_file_success(self):
        """测试安全删除文件 - 成功"""
        self.mock_fs.files["/test.txt"] = "content"
        result = self.manager.safe_remove("/test.txt")
        assert result is True
        assert "/test.txt" not in self.mock_fs.files

    def test_safe_remove_file_not_found(self):
        """测试安全删除文件 - 文件不存在"""
        result = self.manager.safe_remove("/nonexistent.txt")
        assert result is False


@pytest.mark.unit
class TestFileInfo:
    """FileInfo数据类测试"""

    def test_file_info_creation(self):
        """测试FileInfo创建"""
        now = datetime.now()
        file_info = FileInfo(
            path="/test.txt",
            name="test.txt",
            size=100,
            file_type=FileType.FILE,
            created_time=now,
            modified_time=now,
            accessed_time=now,
            permissions=0o644,
        )

        assert file_info.path == "/test.txt"
        assert file_info.name == "test.txt"
        assert file_info.size == 100
        assert file_info.file_type == FileType.FILE
        assert file_info.permissions == 0o644


@pytest.mark.unit
class TestFileType:
    """FileType枚举测试"""

    def test_file_type_values(self):
        """测试FileType枚举值"""
        assert FileType.FILE.value == "file"
        assert FileType.DIRECTORY.value == "directory"
        assert FileType.SYMLINK.value == "symlink"
        assert FileType.UNKNOWN.value == "unknown"
