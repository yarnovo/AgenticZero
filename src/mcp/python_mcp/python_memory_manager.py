"""Python 内存管理器

负责管理 Python 代码的沙盒执行环境
"""

import io
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, TimeoutError
from typing import Any


class SandboxEnvironment:
    """沙盒执行环境"""

    def __init__(self):
        """初始化沙盒环境"""
        self.globals = self._create_safe_globals()
        self.locals = {}
        self.output_buffer = io.StringIO()
        self.error_buffer = io.StringIO()

    def _create_safe_globals(self) -> dict[str, Any]:
        """创建安全的全局命名空间

        Returns:
            安全的全局变量字典
        """
        # 基础内置函数白名单
        safe_builtins = {
            # 基础类型
            "int",
            "float",
            "str",
            "bool",
            "list",
            "dict",
            "set",
            "tuple",
            "type",
            "object",
            "bytes",
            "bytearray",
            # 数学和逻辑
            "abs",
            "all",
            "any",
            "max",
            "min",
            "sum",
            "round",
            "pow",
            "len",
            "range",
            "enumerate",
            "zip",
            "map",
            "filter",
            # 类型转换
            "chr",
            "ord",
            "hex",
            "oct",
            "bin",
            # 其他安全函数
            "print",
            "sorted",
            "reversed",
            "isinstance",
            "issubclass",
            "hasattr",
            "getattr",
            "setattr",
            "dir",
            "help",
            # 异常
            "Exception",
            "ValueError",
            "TypeError",
            "KeyError",
            "IndexError",
            "AttributeError",
            "RuntimeError",
        }

        # 创建受限的内置函数字典
        restricted_builtins = {}
        for name in safe_builtins:
            if hasattr(__builtins__, name):
                restricted_builtins[name] = getattr(__builtins__, name)

        # 添加受限的 print 函数
        def safe_print(*args, **kwargs):
            """安全的 print 函数，输出到缓冲区"""
            output = io.StringIO()
            kwargs["file"] = output
            print(*args, **kwargs)
            self.output_buffer.write(output.getvalue())

        restricted_builtins["print"] = safe_print

        return {
            "__builtins__": restricted_builtins,
            "__name__": "__main__",
            "__doc__": None,
            "__package__": None,
        }

    def execute(self, code: str, timeout: int = 5) -> tuple[bool, str, str]:
        """在沙盒中执行代码

        Args:
            code: 要执行的 Python 代码
            timeout: 超时时间（秒）

        Returns:
            (是否成功, 输出, 错误信息)
        """
        # 重定向标准输出和错误
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        try:
            sys.stdout = self.output_buffer
            sys.stderr = self.error_buffer

            # 编译代码
            compiled_code = compile(code, "<sandbox>", "exec")

            # 执行代码
            exec(compiled_code, self.globals, self.locals)

            # 获取输出
            output = self.output_buffer.getvalue()
            error = self.error_buffer.getvalue()

            return True, output, error

        except Exception:
            # 获取错误信息
            error_msg = traceback.format_exc()
            return False, self.output_buffer.getvalue(), error_msg

        finally:
            # 恢复标准输出和错误
            sys.stdout = old_stdout
            sys.stderr = old_stderr

            # 清空缓冲区
            self.output_buffer = io.StringIO()
            self.error_buffer = io.StringIO()


def _execute_in_process(code: str, timeout: int) -> tuple[bool, str, str]:
    """在独立进程中执行代码（用于更强的隔离）"""
    sandbox = SandboxEnvironment()
    return sandbox.execute(code, timeout)


class PythonMemoryManager:
    """Python 内存管理器"""

    def __init__(self, max_workers: int = 2):
        """初始化内存管理器

        Args:
            max_workers: 最大工作进程数
        """
        self.sandboxes: dict[str, SandboxEnvironment] = {}
        self.execution_history: list[dict[str, Any]] = []
        self.max_workers = max_workers

    def create_sandbox(self, sandbox_id: str) -> None:
        """创建新的沙盒环境

        Args:
            sandbox_id: 沙盒标识符
        """
        if sandbox_id in self.sandboxes:
            raise ValueError(f"沙盒已存在: {sandbox_id}")

        self.sandboxes[sandbox_id] = SandboxEnvironment()

    def delete_sandbox(self, sandbox_id: str) -> None:
        """删除沙盒环境

        Args:
            sandbox_id: 沙盒标识符
        """
        if sandbox_id not in self.sandboxes:
            raise ValueError(f"沙盒不存在: {sandbox_id}")

        del self.sandboxes[sandbox_id]

    def execute_code(
        self,
        code: str,
        sandbox_id: str | None = None,
        timeout: int = 5,
        use_process: bool = True,
    ) -> dict[str, Any]:
        """执行 Python 代码

        Args:
            code: 要执行的代码
            sandbox_id: 沙盒标识符（None 表示使用临时沙盒）
            timeout: 超时时间（秒）
            use_process: 是否使用独立进程执行（更安全但开销更大）

        Returns:
            执行结果
        """
        start_time = time.time()

        if use_process:
            # 使用独立进程执行
            with ProcessPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_execute_in_process, code, timeout)
                try:
                    success, output, error = future.result(timeout=timeout)
                except TimeoutError:
                    success = False
                    output = ""
                    error = f"执行超时（{timeout}秒）"
        else:
            # 使用沙盒执行
            if sandbox_id and sandbox_id in self.sandboxes:
                sandbox = self.sandboxes[sandbox_id]
            else:
                sandbox = SandboxEnvironment()

            success, output, error = sandbox.execute(code, timeout)

        execution_time = time.time() - start_time

        # 记录执行历史
        result = {
            "success": success,
            "output": output,
            "error": error,
            "code": code,
            "sandbox_id": sandbox_id,
            "execution_time": execution_time,
            "timestamp": time.time(),
        }

        self.execution_history.append(result)

        return result

    def get_sandbox_status(self, sandbox_id: str) -> dict[str, Any]:
        """获取沙盒状态

        Args:
            sandbox_id: 沙盒标识符

        Returns:
            沙盒状态信息
        """
        if sandbox_id not in self.sandboxes:
            raise ValueError(f"沙盒不存在: {sandbox_id}")

        sandbox = self.sandboxes[sandbox_id]

        # 获取沙盒中的变量
        variables = {}
        for name, value in sandbox.locals.items():
            try:
                # 尝试获取变量的字符串表示
                if isinstance(
                    value, int | float | str | bool | list | dict | set | tuple
                ):
                    variables[name] = {
                        "type": type(value).__name__,
                        "value": str(value)[:100],  # 限制长度
                    }
                else:
                    variables[name] = {
                        "type": type(value).__name__,
                        "value": f"<{type(value).__name__} object>",
                    }
            except Exception:
                variables[name] = {"type": "unknown", "value": "<无法显示>"}

        return {
            "sandbox_id": sandbox_id,
            "variables": variables,
            "variable_count": len(variables),
        }

    def list_sandboxes(self) -> list[str]:
        """列出所有沙盒

        Returns:
            沙盒标识符列表
        """
        return list(self.sandboxes.keys())

    def get_execution_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """获取执行历史

        Args:
            limit: 返回的最大记录数

        Returns:
            执行历史列表
        """
        return self.execution_history[-limit:]

    def clear_history(self) -> None:
        """清空执行历史"""
        self.execution_history.clear()
