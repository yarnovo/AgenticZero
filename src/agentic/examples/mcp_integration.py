"""MCP 集成示例。"""

import asyncio
import os

from ..agent import AgenticAgent
from ..config import AgentConfig, LLMConfig, MCPServerConfig


async def filesystem_mcp_example():
    """使用文件系统 MCP 服务器的示例。"""

    # 配置文件系统 MCP 服务器
    config = AgentConfig(
        name="filesystem_agent",
        instruction="你是一个可以访问文件系统的智能体助手。",
        llm_config=LLMConfig(
            provider="openai",
            api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"),
            model="gpt-4",
        ),
        mcp_servers={
            "filesystem": MCPServerConfig(
                name="filesystem",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
                env={},
            )
        },
    )

    async with AgenticAgent(config).connect() as agent:
        # 列出文件
        response = await agent.run("请列出 /tmp 目录下的文件")
        print(f"文件列表: {response}")

        # 创建一个测试文件
        response = await agent.run(
            "请在 /tmp 目录下创建一个名为 test.txt 的文件，内容为 'Hello from AgenticAgent!'"
        )
        print(f"创建文件: {response}")

        # 读取文件内容
        response = await agent.run("请读取 /tmp/test.txt 文件的内容")
        print(f"文件内容: {response}")


async def git_mcp_example():
    """使用 Git MCP 服务器的示例。"""

    config = AgentConfig(
        name="git_agent",
        instruction="你是一个可以操作 Git 仓库的智能体助手。",
        llm_config=LLMConfig(
            provider="openai",
            api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"),
            model="gpt-4",
        ),
        mcp_servers={
            "git": MCPServerConfig(
                name="git",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-git", "--repository", "."],
                env={},
            )
        },
    )

    async with AgenticAgent(config).connect() as agent:
        # 查看仓库状态
        response = await agent.run("请查看当前 Git 仓库的状态")
        print(f"Git 状态: {response}")

        # 查看最近的提交
        response = await agent.run("请显示最近 5 次提交的信息")
        print(f"最近提交: {response}")


async def sqlite_mcp_example():
    """使用 SQLite MCP 服务器的示例。"""

    config = AgentConfig(
        name="sqlite_agent",
        instruction="你是一个可以操作 SQLite 数据库的智能体助手。",
        llm_config=LLMConfig(
            provider="openai",
            api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"),
            model="gpt-4",
        ),
        mcp_servers={
            "sqlite": MCPServerConfig(
                name="sqlite",
                command="npx",
                args=[
                    "-y",
                    "@modelcontextprotocol/server-sqlite",
                    "--db-path",
                    "/tmp/test.db",
                ],
                env={},
            )
        },
    )

    async with AgenticAgent(config).connect() as agent:
        # 创建表
        response = await agent.run("""
        请创建一个名为 users 的表，包含以下字段：
        - id (主键，自增)
        - name (文本)
        - email (文本)
        - created_at (时间戳)
        """)
        print(f"创建表: {response}")

        # 插入数据
        response = await agent.run("""
        请向 users 表中插入几条测试数据：
        1. 张三，zhangsan@example.com
        2. 李四，lisi@example.com
        3. 王五，wangwu@example.com
        """)
        print(f"插入数据: {response}")

        # 查询数据
        response = await agent.run("请查询 users 表中的所有数据")
        print(f"查询结果: {response}")


async def multi_mcp_example():
    """使用多个 MCP 服务器的综合示例。"""

    config = AgentConfig(
        name="multi_mcp_agent",
        instruction="你是一个多功能智能体，可以访问文件系统、Git 和数据库。",
        llm_config=LLMConfig(
            provider="openai",
            api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"),
            model="gpt-4",
        ),
        mcp_servers={
            "filesystem": MCPServerConfig(
                name="filesystem",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
                env={},
            ),
            "git": MCPServerConfig(
                name="git",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-git", "--repository", "."],
                env={},
            ),
            "sqlite": MCPServerConfig(
                name="sqlite",
                command="npx",
                args=[
                    "-y",
                    "@modelcontextprotocol/server-sqlite",
                    "--db-path",
                    "/tmp/project.db",
                ],
                env={},
            ),
        },
    )

    async with AgenticAgent(config).connect() as agent:
        # 综合任务：创建项目报告
        response = await agent.run("""
        请帮我创建一个项目报告，包含以下信息：
        1. 查看当前 Git 仓库的状态和最近 3 次提交
        2. 在数据库中创建一个 project_files 表，记录项目中的重要文件
        3. 将报告保存到 /tmp/project_report.md 文件中
        """)
        print(f"项目报告: {response}")


async def custom_mcp_server_example():
    """自定义 MCP 服务器示例。"""

    # 这里演示如何配置自定义的 MCP 服务器
    config = AgentConfig(
        name="custom_mcp_agent",
        instruction="你是一个使用自定义 MCP 服务器的智能体。",
        llm_config=LLMConfig(
            provider="openai",
            api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"),
            model="gpt-4",
        ),
        mcp_servers={
            "custom_server": MCPServerConfig(
                name="custom_server",
                command="python",  # 假设有一个自定义的 Python MCP 服务器
                args=["-m", "custom_mcp_server"],
                env={"CUSTOM_CONFIG": "value", "LOG_LEVEL": "DEBUG"},
            )
        },
    )

    try:
        async with AgenticAgent(config).connect() as agent:
            response = await agent.run("使用自定义服务器执行一些操作")
            print(f"自定义服务器响应: {response}")
    except Exception as e:
        print(f"自定义服务器示例出错（这是正常的，因为服务器不存在）: {e}")


async def mcp_error_handling_example():
    """MCP 错误处理示例。"""

    # 配置一个不存在的 MCP 服务器来演示错误处理
    config = AgentConfig(
        name="error_handling_agent",
        instruction="你是一个测试错误处理的智能体。",
        llm_config=LLMConfig(
            provider="openai",
            api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"),
            model="gpt-4",
        ),
        mcp_servers={
            "nonexistent": MCPServerConfig(
                name="nonexistent",
                command="nonexistent_command",
                args=["--invalid", "args"],
                env={},
            )
        },
    )

    try:
        async with AgenticAgent(config).connect() as agent:
            response = await agent.run("尝试使用不存在的服务器")
            print(f"意外成功: {response}")
    except Exception as e:
        print(f"预期的错误（服务器不存在）: {e}")

        # 演示如何在运行时处理 MCP 错误
        print("现在演示正常的 MCP 服务器...")

        # 使用正常的配置
        valid_config = AgentConfig(
            name="recovery_agent",
            instruction="你是一个从错误中恢复的智能体。",
            llm_config=LLMConfig(
                provider="openai",
                api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"),
                model="gpt-4",
            ),
            mcp_servers={
                "filesystem": MCPServerConfig(
                    name="filesystem",
                    command="npx",
                    args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
                    env={},
                )
            },
        )

        async with AgenticAgent(valid_config).connect() as agent:
            response = await agent.run("现在可以正常工作了，请列出 /tmp 目录的内容")
            print(f"恢复后的响应: {response}")


async def mcp_health_monitoring_example():
    """MCP 健康监控示例。"""

    config = AgentConfig(
        name="health_monitoring_agent",
        instruction="你是一个健康监控智能体。",
        llm_config=LLMConfig(
            provider="openai",
            api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"),
            model="gpt-4",
        ),
        mcp_servers={
            "filesystem": MCPServerConfig(
                name="filesystem",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
                env={},
            )
        },
    )

    async with AgenticAgent(config).connect() as agent:
        # 定期检查 MCP 服务器健康状态
        for i in range(3):
            print(f"\n--- 健康检查 {i + 1} ---")

            health = await agent.get_health_status()
            print("智能体健康状态:")
            print(f"  - 名称: {health['name']}")
            print(f"  - MCP 提供商健康: {health['mcp_provider']['healthy']}")
            print(f"  - 连接的服务器数: {health['mcp_provider']['connected_servers']}")
            print(f"  - 总服务器数: {health['mcp_provider']['total_servers']}")

            # 测试 MCP 服务器功能
            response = await agent.run(f"第 {i + 1} 次测试：请列出 /tmp 目录下的文件")
            print(
                f"MCP 功能测试: {'正常' if '文件' in response or 'directory' in response.lower() else '异常'}"
            )

            await asyncio.sleep(2)


async def main():
    """运行所有 MCP 集成示例。"""
    examples = [
        ("文件系统 MCP", filesystem_mcp_example),
        ("Git MCP", git_mcp_example),
        ("SQLite MCP", sqlite_mcp_example),
        ("多 MCP 服务器", multi_mcp_example),
        ("自定义 MCP 服务器", custom_mcp_server_example),
        ("MCP 错误处理", mcp_error_handling_example),
        ("MCP 健康监控", mcp_health_monitoring_example),
    ]

    for name, example_func in examples:
        print(f"\n{'=' * 60}")
        print(f"运行示例: {name}")
        print(f"{'=' * 60}")

        try:
            await example_func()
            print(f"✅ {name} 示例完成")
        except Exception as e:
            print(f"❌ {name} 示例出错: {e}")

        print(f"{'=' * 60}\n")


if __name__ == "__main__":
    print("MCP 集成示例演示")
    print("注意：需要安装相应的 MCP 服务器包才能运行这些示例")
    print("例如：npm install -g @modelcontextprotocol/server-filesystem")

    asyncio.run(main())
