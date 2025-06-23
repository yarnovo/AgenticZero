"""Python 文件管理器测试"""

import tempfile

import pytest

from src.mcp.python_mcp.python_file_manager import PythonFileManager


@pytest.fixture
def temp_dir():
    """创建临时目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def file_manager(temp_dir):
    """创建文件管理器实例"""
    return PythonFileManager(base_dir=temp_dir)


class TestPythonFileManager:
    """Python 文件管理器测试类"""

    @pytest.mark.unit
    def test_create_file(self, file_manager):
        """测试创建文件"""
        code = """def hello():
    print("Hello, World!")
"""
        result = file_manager.create("test_file", code, "测试文件")

        assert result["name"] == "test_file"
        assert result["lines"] == 2
        assert result["description"] == "测试文件"
        assert file_manager.exists("test_file")

    @pytest.mark.unit
    def test_create_file_syntax_error(self, file_manager):
        """测试创建语法错误的文件"""
        code = """def hello()  # 缺少冒号
    print("Hello")
"""
        with pytest.raises(ValueError, match="语法错误"):
            file_manager.create("bad_syntax", code)

    @pytest.mark.unit
    def test_create_duplicate_file(self, file_manager):
        """测试创建重复文件"""
        code = "print('test')"
        file_manager.create("duplicate", code)

        with pytest.raises(FileExistsError):
            file_manager.create("duplicate", code)

    @pytest.mark.unit
    def test_read_file(self, file_manager):
        """测试读取文件"""
        code = "x = 42"
        file_manager.create("read_test", code)

        result = file_manager.read("read_test")
        assert result["name"] == "read_test"
        assert result["code"] == code
        assert "metadata" in result

    @pytest.mark.unit
    def test_read_nonexistent_file(self, file_manager):
        """测试读取不存在的文件"""
        with pytest.raises(FileNotFoundError):
            file_manager.read("nonexistent")

    @pytest.mark.unit
    def test_update_file(self, file_manager):
        """测试更新文件"""
        file_manager.create("update_test", "x = 1")

        new_code = "x = 42\ny = 100"
        result = file_manager.update("update_test", new_code)

        assert result["lines"] == 2
        assert file_manager.read("update_test")["code"] == new_code

    @pytest.mark.unit
    def test_update_with_syntax_error(self, file_manager):
        """测试更新文件时的语法错误"""
        file_manager.create("syntax_test", "x = 1")

        with pytest.raises(ValueError, match="语法错误"):
            file_manager.update("syntax_test", "def bad(")

    @pytest.mark.unit
    def test_delete_file(self, file_manager):
        """测试删除文件"""
        file_manager.create("delete_test", "x = 1")
        assert file_manager.exists("delete_test")

        file_manager.delete("delete_test")
        assert not file_manager.exists("delete_test")

    @pytest.mark.unit
    def test_delete_nonexistent_file(self, file_manager):
        """测试删除不存在的文件"""
        with pytest.raises(FileNotFoundError):
            file_manager.delete("nonexistent")

    @pytest.mark.unit
    def test_list_files(self, file_manager):
        """测试列出所有文件"""
        # 创建多个文件
        file_manager.create("file1", "x = 1")
        file_manager.create("file2", "x = 2")
        file_manager.create("file3", "x = 3")

        files = file_manager.list()
        assert len(files) == 3
        names = [f["name"] for f in files]
        assert "file1" in names
        assert "file2" in names
        assert "file3" in names

    @pytest.mark.unit
    def test_search_files(self, file_manager):
        """测试搜索文件"""
        # 创建测试文件
        file_manager.create("math_utils", "def add(a, b): return a + b", "数学工具")
        file_manager.create(
            "string_utils", "def upper(s): return s.upper()", "字符串工具"
        )
        file_manager.create("test_math", "import math_utils", "测试数学")

        # 按文件名搜索
        results = file_manager.search("math")
        assert len(results) == 2

        # 按描述搜索
        results = file_manager.search("工具")
        assert len(results) == 2

        # 按内容搜索
        results = file_manager.search("upper")
        assert len(results) == 1
        assert results[0]["name"] == "string_utils"

    @pytest.mark.unit
    def test_invalid_filename(self, file_manager):
        """测试无效文件名"""
        with pytest.raises(ValueError, match="无效的文件名"):
            file_manager.create("", "x = 1")

        with pytest.raises(ValueError, match="无效的文件名"):
            file_manager.create("test/file", "x = 1")

        with pytest.raises(ValueError, match="无效的文件名"):
            file_manager.create("test.py", "x = 1")

    @pytest.mark.unit
    def test_metadata_persistence(self, file_manager):
        """测试元数据持久化"""
        # 创建文件
        file_manager.create("meta_test", "x = 1", "元数据测试")

        # 创建新的管理器实例（模拟重启）
        new_manager = PythonFileManager(base_dir=file_manager.base_dir)

        # 检查元数据是否被正确加载
        assert new_manager.exists("meta_test")
        file_info = new_manager.read("meta_test")
        assert file_info["metadata"]["description"] == "元数据测试"
