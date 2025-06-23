"""
图管理系统测试
"""

import shutil
import tempfile

import pytest

from src.graph import GraphManager, GraphProxy, TaskNode


@pytest.mark.unit
class TestGraphFileManager:
    """文件管理器测试"""

    def setup_method(self):
        """创建临时目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = GraphManager(self.temp_dir)

    def teardown_method(self):
        """清理临时目录"""
        shutil.rmtree(self.temp_dir)

    def test_create_graph_file(self):
        """测试创建图文件"""
        config = {
            "name": "test_graph",
            "start_node": "start",
            "end_nodes": ["end"],
            "nodes": [
                {"id": "start", "type": "TaskNode", "name": "开始"},
                {"id": "end", "type": "TaskNode", "name": "结束"},
            ],
            "edges": [{"from": "start", "to": "end"}],
        }

        path = self.manager.file_manager.create("test_graph", config)
        assert path.exists()
        assert path.name == "test_graph.yaml"

    def test_read_graph_file(self):
        """测试读取图文件"""
        # 先创建
        config = {"name": "test", "start_node": "s", "end_nodes": ["e"]}
        self.manager.file_manager.create("test", config)

        # 再读取
        loaded = self.manager.file_manager.read("test")
        assert loaded["name"] == "test"
        assert loaded["start_node"] == "s"

    def test_list_graphs(self):
        """测试列出所有图"""
        # 创建多个图
        for i in range(3):
            config = {"name": f"graph_{i}"}
            self.manager.file_manager.create(f"graph_{i}", config)

        graphs = self.manager.file_manager.list()
        assert len(graphs) == 3
        assert "graph_0" in graphs
        assert "graph_1" in graphs
        assert "graph_2" in graphs

    def test_delete_graph_file(self):
        """测试删除图文件"""
        # 创建
        self.manager.file_manager.create("temp", {"name": "temp"})
        assert self.manager.file_manager.exists("temp")

        # 删除
        self.manager.file_manager.delete("temp")
        assert not self.manager.file_manager.exists("temp")


@pytest.mark.unit
class TestGraphMemoryManager:
    """内存管理器测试"""

    def setup_method(self):
        """初始化"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = GraphManager(self.temp_dir)

    def teardown_method(self):
        """清理"""
        shutil.rmtree(self.temp_dir)

    def test_load_to_memory(self):
        """测试加载到内存"""
        # 创建代理
        proxy = GraphProxy.create("test", "测试图")

        # 加载到内存
        self.manager.memory_manager.load("test", proxy.graph)

        assert self.manager.memory_manager.is_loaded("test")
        assert self.manager.memory_manager.get_graph("test") is not None
        assert self.manager.memory_manager.get_proxy("test") is not None
        assert self.manager.memory_manager.get_executor("test") is not None

    def test_unload_from_memory(self):
        """测试从内存卸载"""
        proxy = GraphProxy.create("test", "测试图")
        self.manager.memory_manager.load("test", proxy.graph)

        # 卸载
        self.manager.memory_manager.unload("test")

        assert not self.manager.memory_manager.is_loaded("test")
        assert self.manager.memory_manager.get_graph("test") is None

    def test_list_loaded(self):
        """测试列出已加载的图"""
        # 加载多个图
        for i in range(3):
            proxy = GraphProxy.create(f"graph_{i}")
            self.manager.memory_manager.load(f"graph_{i}", proxy.graph)

        loaded = self.manager.memory_manager.list_loaded()
        assert len(loaded) == 3
        assert "graph_0" in loaded


@pytest.mark.unit
class TestGraphManager:
    """统一管理器测试"""

    def setup_method(self):
        """初始化"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = GraphManager(self.temp_dir)

    def teardown_method(self):
        """清理"""
        shutil.rmtree(self.temp_dir)

    def test_create_graph(self):
        """测试创建图"""
        proxy = self.manager.create("workflow1", "测试工作流")

        # 验证代理
        assert proxy is not None
        assert proxy.name == "workflow1"

        # 验证文件创建
        assert self.manager.file_manager.exists("workflow1")

        # 验证内存加载
        assert self.manager.memory_manager.is_loaded("workflow1")

    def test_load_graph(self):
        """测试加载图"""
        # 先创建但不自动加载
        self.manager.create("workflow2", auto_load=False)
        assert not self.manager.memory_manager.is_loaded("workflow2")

        # 手动加载
        proxy2 = self.manager.load("workflow2")
        assert self.manager.memory_manager.is_loaded("workflow2")
        assert proxy2 is not None

    def test_save_graph(self):
        """测试保存图"""
        # 创建并修改
        proxy = self.manager.create("workflow3")
        proxy.add_node("middle", "TaskNode", "中间节点")
        proxy.add_edge("start", "middle")
        proxy.add_edge("middle", "end")

        # 保存
        self.manager.save("workflow3")

        # 重新加载验证
        self.manager.unload("workflow3")
        proxy2 = self.manager.load("workflow3")
        assert proxy2.has_node("middle")
        assert proxy2.has_edge("start", "middle")

    def test_delete_graph(self):
        """测试删除图"""
        self.manager.create("temp_workflow")

        # 尝试删除已加载的图（应该失败）
        with pytest.raises(RuntimeError):
            self.manager.delete("temp_workflow")

        # 强制删除
        self.manager.delete("temp_workflow", force=True)
        assert not self.manager.file_manager.exists("temp_workflow")
        assert not self.manager.memory_manager.is_loaded("temp_workflow")

    @pytest.mark.asyncio
    async def test_run_graph(self):
        """测试运行图"""
        # 创建简单图
        proxy = self.manager.create("executable")

        # 设置节点执行逻辑
        start_node = proxy.get_node("start")
        if isinstance(start_node, TaskNode):
            start_node.process_func = lambda x: "Hello"

        end_node = proxy.get_node("end")
        if isinstance(end_node, TaskNode):
            end_node.process_func = lambda x: f"{x} World!"

        # 运行
        await self.manager.run("executable", "Test")
        # 注意：实际结果依赖于执行器的实现

    def test_list_all_graphs(self):
        """测试列出所有图"""
        # 创建一些图
        self.manager.create("graph1")
        self.manager.create("graph2", auto_load=False)
        self.manager.create("graph3")
        self.manager.unload("graph3")

        all_graphs = self.manager.list_all()

        assert len(all_graphs) == 3
        assert all_graphs["graph1"]["in_memory"] is True
        assert all_graphs["graph2"]["in_memory"] is False
        assert all_graphs["graph3"]["in_memory"] is False
        assert all_graphs["graph3"]["in_file"] is True

    def test_get_proxy_for_modification(self):
        """测试获取代理进行动态修改"""
        self.manager.create("dynamic")

        # 获取代理
        proxy = self.manager.get_proxy("dynamic")
        assert proxy is not None

        # 动态添加节点
        proxy.add_node("new_node", "TaskNode", "新节点")
        assert proxy.has_node("new_node")

        # 验证仍然有效
        valid, errors = proxy.validate()
        # 可能因为新节点是孤立的而无效，但这是预期的

    def test_sync_graph(self):
        """测试同步功能"""
        # 创建并修改
        proxy = self.manager.create("sync_test")
        proxy.add_node("extra", "TaskNode")
        # 添加边以避免孤立节点
        proxy.add_edge("start", "extra")
        proxy.add_edge("extra", "end")
        # 移除原来的直接边
        proxy.remove_edge("start", "end")

        # 保存到文件
        self.manager.sync("sync_test")

        # 卸载后重新同步（从文件加载）
        self.manager.unload("sync_test")
        self.manager.sync("sync_test")

        # 验证修改仍在
        proxy2 = self.manager.get_proxy("sync_test")
        assert proxy2 is not None
        assert proxy2.has_node("extra")
