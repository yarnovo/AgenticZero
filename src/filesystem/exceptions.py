"""文件管理模块异常定义"""


class FileManagerError(Exception):
    """文件管理器基础异常"""

    def __init__(self, message: str, path: str | None = None):
        super().__init__(message)
        self.message = message
        self.path = path

    def __str__(self) -> str:
        if self.path:
            return f"{self.message} (路径: {self.path})"
        return self.message


class FileNotFoundError(FileManagerError):
    """文件不存在异常"""

    def __init__(self, path: str):
        super().__init__("文件或目录不存在", path)


class PermissionError(FileManagerError):
    """权限不足异常"""

    def __init__(self, path: str, operation: str):
        super().__init__(f"没有权限执行操作: {operation}", path)
        self.operation = operation


class DirectoryNotEmptyError(FileManagerError):
    """目录非空异常"""

    def __init__(self, path: str):
        super().__init__("目录不为空，无法删除", path)


class FileAlreadyExistsError(FileManagerError):
    """文件已存在异常"""

    def __init__(self, path: str):
        super().__init__("文件或目录已存在", path)


class InvalidPathError(FileManagerError):
    """无效路径异常"""

    def __init__(self, path: str, reason: str = ""):
        message = "无效的路径格式"
        if reason:
            message += f": {reason}"
        super().__init__(message, path)
