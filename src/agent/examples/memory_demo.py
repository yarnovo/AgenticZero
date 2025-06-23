#!/usr/bin/env python3
"""记忆功能演示示例。"""

import asyncio
import logging

from src.agent import Agent, AgentSettings, LLMSettings

# 设置日志
logging.basicConfig(level=logging.INFO)


async def main():
    """演示记忆功能的使用。"""

    # 创建智能体配置
    settings = AgentSettings(
        name="memory_agent",
        instruction="你是一个具有记忆能力的AI助手。你可以记住重要信息并在需要时回忆它们。",
        llm_settings=LLMSettings(
            provider="openai",
            api_key="your-api-key",  # 替换为你的API密钥
            model="gpt-4",
            temperature=0.7,
        ),
        max_iterations=5,
    )

    # 创建智能体
    agent = Agent(
        config=settings,
        conversation_id="memory_demo",
    )

    # 使用上下文管理器自动初始化和清理
    async with agent.connect():
        print("=== 记忆功能演示 ===\n")

        # 演示1：存储记忆
        print("1. 存储一些重要信息...")
        response = await agent.run(
            "请使用memory_store工具记住以下信息：我最喜欢的编程语言是Python，"
            "我正在开发一个名为AgenticZero的智能体框架。这些是重要信息。"
        )
        print(f"助手: {response}\n")

        # 演示2：搜索记忆
        print("2. 搜索相关记忆...")
        response = await agent.run("使用memory_search工具搜索关于'编程语言'的记忆。")
        print(f"助手: {response}\n")

        # 演示3：获取重要记忆
        print("3. 获取重要的记忆...")
        response = await agent.run("使用memory_get_important工具获取最重要的记忆。")
        print(f"助手: {response}\n")

        # 演示4：基于记忆回答问题
        print("4. 基于记忆回答问题...")
        response = await agent.run(
            "我之前告诉过你我最喜欢的编程语言是什么吗？我在开发什么项目？"
        )
        print(f"助手: {response}\n")

        # 演示5：查看记忆统计
        print("5. 查看记忆系统统计...")
        response = await agent.run("使用memory_stats工具查看记忆系统的统计信息。")
        print(f"助手: {response}\n")

        # 演示6：整合记忆
        print("6. 整合短期记忆为长期记忆...")
        response = await agent.run("使用memory_consolidate工具整合记忆。")
        print(f"助手: {response}\n")


if __name__ == "__main__":
    asyncio.run(main())
