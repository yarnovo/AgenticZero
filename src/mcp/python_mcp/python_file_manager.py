"""Python 文件管理器

负责管理 Python 文件的创建、读取、修改、删除等操作
"""

import ast
import builtins
import json
from datetime import datetime
from pathlib import Path
from typing import Any


class PythonFileManager:
    """Python 文件管理器"""

    def __init__(self, base_dir: str = "python_scripts"):
        """初始化文件管理器

        Args:
            base_dir: Python 文件存储的基础目录
        """
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.base_dir / ".metadata.json"
        self._load_metadata()

    def _load_metadata(self) -> None:
        """加载文件元数据"""
        if self.metadata_file.exists():
            with open(self.metadata_file, encoding="utf-8") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}

    def _save_metadata(self) -> None:
        """保存文件元数据"""
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)

    def _validate_python_syntax(self, code: str) -> tuple[bool, str | None]:
        """验证 Python 代码语法

        Args:
            code: Python 代码

        Returns:
            (是否有效, 错误信息)
        """
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"语法错误: 第 {e.lineno} 行 - {e.msg}"

    def create(self, name: str, code: str, description: str = "") -> dict[str, Any]:
        """创建 Python 文件

        Args:
            name: 文件名（不含 .py 后缀）
            code: Python 代码
            description: 文件描述

        Returns:
            文件信息
        """
        # 验证文件名
        if not name or not name.replace("_", "").replace("-", "").isalnum():
            raise ValueError(f"无效的文件名: {name}")

        # 验证语法
        is_valid, error_msg = self._validate_python_syntax(code)
        if not is_valid:
            raise ValueError(error_msg)

        # 创建文件路径
        file_path = self.base_dir / f"{name}.py"
        if file_path.exists():
            raise FileExistsError(f"文件已存在: {name}.py")

        # 写入文件
        file_path.write_text(code, encoding="utf-8")

        # 更新元数据
        file_info = {
            "name": name,
            "path": str(file_path),
            "description": description,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "size": len(code),
            "lines": len(code.splitlines()),
        }
        self.metadata[name] = file_info
        self._save_metadata()

        return file_info

    def read(self, name: str) -> dict[str, Any]:
        """读取 Python 文件

        Args:
            name: 文件名（不含 .py 后缀）

        Returns:
            包含文件内容和元数据的字典
        """
        if name not in self.metadata:
            raise FileNotFoundError(f"文件不存在: {name}")

        file_path = Path(self.metadata[name]["path"])
        if not file_path.exists():
            raise FileNotFoundError(f"文件路径不存在: {file_path}")

        code = file_path.read_text(encoding="utf-8")

        return {"name": name, "code": code, "metadata": self.metadata[name]}

    def update(self, name: str, code: str) -> dict[str, Any]:
        """更新 Python 文件

        Args:
            name: 文件名（不含 .py 后缀）
            code: 新的 Python 代码

        Returns:
            更新后的文件信息
        """
        if name not in self.metadata:
            raise FileNotFoundError(f"文件不存在: {name}")

        # 验证语法
        is_valid, error_msg = self._validate_python_syntax(code)
        if not is_valid:
            raise ValueError(error_msg)

        # 更新文件
        file_path = Path(self.metadata[name]["path"])
        file_path.write_text(code, encoding="utf-8")

        # 更新元数据
        self.metadata[name]["updated_at"] = datetime.now().isoformat()
        self.metadata[name]["size"] = len(code)
        self.metadata[name]["lines"] = len(code.splitlines())
        self._save_metadata()

        return self.metadata[name]

    def delete(self, name: str) -> None:
        """删除 Python 文件

        Args:
            name: 文件名（不含 .py 后缀）
        """
        if name not in self.metadata:
            raise FileNotFoundError(f"文件不存在: {name}")

        # 删除文件
        file_path = Path(self.metadata[name]["path"])
        if file_path.exists():
            file_path.unlink()

        # 删除元数据
        del self.metadata[name]
        self._save_metadata()

    def list(self) -> list[dict[str, Any]]:
        """列出所有 Python 文件

        Returns:
            文件信息列表
        """
        return list(self.metadata.values())

    def exists(self, name: str) -> bool:
        """检查文件是否存在

        Args:
            name: 文件名（不含 .py 后缀）

        Returns:
            是否存在
        """
        return name in self.metadata

    def search(self, keyword: str) -> builtins.list[dict[str, Any]]:
        """搜索 Python 文件

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的文件列表
        """
        results = []
        keyword_lower = keyword.lower()

        for name, info in self.metadata.items():
            # 搜索文件名和描述
            if (
                keyword_lower in name.lower()
                or keyword_lower in info.get("description", "").lower()
            ):
                results.append(info)
                continue

            # 搜索文件内容
            try:
                file_path = Path(info["path"])
                if file_path.exists():
                    content = file_path.read_text(encoding="utf-8")
                    if keyword in content:
                        results.append(info)
            except Exception:
                pass

        return results
