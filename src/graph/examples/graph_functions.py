"""
图配置中使用的示例函数
"""

import asyncio
import random
from typing import Any


async def prepare_data(context: dict[str, Any]) -> dict[str, Any]:
    """准备数据"""
    print("准备数据中...")
    await asyncio.sleep(0.5)

    data = {
        "items": [random.randint(1, 100) for _ in range(10)],
        "timestamp": asyncio.get_event_loop().time(),
    }

    context["data"] = data
    return data


async def process_data(context: dict[str, Any]) -> dict[str, Any]:
    """处理数据"""
    print("处理数据中...")
    data = context.get("data", {})
    items = data.get("items", [])

    result = {
        "sum": sum(items),
        "average": sum(items) / len(items) if items else 0,
        "max": max(items) if items else None,
        "min": min(items) if items else None,
        "count": len(items),
    }

    context["result"] = result
    return result


async def validate_result(context: dict[str, Any]) -> str:
    """验证结果"""
    print("验证结果中...")
    result = context.get("result", {})

    # 检查结果是否有效
    if result and result.get("count", 0) > 0:
        print(f"验证通过: 平均值={result['average']:.2f}")
        return "valid"
    else:
        print("验证失败: 无有效数据")
        return "invalid"


async def save_result(context: dict[str, Any]) -> bool:
    """保存结果"""
    print("保存结果中...")
    result = context.get("result", {})

    # 模拟保存操作
    await asyncio.sleep(0.3)
    print(f"结果已保存: {result}")

    return True
