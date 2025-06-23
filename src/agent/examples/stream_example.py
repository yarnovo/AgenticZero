"""流式响应示例代码。"""

import asyncio
import os

from src.agent import Agent, AgentSettings, LLMSettings


async def main():
    """流式响应示例。"""
    # 配置智能体
    settings = AgentSettings(
        name="stream_demo",
        instruction="你是一个友好的AI助手，擅长详细解释各种概念。",
        llm_settings=LLMSettings(
            provider="openai",
            api_key=os.getenv("OPENAI_API_KEY", "your-key-here"),
            model="gpt-3.5-turbo",
            temperature=0.7,
        ),
    )

    # 创建智能体
    agent = Agent(config=settings)

    try:
        # 初始化智能体
        await agent.initialize()

        # 使用流式响应
        print("=== 流式响应示例 ===")
        print("问题：什么是人工智能？请详细解释。")
        print("\n助手：", end="", flush=True)

        # 收集完整响应用于演示
        full_response = ""
        tool_calls = []

        async for chunk in agent.run_stream("什么是人工智能？请详细解释。"):
            # 处理不同类型的流式响应片段
            if chunk["type"] == "content":
                # 实时打印内容片段
                content = chunk["content"]
                print(content, end="", flush=True)
                full_response += content

            elif chunk["type"] == "tool_call":
                # 记录工具调用
                tool_calls.append(chunk)
                print(f"\n[调用工具: {chunk['tool']} - 参数: {chunk['arguments']}]")

            elif chunk["type"] == "tool_result":
                # 显示工具结果
                success = "成功" if chunk["success"] else "失败"
                print(f"\n[工具 {chunk['tool']} 执行{success}]")
                if chunk["success"]:
                    print(f"[结果: {chunk['result'][:100]}...]")  # 只显示前100字符

            elif chunk["type"] == "iteration":
                # 显示迭代信息（通常用于调试）
                if chunk["current"] > 1:
                    print(f"\n[进入第 {chunk['current']} 轮迭代]")

            elif chunk["type"] == "complete":
                # 完成标记
                print(f"\n\n[响应完成 - 共 {chunk['iterations']} 轮迭代]")

            elif chunk["type"] == "error":
                # 错误信息
                print(f"\n[错误: {chunk['error']}]")

        # 显示统计信息
        print(f"\n总字符数: {len(full_response)}")
        print(f"工具调用次数: {len(tool_calls)}")

        # 演示对比：非流式响应
        print("\n\n=== 非流式响应示例（对比）===")
        print("问题：你好")
        print("助手：", end="", flush=True)

        # 非流式响应需要等待完整响应
        response = await agent.run("你好")
        print(response)

    finally:
        # 清理资源
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
