"""测试 API 的基本功能"""

import asyncio
import json
import os
from urllib.parse import urljoin

import httpx


async def test_api():
    """测试 API 的基本功能"""
    base_url = "http://localhost:8000"

    async with httpx.AsyncClient() as client:
        # 1. 测试根端点
        print("1. 测试根端点...")
        response = await client.get(f"{base_url}/")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()

        # 2. 测试健康检查
        print("2. 测试健康检查...")
        response = await client.get(f"{base_url}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()

        # 3. 创建会话（需要设置环境变量）
        session_id = "test-session-001"
        print(f"3. 创建会话 {session_id}...")

        session_data = {
            "session_id": session_id,
            "name": "测试会话",
            "description": "这是一个测试会话",
            "llm_provider": "openai",
            "llm_settings": {
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "api_key": os.getenv("OPENAI_API_KEY", "test-key"),
            },
        }

        try:
            response = await client.post(
                f"{base_url}/api/v1/sessions/", json=session_data
            )
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                print(f"响应: {response.json()}")
            else:
                print(f"错误: {response.text}")
        except Exception as e:
            print(f"创建会话失败: {e}")
        print()

        # 4. 列出会话
        print("4. 列出会话...")
        try:
            response = await client.get(f"{base_url}/api/v1/sessions/")
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.json()}")
        except Exception as e:
            print(f"列出会话失败: {e}")
        print()

        # 5. 测试非流式聊天（如果有API key）
        if os.getenv("OPENAI_API_KEY"):
            print("5. 测试非流式聊天...")
            chat_data = {
                "session_id": session_id,
                "message": "你好，请用一句话介绍你自己",
                "stream": False,
            }

            try:
                response = await client.post(
                    f"{base_url}/api/v1/chat/completions", json=chat_data, timeout=30.0
                )
                print(f"状态码: {response.status_code}")
                if response.status_code == 200:
                    print(f"响应: {response.json()}")
                else:
                    print(f"错误: {response.text}")
            except Exception as e:
                print(f"聊天失败: {e}")
            print()

            # 6. 测试流式聊天
            print("6. 测试流式聊天...")
            chat_data["stream"] = True
            chat_data["message"] = "请详细解释什么是人工智能"

            try:
                async with client.stream(
                    "POST",
                    f"{base_url}/api/v1/chat/completions",
                    json=chat_data,
                    timeout=30.0,
                ) as response:
                    print(f"状态码: {response.status_code}")
                    if response.status_code == 200:
                        print("流式响应:")
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                data_str = line[6:]  # 去掉 "data: " 前缀
                                if data_str == "[DONE]":
                                    print("[完成]")
                                    break
                                try:
                                    data = json.loads(data_str)
                                    print(f"  {data}")
                                except json.JSONDecodeError:
                                    continue
                    else:
                        print(f"错误: {await response.aread()}")
            except Exception as e:
                print(f"流式聊天失败: {e}")
        else:
            print("5-6. 跳过聊天测试（未设置 OPENAI_API_KEY）")


if __name__ == "__main__":
    print("AgenticZero API 测试")
    print("=" * 50)
    print("请确保 API 服务器正在运行: make api-dev")
    print("如需测试聊天功能，请设置 OPENAI_API_KEY 环境变量")
    print("=" * 50)
    print()

    asyncio.run(test_api())
