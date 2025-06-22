"""
Graph 管理系统 - 统一管理内存和文件中的图

提供创建、加载、运行、保存和删除图的完整生命周期管理。
"""

import json
import os
from pathlib import Path
from typing import Any

import yaml

from .core import Graph
from .executor import GraphExecutor
from .graph_proxy import GraphProxy
from .graph_validator import GraphValidator
from .config_parser import GraphConfigParser


class GraphFileManager:
    """
    图文件管理器
    
    负责管理文件系统中的 YAML 配置文件。
    """
    
    def __init__(self, base_path: str | Path = "graphs"):
        """
        初始化文件管理器
        
        Args:
            base_path: 图配置文件的基础目录
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self._ensure_schema_file()
    
    def _ensure_schema_file(self) -> None:
        """确保 schema 文件存在"""
        schema_path = self.base_path / "graph-config.schema.json"
        if not schema_path.exists():
            # 这里可以从 schemas 目录复制或生成 schema 文件
            pass
    
    def create(self, name: str, config: dict[str, Any]) -> Path:
        """
        创建新的图配置文件
        
        Args:
            name: 图的名称（不含扩展名）
            config: 图的配置字典
            
        Returns:
            创建的文件路径
        """
        # 确保配置包含必要字段
        if "name" not in config:
            config["name"] = name
        
        # 添加 schema 引用
        config = {
            "$schema": "./graph-config.schema.json",
            **config
        }
        
        # 生成文件路径
        file_path = self.base_path / f"{name}.yaml"
        
        # 检查文件是否已存在
        if file_path.exists():
            raise FileExistsError(f"图配置文件已存在: {file_path}")
        
        # 保存到文件
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, allow_unicode=True, sort_keys=False)
        
        return file_path
    
    def read(self, name: str) -> dict[str, Any]:
        """
        读取图配置
        
        Args:
            name: 图的名称（不含扩展名）
            
        Returns:
            配置字典
        """
        file_path = self.base_path / f"{name}.yaml"
        
        if not file_path.exists():
            raise FileNotFoundError(f"图配置文件不存在: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def update(self, name: str, config: dict[str, Any]) -> None:
        """
        更新图配置
        
        Args:
            name: 图的名称
            config: 新的配置
        """
        file_path = self.base_path / f"{name}.yaml"
        
        if not file_path.exists():
            raise FileNotFoundError(f"图配置文件不存在: {file_path}")
        
        # 保留 schema 引用
        if "$schema" not in config:
            config = {
                "$schema": "./graph-config.schema.json",
                **config
            }
        
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, allow_unicode=True, sort_keys=False)
    
    def delete(self, name: str) -> None:
        """
        删除图配置文件
        
        Args:
            name: 图的名称
        """
        file_path = self.base_path / f"{name}.yaml"
        
        if not file_path.exists():
            raise FileNotFoundError(f"图配置文件不存在: {file_path}")
        
        file_path.unlink()
    
    def list(self) -> list[str]:
        """
        列出所有图配置
        
        Returns:
            图名称列表
        """
        yaml_files = self.base_path.glob("*.yaml")
        return [f.stem for f in yaml_files if f.name != "graph-config.schema.json"]
    
    def exists(self, name: str) -> bool:
        """检查图配置是否存在"""
        return (self.base_path / f"{name}.yaml").exists()


class GraphMemoryManager:
    """
    图内存管理器
    
    负责管理内存中的图实例和执行器。
    """
    
    def __init__(self):
        """初始化内存管理器"""
        self._graphs: dict[str, Graph] = {}
        self._proxies: dict[str, GraphProxy] = {}
        self._executors: dict[str, GraphExecutor] = {}
    
    def load(self, name: str, graph: Graph) -> None:
        """
        加载图到内存
        
        Args:
            name: 图的名称
            graph: Graph 实例
        """
        self._graphs[name] = graph
        self._proxies[name] = GraphProxy(graph, auto_validate=True)
        self._executors[name] = GraphExecutor(graph)
    
    def get_graph(self, name: str) -> Graph | None:
        """获取图实例"""
        return self._graphs.get(name)
    
    def get_proxy(self, name: str) -> GraphProxy | None:
        """获取图代理"""
        return self._proxies.get(name)
    
    def get_executor(self, name: str) -> GraphExecutor | None:
        """获取图执行器"""
        return self._executors.get(name)
    
    def unload(self, name: str) -> None:
        """
        从内存中卸载图
        
        Args:
            name: 图的名称
        """
        self._graphs.pop(name, None)
        self._proxies.pop(name, None)
        self._executors.pop(name, None)
    
    def is_loaded(self, name: str) -> bool:
        """检查图是否已加载"""
        return name in self._graphs
    
    def list_loaded(self) -> list[str]:
        """列出所有已加载的图"""
        return list(self._graphs.keys())
    
    def clear(self) -> None:
        """清空所有内存中的图"""
        self._graphs.clear()
        self._proxies.clear()
        self._executors.clear()


class GraphManager:
    """
    统一的图管理系统
    
    整合文件管理和内存管理，提供完整的图生命周期管理。
    """
    
    def __init__(self, base_path: str | Path = "graphs"):
        """
        初始化图管理器
        
        Args:
            base_path: 图配置文件的基础目录
        """
        self.file_manager = GraphFileManager(base_path)
        self.memory_manager = GraphMemoryManager()
        self.validator = GraphValidator()
    
    def create(
        self,
        name: str,
        description: str = "",
        auto_load: bool = True
    ) -> GraphProxy:
        """
        创建新图
        
        Args:
            name: 图的名称
            description: 图的描述
            auto_load: 是否自动加载到内存
            
        Returns:
            GraphProxy 实例
        """
        # 创建基础配置（使用数组格式的节点，符合 YAML 标准）
        config = {
            "name": name,
            "description": description,
            "start_node": "start",
            "end_nodes": ["end"],
            "nodes": [
                {
                    "id": "start",
                    "type": "TaskNode",
                    "name": "开始节点"
                },
                {
                    "id": "end",
                    "type": "TaskNode", 
                    "name": "结束节点"
                }
            ],
            "edges": [
                {
                    "from": "start",
                    "to": "end"
                }
            ]
        }
        
        # 保存到文件
        self.file_manager.create(name, config)
        
        # 如果需要，加载到内存
        if auto_load:
            return self.load(name)
        
        # 创建临时代理返回
        proxy = GraphProxy.create(name, description)
        proxy.add_node("start", "TaskNode", "开始节点")
        proxy.add_node("end", "TaskNode", "结束节点")
        proxy.add_edge("start", "end")
        proxy.set_start_node("start")
        proxy.add_end_node("end")
        
        return proxy
    
    def load(self, name: str) -> GraphProxy:
        """
        加载图到内存
        
        Args:
            name: 图的名称
            
        Returns:
            GraphProxy 实例
        """
        # 如果已经加载，直接返回
        if self.memory_manager.is_loaded(name):
            proxy = self.memory_manager.get_proxy(name)
            if proxy:
                return proxy
        
        # 从文件读取配置
        config = self.file_manager.read(name)
        
        # 使用 GraphConfigParser 解析配置
        parser = GraphConfigParser()
        graph = parser.parse_config(config)
        
        # 创建图代理
        proxy = GraphProxy(graph, auto_validate=True)
        
        # 验证图结构
        valid, errors = proxy.validate()
        if not valid:
            raise ValueError(f"图结构无效: {'; '.join(errors)}")
        
        # 加载到内存
        self.memory_manager.load(name, proxy.graph)
        
        return proxy
    
    def save(self, name: str) -> None:
        """
        保存内存中的图到文件
        
        Args:
            name: 图的名称
        """
        proxy = self.memory_manager.get_proxy(name)
        if not proxy:
            raise ValueError(f"图 '{name}' 未加载到内存")
        
        # 导出配置
        config = proxy.to_dict()
        
        # 转换节点格式：从字典转为数组
        if "nodes" in config and isinstance(config["nodes"], dict):
            nodes_list = []
            for node_id, node_data in config["nodes"].items():
                node_info = {
                    "id": node_id,
                    "type": node_data.get("type", "TaskNode"),
                    "name": node_data.get("name", node_id),
                }
                if "metadata" in node_data:
                    node_info["params"] = node_data["metadata"]
                nodes_list.append(node_info)
            config["nodes"] = nodes_list
        
        # 保存到文件
        self.file_manager.update(name, config)
    
    def delete(self, name: str, force: bool = False) -> None:
        """
        删除图
        
        Args:
            name: 图的名称
            force: 是否强制删除（即使已加载）
        """
        # 检查是否已加载
        if self.memory_manager.is_loaded(name) and not force:
            raise RuntimeError(f"图 '{name}' 正在使用中，请先卸载或使用 force=True")
        
        # 从内存中卸载
        self.memory_manager.unload(name)
        
        # 删除文件
        self.file_manager.delete(name)
    
    async def run(
        self,
        name: str,
        input_data: Any = None,
        auto_load: bool = True
    ) -> Any:
        """
        运行图
        
        Args:
            name: 图的名称
            input_data: 输入数据
            auto_load: 如果未加载，是否自动加载
            
        Returns:
            执行结果
        """
        # 确保图已加载
        if not self.memory_manager.is_loaded(name):
            if auto_load:
                self.load(name)
            else:
                raise ValueError(f"图 '{name}' 未加载到内存")
        
        # 获取执行器
        executor = self.memory_manager.get_executor(name)
        if not executor:
            raise RuntimeError(f"无法获取图 '{name}' 的执行器")
        
        # 执行图（注意参数顺序）
        context = await executor.execute(start_node_id=None, initial_input=input_data)
        # 返回最后执行的节点的结果
        return context.data.get("final_result", input_data)
    
    def list_all(self) -> dict[str, dict[str, Any]]:
        """
        列出所有图的信息
        
        Returns:
            图信息字典
        """
        all_graphs = {}
        
        # 获取文件中的图
        for name in self.file_manager.list():
            all_graphs[name] = {
                "in_file": True,
                "in_memory": self.memory_manager.is_loaded(name),
                "status": "loaded" if self.memory_manager.is_loaded(name) else "unloaded"
            }
        
        return all_graphs
    
    def get_proxy(self, name: str) -> GraphProxy | None:
        """
        获取图代理（用于动态修改）
        
        Args:
            name: 图的名称
            
        Returns:
            GraphProxy 实例或 None
        """
        return self.memory_manager.get_proxy(name)
    
    def unload(self, name: str) -> None:
        """
        从内存中卸载图
        
        Args:
            name: 图的名称
        """
        self.memory_manager.unload(name)
    
    def sync(self, name: str) -> None:
        """
        同步内存和文件（双向）
        
        Args:
            name: 图的名称
        """
        if self.memory_manager.is_loaded(name):
            # 内存 -> 文件
            self.save(name)
        elif self.file_manager.exists(name):
            # 文件 -> 内存
            self.load(name)
        else:
            raise ValueError(f"图 '{name}' 不存在")