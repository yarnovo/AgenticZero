"""异常类测试"""

import pytest

from ..exceptions import (
    DirectoryNotEmptyError,
    FileAlreadyExistsError,
    FileManagerError,
    FileNotFoundError,
    InvalidPathError,
    PermissionError,
)


@pytest.mark.unit
class TestFileManagerError:
    """FileManagerError基础异常测试"""

    def test_basic_error(self):
        """测试基本异常"""
        message = "测试错误消息"
        error = FileManagerError(message)

        assert error.message == message
        assert error.path is None
        assert str(error) == message

    def test_error_with_path(self):
        """测试带路径的异常"""
        message = "测试错误消息"
        path = "/test/path"
        error = FileManagerError(message, path)

        assert error.message == message
        assert error.path == path
        assert str(error) == f"{message} (路径: {path})"


@pytest.mark.unit
class TestFileNotFoundError:
    """FileNotFoundError测试"""

    def test_file_not_found_error(self):
        """测试文件不存在异常"""
        path = "/nonexistent/file.txt"
        error = FileNotFoundError(path)

        assert error.path == path
        assert "文件或目录不存在" in error.message
        assert path in str(error)


@pytest.mark.unit
class TestPermissionError:
    """PermissionError测试"""

    def test_permission_error(self):
        """测试权限异常"""
        path = "/protected/file.txt"
        operation = "读取文件"
        error = PermissionError(path, operation)

        assert error.path == path
        assert error.operation == operation
        assert "没有权限执行操作" in error.message
        assert operation in error.message
        assert path in str(error)


@pytest.mark.unit
class TestDirectoryNotEmptyError:
    """DirectoryNotEmptyError测试"""

    def test_directory_not_empty_error(self):
        """测试目录非空异常"""
        path = "/some/directory"
        error = DirectoryNotEmptyError(path)

        assert error.path == path
        assert "目录不为空" in error.message
        assert path in str(error)


@pytest.mark.unit
class TestFileAlreadyExistsError:
    """FileAlreadyExistsError测试"""

    def test_file_already_exists_error(self):
        """测试文件已存在异常"""
        path = "/existing/file.txt"
        error = FileAlreadyExistsError(path)

        assert error.path == path
        assert "文件或目录已存在" in error.message
        assert path in str(error)


@pytest.mark.unit
class TestInvalidPathError:
    """InvalidPathError测试"""

    def test_invalid_path_error_basic(self):
        """测试基本无效路径异常"""
        path = "invalid//path"
        error = InvalidPathError(path)

        assert error.path == path
        assert "无效的路径格式" in error.message
        assert path in str(error)

    def test_invalid_path_error_with_reason(self):
        """测试带原因的无效路径异常"""
        path = "invalid//path"
        reason = "包含连续的斜杠"
        error = InvalidPathError(path, reason)

        assert error.path == path
        assert "无效的路径格式" in error.message
        assert reason in error.message
        assert path in str(error)


@pytest.mark.unit
class TestExceptionInheritance:
    """异常继承关系测试"""

    def test_all_exceptions_inherit_from_base(self):
        """测试所有异常都继承自基础异常"""
        exceptions = [
            FileNotFoundError("/path"),
            PermissionError("/path", "operation"),
            DirectoryNotEmptyError("/path"),
            FileAlreadyExistsError("/path"),
            InvalidPathError("/path"),
        ]

        for exception in exceptions:
            assert isinstance(exception, FileManagerError)
            assert isinstance(exception, Exception)

    def test_exception_can_be_caught_as_base(self):
        """测试异常可以作为基础异常捕获"""
        try:
            raise FileNotFoundError("/test/path")
        except FileManagerError as e:
            assert isinstance(e, FileManagerError)
            assert isinstance(e, FileNotFoundError)

        try:
            raise PermissionError("/test/path", "read")
        except FileManagerError as e:
            assert isinstance(e, FileManagerError)
            assert isinstance(e, PermissionError)
