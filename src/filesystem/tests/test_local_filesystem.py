"""本地文件系统测试"""

import os
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from ..core import FileType
from ..exceptions import (
    FileNotFoundError,
    InvalidPathError,
)
from ..local_filesystem import LocalFileSystem


@pytest.mark.integration
class TestLocalFileSystem:
    """本地文件系统集成测试"""

    def setup_method(self):
        """每个测试前设置临时目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.fs = LocalFileSystem(self.temp_dir)

    def teardown_method(self):
        """每个测试后清理临时目录"""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_init_with_base_path(self):
        """测试使用基础路径初始化"""
        fs = LocalFileSystem(self.temp_dir)
        assert fs._base_path == Path(self.temp_dir).resolve()

    def test_init_without_base_path(self):
        """测试不使用基础路径初始化"""
        fs = LocalFileSystem()
        assert fs._base_path is None

    def test_init_with_nonexistent_base_path(self):
        """测试使用不存在的基础路径初始化"""
        nonexistent_path = "/nonexistent/path/12345"
        with pytest.raises(FileNotFoundError):
            LocalFileSystem(nonexistent_path)

    def test_exists_file(self):
        """测试检查文件是否存在"""
        test_file = "test.txt"
        file_path = os.path.join(self.temp_dir, test_file)

        # 文件不存在时
        assert self.fs.exists(test_file) is False

        # 创建文件后
        with open(file_path, "w") as f:
            f.write("test content")
        assert self.fs.exists(test_file) is True

    def test_exists_directory(self):
        """测试检查目录是否存在"""
        test_dir = "test_dir"
        dir_path = os.path.join(self.temp_dir, test_dir)

        # 目录不存在时
        assert self.fs.exists(test_dir) is False

        # 创建目录后
        os.mkdir(dir_path)
        assert self.fs.exists(test_dir) is True

    def test_is_file(self):
        """测试检查是否为文件"""
        test_file = "test.txt"
        test_dir = "test_dir"

        file_path = os.path.join(self.temp_dir, test_file)
        dir_path = os.path.join(self.temp_dir, test_dir)

        # 创建文件和目录
        with open(file_path, "w") as f:
            f.write("test")
        os.mkdir(dir_path)

        assert self.fs.is_file(test_file) is True
        assert self.fs.is_file(test_dir) is False
        assert self.fs.is_file("nonexistent") is False

    def test_is_dir(self):
        """测试检查是否为目录"""
        test_file = "test.txt"
        test_dir = "test_dir"

        file_path = os.path.join(self.temp_dir, test_file)
        dir_path = os.path.join(self.temp_dir, test_dir)

        # 创建文件和目录
        with open(file_path, "w") as f:
            f.write("test")
        os.mkdir(dir_path)

        assert self.fs.is_dir(test_dir) is True
        assert self.fs.is_dir(test_file) is False
        assert self.fs.is_dir("nonexistent") is False

    def test_get_info_file(self):
        """测试获取文件信息"""
        test_file = "test.txt"
        test_content = "测试内容"
        file_path = os.path.join(self.temp_dir, test_file)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(test_content)

        info = self.fs.get_info(test_file)

        assert info.name == test_file
        assert info.file_type == FileType.FILE
        assert info.size == len(test_content.encode("utf-8"))
        assert isinstance(info.created_time, datetime)
        assert isinstance(info.modified_time, datetime)
        assert isinstance(info.accessed_time, datetime)

    def test_get_info_directory(self):
        """测试获取目录信息"""
        test_dir = "test_dir"
        dir_path = os.path.join(self.temp_dir, test_dir)
        os.mkdir(dir_path)

        info = self.fs.get_info(test_dir)

        assert info.name == test_dir
        assert info.file_type == FileType.DIRECTORY
        assert info.size == 0

    def test_get_info_nonexistent(self):
        """测试获取不存在文件的信息"""
        with pytest.raises(FileNotFoundError):
            self.fs.get_info("nonexistent.txt")

    def test_list_dir_empty(self):
        """测试列出空目录"""
        items = self.fs.list_dir(".")
        assert items == []

    def test_list_dir_with_files(self):
        """测试列出包含文件的目录"""
        # 创建测试文件和目录
        test_files = ["file1.txt", "file2.txt"]
        test_dirs = ["dir1", "dir2"]

        for filename in test_files:
            with open(os.path.join(self.temp_dir, filename), "w") as f:
                f.write("test")

        for dirname in test_dirs:
            os.mkdir(os.path.join(self.temp_dir, dirname))

        items = self.fs.list_dir(".")
        names = [item.name for item in items]

        for filename in test_files:
            assert filename in names
        for dirname in test_dirs:
            assert dirname in names

    def test_list_dir_recursive(self):
        """测试递归列出目录"""
        # 创建嵌套结构
        subdir = os.path.join(self.temp_dir, "subdir")
        os.mkdir(subdir)

        with open(os.path.join(self.temp_dir, "root.txt"), "w") as f:
            f.write("root file")

        with open(os.path.join(subdir, "sub.txt"), "w") as f:
            f.write("sub file")

        # 非递归
        items = self.fs.list_dir(".", recursive=False)
        names = [item.name for item in items]
        assert "root.txt" in names
        assert "subdir" in names
        assert "sub.txt" not in names

        # 递归
        items = self.fs.list_dir(".", recursive=True)
        names = [item.name for item in items]
        assert "root.txt" in names
        assert "subdir" in names
        assert "sub.txt" in names

    def test_read_write_text(self):
        """测试文本文件读写"""
        test_file = "test.txt"
        test_content = "这是测试内容\n包含中文字符"

        # 写入
        self.fs.write_text(test_file, test_content)

        # 读取
        result = self.fs.read_text(test_file)
        assert result == test_content

        # 检查文件是否真的存在
        assert self.fs.exists(test_file)
        assert self.fs.is_file(test_file)

    def test_read_write_bytes(self):
        """测试二进制文件读写"""
        test_file = "test.bin"
        test_content = b"Binary content \x00\x01\x02"

        # 写入
        self.fs.write_bytes(test_file, test_content)

        # 读取
        result = self.fs.read_bytes(test_file)
        assert result == test_content

    def test_write_with_create_dirs(self):
        """测试写入时创建目录"""
        nested_file = "nested/deep/file.txt"
        test_content = "nested content"

        # 默认创建目录
        self.fs.write_text(nested_file, test_content, create_dirs=True)

        assert self.fs.exists(nested_file)
        assert self.fs.read_text(nested_file) == test_content

    def test_append_text(self):
        """测试追加文本"""
        test_file = "test.txt"
        initial_content = "初始内容"
        append_content = "\n追加内容"

        # 先写入初始内容
        self.fs.write_text(test_file, initial_content)

        # 追加内容
        self.fs.append_text(test_file, append_content)

        # 验证结果
        result = self.fs.read_text(test_file)
        assert result == initial_content + append_content

    def test_create_dir(self):
        """测试创建目录"""
        test_dir = "new_dir"

        self.fs.create_dir(test_dir)

        assert self.fs.exists(test_dir)
        assert self.fs.is_dir(test_dir)

    def test_create_nested_dir(self):
        """测试创建嵌套目录"""
        nested_dir = "level1/level2/level3"

        self.fs.create_dir(nested_dir, parents=True)

        assert self.fs.exists(nested_dir)
        assert self.fs.is_dir(nested_dir)
        assert self.fs.exists("level1")
        assert self.fs.exists("level1/level2")

    def test_remove_file(self):
        """测试删除文件"""
        test_file = "test.txt"

        # 创建文件
        self.fs.write_text(test_file, "test content")
        assert self.fs.exists(test_file)

        # 删除文件
        self.fs.remove_file(test_file)
        assert not self.fs.exists(test_file)

    def test_remove_nonexistent_file(self):
        """测试删除不存在的文件"""
        with pytest.raises(FileNotFoundError):
            self.fs.remove_file("nonexistent.txt")

    def test_remove_dir_empty(self):
        """测试删除空目录"""
        test_dir = "empty_dir"

        self.fs.create_dir(test_dir)
        assert self.fs.exists(test_dir)

        self.fs.remove_dir(test_dir)
        assert not self.fs.exists(test_dir)

    def test_remove_dir_recursive(self):
        """测试递归删除目录"""
        # 创建包含文件的目录
        test_dir = "test_dir"
        self.fs.create_dir(test_dir)
        self.fs.write_text(f"{test_dir}/file.txt", "content")
        self.fs.create_dir(f"{test_dir}/subdir")

        # 递归删除
        self.fs.remove_dir(test_dir, recursive=True)
        assert not self.fs.exists(test_dir)

    def test_copy_file(self):
        """测试复制文件"""
        src_file = "source.txt"
        dst_file = "dest.txt"
        test_content = "测试内容"

        # 创建源文件
        self.fs.write_text(src_file, test_content)

        # 复制文件
        self.fs.copy_file(src_file, dst_file)

        # 验证
        assert self.fs.exists(dst_file)
        assert self.fs.read_text(dst_file) == test_content
        assert self.fs.exists(src_file)  # 源文件仍然存在

    def test_move_file(self):
        """测试移动文件"""
        src_file = "source.txt"
        dst_file = "dest.txt"
        test_content = "测试内容"

        # 创建源文件
        self.fs.write_text(src_file, test_content)

        # 移动文件
        self.fs.move(src_file, dst_file)

        # 验证
        assert self.fs.exists(dst_file)
        assert self.fs.read_text(dst_file) == test_content
        assert not self.fs.exists(src_file)  # 源文件被移动

    def test_rename_file(self):
        """测试重命名文件"""
        old_name = "old_name.txt"
        new_name = "new_name.txt"
        test_content = "测试内容"

        # 创建文件
        self.fs.write_text(old_name, test_content)

        # 重命名
        self.fs.rename(old_name, new_name)

        # 验证
        assert self.fs.exists(new_name)
        assert self.fs.read_text(new_name) == test_content
        assert not self.fs.exists(old_name)

    def test_get_size_file(self):
        """测试获取文件大小"""
        test_file = "test.txt"
        test_content = "测试内容"

        self.fs.write_text(test_file, test_content)

        size = self.fs.get_size(test_file)
        expected_size = len(test_content.encode("utf-8"))
        assert size == expected_size

    def test_get_size_directory(self):
        """测试获取目录大小"""
        test_dir = "test_dir"
        self.fs.create_dir(test_dir)

        # 在目录中创建文件
        file1_content = "文件1内容"
        file2_content = "文件2内容"

        self.fs.write_text(f"{test_dir}/file1.txt", file1_content)
        self.fs.write_text(f"{test_dir}/file2.txt", file2_content)

        size = self.fs.get_size(test_dir)
        expected_size = len(file1_content.encode("utf-8")) + len(
            file2_content.encode("utf-8")
        )
        assert size == expected_size

    def test_search_files(self):
        """测试搜索文件"""
        # 创建测试文件
        files = ["test1.txt", "test2.py", "data.txt", "script.py"]
        for filename in files:
            self.fs.write_text(filename, "content")

        # 搜索.txt文件
        txt_files = self.fs.search(".", "*.txt")
        txt_names = [f.name for f in txt_files]
        assert "test1.txt" in txt_names
        assert "data.txt" in txt_names
        assert "test2.py" not in txt_names

        # 搜索.py文件
        py_files = self.fs.search(".", "*.py")
        py_names = [f.name for f in py_files]
        assert "test2.py" in py_names
        assert "script.py" in py_names
        assert "test1.txt" not in py_names

    def test_path_resolution_with_base_path(self):
        """测试基础路径下的路径解析"""
        # 测试相对路径
        self.fs.write_text("relative.txt", "content")
        assert self.fs.exists("relative.txt")

        # 测试绝对路径（在基础路径内）
        abs_path = os.path.join(self.temp_dir, "absolute.txt")
        self.fs.write_text(abs_path, "content")
        assert self.fs.exists(abs_path)

    def test_invalid_path_outside_base(self):
        """测试访问基础路径外的路径"""
        outside_path = "/tmp/outside.txt"

        with pytest.raises(InvalidPathError):
            self.fs.write_text(outside_path, "content")
