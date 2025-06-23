"""Ollama 本地模型使用示例。"""

import asyncio

from src.agent import Agent, AgentSettings, LLMSettings


async def main():
    """Ollama 使用示例。"""
    print("=== Ollama 本地模型示例 ===")

    # 检查 Ollama 服务是否可用
    try:
        import requests

        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("❌ 错误：无法连接到 Ollama 服务")
            print("请确保：")
            print("1. 已安装 Ollama: https://ollama.com")
            print("2. 已启动服务: ollama serve")
            print("3. 已下载模型: ollama pull llama3.2")
            return

        # 获取可用模型
        models = response.json().get("models", [])
        print(f"✅ 发现 {len(models)} 个本地模型:")
        for model in models:
            print(f"   - {model['name']} ({model.get('size', 'Unknown')})")

        if not models:
            print("❌ 没有发现本地模型，请先下载：")
            print("   ollama pull llama3.2")
            return

    except Exception as e:
        print(f"❌ 无法连接到 Ollama: {e}")
        print("请确保 Ollama 服务正在运行：ollama serve")
        return

    # 使用第一个可用模型，或默认为 llama3.2
    model_name = models[0]["name"] if models else "llama3.2"
    print(f"\n🚀 使用模型: {model_name}")

    # 配置智能体使用 Ollama
    settings = AgentSettings(
        name="ollama_demo",
        instruction="你是一个友好的AI助手，运行在用户的本地计算机上。你的回答要简洁明了。",
        llm_settings=LLMSettings(
            provider="ollama",
            model=model_name,
            base_url="http://localhost:11434",
            temperature=0.7,
            max_tokens=512,
        ),
        # 可以添加一些MCP工具
        mcp_servers={
            # 注意：这里需要确保有可用的MCP服务器
        },
    )

    # 创建智能体
    agent = Agent(config=settings)

    try:
        # 初始化智能体
        print("\n📡 正在初始化智能体...")
        await agent.initialize()
        print("✅ 智能体初始化完成")

        # 示例1：简单对话
        print("\n=== 示例1：基本对话 ===")
        response = await agent.run("你好，请简单介绍一下你自己")
        print(f"助手：{response}")

        # 示例2：流式响应
        print("\n=== 示例2：流式响应 ===")
        print("问题：请解释什么是人工智能？")
        print("助手：", end="", flush=True)

        async for chunk in agent.run_stream("请解释什么是人工智能？"):
            if chunk["type"] == "content":
                print(chunk["content"], end="", flush=True)
            elif chunk["type"] == "complete":
                print(f"\n[✅ 完成，用时 {chunk.get('iterations', 1)} 轮迭代]")

        # 示例3：代码生成
        print("\n=== 示例3：代码生成 ===")
        code_response = await agent.run("写一个Python函数来计算斐波那契数列的第n项")
        print(f"助手：{code_response}")

        # 示例4：连续对话（测试记忆功能）
        print("\n=== 示例4：连续对话 ===")
        await agent.run("我的名字是张三，我是一名软件工程师")
        memory_response = await agent.run("你还记得我的名字和职业吗？")
        print(f"助手：{memory_response}")

        # 显示性能信息
        print("\n=== 性能信息 ===")
        print("✅ 本地运行：完全私密，无需网络")
        print("✅ 无API费用：一次部署，永久使用")
        print("✅ 自定义控制：可调整模型参数")

    except Exception as e:
        print(f"❌ 运行出错: {e}")
        print("可能的解决方案：")
        print("1. 检查模型是否存在：ollama list")
        print("2. 重启 Ollama 服务：ollama serve")
        print("3. 尝试下载其他模型：ollama pull llama3.2")

    finally:
        # 清理资源
        await agent.close()
        print("\n🔚 示例结束")


async def model_comparison():
    """不同模型性能对比示例。"""
    models_to_test = ["llama3.2", "llama3.2:7b", "qwen2.5:7b"]
    test_prompt = "用一句话解释什么是机器学习"

    print("\n=== 模型对比测试 ===")

    for model in models_to_test:
        try:
            print(f"\n🔍 测试模型: {model}")

            settings = AgentSettings(
                name=f"test_{model.replace(':', '_')}",
                instruction="请用简洁明了的语言回答问题。",
                llm_settings=LLMSettings(
                    provider="ollama",
                    model=model,
                    base_url="http://localhost:11434",
                    temperature=0.3,
                    max_tokens=100,
                ),
            )

            agent = Agent(config=settings)
            await agent.initialize()

            import time

            start_time = time.time()
            response = await agent.run(test_prompt)
            end_time = time.time()

            print(f"   响应时间: {end_time - start_time:.2f}秒")
            print(f"   回答: {response[:100]}...")

            await agent.close()

        except Exception as e:
            print(f"   ❌ 模型 {model} 不可用: {e}")


if __name__ == "__main__":
    # 运行主示例
    asyncio.run(main())

    # 可选：运行模型对比
    print("\n" + "=" * 50)
    user_input = input("是否运行模型对比测试？(y/n): ")
    if user_input.lower() == "y":
        asyncio.run(model_comparison())
