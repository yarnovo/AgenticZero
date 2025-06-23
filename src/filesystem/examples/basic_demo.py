"""文件系统模块基础功能演示"""

import tempfile

from ..core import FileManager
from ..local_filesystem import LocalFileSystem


def basic_operations_demo():
    """基础文件操作演示"""
    print("=== 文件系统模块基础操作演示 ===\n")

    # 创建临时目录用于演示
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"使用临时目录: {temp_dir}\n")

        # 初始化文件管理器
        fs = LocalFileSystem(temp_dir)
        manager = FileManager(fs)

        # 1. 创建目录
        print("1. 创建目录结构")
        manager.create_dir("docs")
        manager.create_dir("src/utils")
        manager.create_dir("tests")
        print("   ✓ 目录创建完成\n")

        # 2. 写入文件
        print("2. 写入文件")
        manager.write_text("README.md", "# 文件系统模块演示\n\n这是一个演示项目。")
        manager.write_text("src/main.py", "def main():\n    print('Hello, World!')\n")
        manager.write_text(
            "src/utils/helper.py", "def helper_function():\n    return '辅助函数'"
        )
        manager.write_bytes("docs/binary_file.bin", b"Binary content example")
        print("   ✓ 文件写入完成\n")

        # 3. 列出目录内容
        print("3. 列出目录内容")
        root_items = manager.list_dir(".")
        print("   根目录内容:")
        for item in root_items:
            print(f"   - {item.name} ({item.file_type.value}, {item.size} bytes)")
        print()

        # 4. 读取文件
        print("4. 读取文件内容")
        readme_content = manager.read_text("README.md")
        print(f"   README.md 内容:\n   {readme_content}\n")

        # 5. 获取文件信息
        print("5. 获取文件信息")
        main_info = manager.get_info("src/main.py")
        print(f"   文件: {main_info.name}")
        print(f"   大小: {main_info.size} bytes")
        print(f"   修改时间: {main_info.modified_time}")
        print(f"   可读: {main_info.is_readable}")
        print(f"   可写: {main_info.is_writable}")
        print()

        # 6. 搜索文件
        print("6. 搜索文件")
        py_files = manager.search(".", "*.py")
        print("   找到的Python文件:")
        for file_info in py_files:
            print(f"   - {file_info.path}")
        print()

        # 7. 复制文件
        print("7. 复制文件")
        manager.copy_file("README.md", "docs/README_copy.md")
        print("   ✓ 文件复制完成\n")

        # 8. 移动文件
        print("8. 移动文件")
        manager.move("docs/README_copy.md", "docs/README_moved.md")
        print("   ✓ 文件移动完成\n")

        # 9. 获取目录树
        print("9. 获取目录树结构")
        tree = manager.get_dir_tree(".")
        print_tree(tree, ".")
        print()

        # 10. 追加内容
        print("10. 追加文件内容")
        manager.append_text("README.md", "\n\n## 更新日志\n- 添加了新功能")
        updated_content = manager.read_text("README.md")
        print(f"   更新后的内容:\n   {updated_content}\n")

        # 11. 获取大小
        print("11. 获取文件和目录大小")
        readme_size = manager.get_size("README.md")
        total_size = manager.get_size(".")
        print(f"   README.md 大小: {readme_size} bytes")
        print(f"   整个目录大小: {total_size} bytes")
        print()


def print_tree(tree_dict, name, indent=""):
    """打印目录树"""
    print(f"{indent}{name}/")
    children = tree_dict.get("children", {})
    items = list(children.items())

    for i, (child_name, child_data) in enumerate(items):
        is_last = i == len(items) - 1
        child_indent = indent + ("    " if is_last else "│   ")
        prefix = "└── " if is_last else "├── "

        if child_data.get("type") == "directory":
            print(f"{indent}{prefix}{child_name}/")
            print_tree(child_data, "", child_indent)
        else:
            size = child_data.get("size", 0)
            print(f"{indent}{prefix}{child_name} ({size} bytes)")


def error_handling_demo():
    """错误处理演示"""
    print("=== 错误处理演示 ===\n")

    # 使用不受限制的文件系统
    fs = LocalFileSystem()
    manager = FileManager(fs)

    # 1. 尝试访问不存在的文件
    print("1. 访问不存在的文件")
    try:
        manager.read_text("/nonexistent/file.txt")
    except Exception as e:
        print(f"   捕获异常: {type(e).__name__}: {e}")
    print()

    # 2. 尝试在不存在的目录中创建文件
    print("2. 在不存在的目录创建文件（不自动创建目录）")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_fs = LocalFileSystem(temp_dir)
            temp_manager = FileManager(temp_fs)
            temp_manager.write_text(
                "nonexistent/file.txt", "content", create_dirs=False
            )
    except Exception as e:
        print(f"   捕获异常: {type(e).__name__}: {e}")
    print()


def advanced_demo():
    """高级功能演示"""
    print("=== 高级功能演示 ===\n")

    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"使用临时目录: {temp_dir}\n")

        # 创建受限的文件系统
        fs = LocalFileSystem(temp_dir)
        manager = FileManager(fs)

        # 1. 批量操作
        print("1. 批量文件操作")

        # 创建多个文件
        files_to_create = [
            ("file1.txt", "内容1"),
            ("file2.txt", "内容2"),
            ("subdir/file3.txt", "内容3"),
            ("subdir/file4.txt", "内容4"),
        ]

        for filename, content in files_to_create:
            manager.write_text(filename, content)

        print(f"   ✓ 创建了 {len(files_to_create)} 个文件")

        # 2. 递归列出所有文件
        print("\n2. 递归列出所有文件")
        all_files = manager.list_dir(".", recursive=True)
        for file_info in all_files:
            if file_info.file_type.value == "file":
                print(f"   - {file_info.path} ({file_info.size} bytes)")

        # 3. 安全删除演示
        print("\n3. 安全删除文件")
        success = manager.safe_remove("file1.txt")
        print(f"   删除 file1.txt: {'成功' if success else '失败'}")

        success = manager.safe_remove("nonexistent.txt")
        print(f"   删除不存在文件: {'成功' if success else '失败'}")

        # 4. 目录大小统计
        print("\n4. 目录大小统计")
        total_size = manager.get_size(".")
        print(f"   总大小: {total_size} bytes")

        print()


if __name__ == "__main__":
    basic_operations_demo()
    print("\n" + "=" * 50 + "\n")
    error_handling_demo()
    print("\n" + "=" * 50 + "\n")
    advanced_demo()
