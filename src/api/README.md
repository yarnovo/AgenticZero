# AgenticZero API

AgenticZero API 提供了一个完整的会话管理和聊天接口，支持创建、管理和与 AI Agent 进行交互。

## 功能特性

- 🔄 **会话管理**：创建、删除、更新和列出会话
- 💬 **聊天接口**：支持流式和非流式响应
- 📁 **持久化存储**：会话数据同时保存在内存和文件系统中
- 🛠️ **自定义配置**：支持自定义 Agent 设置和路径
- 🌐 **CORS 支持**：支持跨域请求

## API 端点

### 会话管理

#### 创建会话
```
POST /api/v1/sessions/
```

请求体：
```json
{
  "session_id": "unique-session-id",
  "name": "会话名称",
  "description": "会话描述",
  "llm_provider": "openai",
  "llm_settings": {
    "model": "gpt-4",
    "temperature": 0.7
  },
  "agent_settings": {
    "tools": ["python", "browser"]
  }
}
```

#### 列出会话
```
GET /api/v1/sessions/?source=all
```

参数：
- `source`: `memory` | `file` | `all` (默认: `all`)

#### 获取会话信息
```
GET /api/v1/sessions/{session_id}
```

#### 更新会话
```
PUT /api/v1/sessions/{session_id}
```

请求体：
```json
{
  "name": "新名称",
  "description": "新描述",
  "metadata": {
    "key": "value"
  }
}
```

#### 删除会话
```
DELETE /api/v1/sessions/{session_id}
```

### 聊天接口

#### 发送消息（支持流式响应）
```
POST /api/v1/chat/completions
```

请求体：
```json
{
  "session_id": "unique-session-id",
  "message": "你好，请帮我写一个 Python 脚本",
  "stream": true,
  "max_iterations": 10
}
```

#### 简化的消息接口
```
POST /api/v1/chat/{session_id}/messages?message=你好&stream=true
```

### 其他端点

#### 健康检查
```
GET /health
GET /api/v1/chat/health
```

#### API 文档
```
GET /docs        # Swagger UI
GET /redoc       # ReDoc
```

## 流式响应

流式响应使用 Server-Sent Events (SSE) 格式，直接使用 Agent 的原生 `run_stream` 方法，支持以下响应类型：

### 响应类型

1. **content** - 内容片段
   ```json
   {"type": "content", "content": "这是响应的一部分..."}
   ```

2. **tool_call** - 工具调用
   ```json
   {"type": "tool_call", "tool": "python_execute", "arguments": {"code": "print('hello')"}}
   ```

3. **tool_result** - 工具执行结果
   ```json
   {"type": "tool_result", "tool": "python_execute", "success": true, "result": "hello"}
   ```

4. **iteration** - 自驱动迭代信息
   ```json
   {"type": "iteration", "current": 2, "max": 10}
   ```

5. **complete** - 完成标记
   ```json
   {"type": "complete", "final_response": "完整响应内容", "iterations": 3}
   ```

6. **error** - 错误信息
   ```json
   {"type": "error", "error": "错误描述"}
   ```

### 前端示例代码

```javascript
// 前端示例代码
const response = await fetch('/api/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    session_id: 'my-session',
    message: '请用 Python 计算 2+2 并解释结果',
    stream: true
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const dataStr = line.slice(6);
      if (dataStr === '[DONE]') {
        console.log('流结束');
        break;
      }
      
      try {
        const data = JSON.parse(dataStr);
        
        switch (data.type) {
          case 'content':
            // 实时显示内容
            console.log(data.content);
            break;
          case 'tool_call':
            // 显示工具调用
            console.log(`🔧 调用工具: ${data.tool}`);
            break;
          case 'tool_result':
            // 显示工具结果
            console.log(`✅ 工具结果: ${data.result}`);
            break;
          case 'iteration':
            // 显示迭代进度
            console.log(`🔄 迭代 ${data.current}/${data.max}`);
            break;
          case 'complete':
            // 完成
            console.log(`✨ 完成 (共${data.iterations}次迭代)`);
            break;
          case 'error':
            // 错误
            console.error(`❌ 错误: ${data.error}`);
            break;
        }
      } catch (e) {
        // 忽略JSON解析错误
      }
    }
  }
}
```

## 文件系统结构

每个会话在文件系统中的结构：

```
sessions/
└── {session_id}/
    ├── session_config.json    # 会话配置
    ├── memory/                # 记忆存储
    ├── mcp/                   # MCP 服务数据
    ├── graphs/                # 图数据
    └── logs/                  # 日志文件
```

## 环境配置

确保设置了必要的环境变量：

```bash
# OpenAI
export OPENAI_API_KEY=your-api-key

# Anthropic
export ANTHROPIC_API_KEY=your-api-key

# 其他 LLM 提供商...
```

## 启动服务

```bash
# 生产模式
make api

# 开发模式（带自动重载）
make api-dev
```

服务将在 `http://localhost:8000` 启动。

## 测试 API

提供了测试脚本来验证 API 功能：

```bash
# 设置环境变量（可选，用于测试聊天功能）
export OPENAI_API_KEY=your-api-key

# 启动 API 服务器
make api-dev

# 在另一个终端运行测试
uv run python test_api.py
```

测试脚本会验证：
- 根端点和健康检查
- 会话创建和列表
- 非流式聊天（如果有 API key）
- 流式聊天（如果有 API key）

## 注意事项

1. **流式响应支持**：现在使用 Agent 的原生 `run_stream` 方法，支持真正的流式响应，包括内容、工具调用、工具结果等。

2. **会话持久化**：
   - 会话配置保存到文件系统
   - Agent 实例在内存中，重启服务后需要重新加载
   - 每个会话有独立的存储目录

3. **并发限制**：每个会话同时只能处理一个请求。如需并发处理，请创建多个会话。

4. **安全性**：在生产环境中，请：
   - 设置具体的 CORS 源，而不是使用 `*`
   - 添加认证和授权机制
   - 限制会话创建频率
   - 设置合理的超时时间
   - 验证用户输入和参数