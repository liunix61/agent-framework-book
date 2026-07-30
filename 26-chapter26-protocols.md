# 第26章：Agent 协议栈实现

## 本章目标

通过实战项目，掌握 Agent 协议栈的实现方法。

## 前置知识

- **基础 协议**: HTTP、WebSocket、JSON
- **基础 Agent**: Harness、Loop、Graph
- **基础 项目**: 项目结构、代码组织

## 26.1 A2A 协议实现

### 26.1.1 A2A 协议设计

**1. A2A 协议概述**

**A2A 协议**（Agent-to-Agent Protocol）是 Agent 之间的通信协议，定义了 Agent 之间的通信格式和规则。

**2. A2A 协议结构**

```json
{
  "protocol": "A2A",
  "version": "1.0.0",
  "message_type": "request",
  "sender_agent": {
    "agent_id": "agent_1",
    "agent_name": "Agent 1",
    "agent_version": "1.0.0"
  },
  "receiver_agent": {
    "agent_id": "agent_2",
    "agent_name": "Agent 2",
    "agent_version": "1.0.0"
  },
  "message_id": "msg_1234567890",
  "timestamp": "2026-07-28T12:00:00Z",
  "payload": {
    "task": "写一首关于春天的诗",
    "context": {
      "language": "中文",
      "style": "诗歌"
    }
  }
}
```

**3. A2A 协议消息类型**

| 消息类型 | 说明 | 用途 |
|---------|------|------|
| **request** | 请求消息 | Agent 请求其他 Agent 执行任务 |
| **response** | 响应消息 | Agent 响应其他 Agent 的请求 |
| **notification** | 通知消息 | Agent 通知其他 Agent 状态变化 |
| **error** | 错误消息 | Agent 报告错误 |

### 26.1.2 A2A 协议实现

**1. A2A 消息类**

```python
# a2a_protocol/message.py
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

class A2AMessage:
    """A2A 消息"""

    def __init__(
        self,
        message_type: str,
        sender_agent: Dict[str, Any],
        receiver_agent: Dict[str, Any],
        payload: Dict[str, Any],
        message_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        初始化 A2A 消息

        Args:
            message_type: 消息类型（request/response/notification/error）
            sender_agent: 发送者 Agent 信息
            receiver_agent: 接收者 Agent 信息
            payload: 消息载荷
            message_id: 消息 ID
            timestamp: 时间戳
        """
        self.message_type = message_type
        self.sender_agent = sender_agent
        self.receiver_agent = receiver_agent
        self.payload = payload
        self.message_id = message_id or str(uuid.uuid4())
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "protocol": "A2A",
            "version": "1.0.0",
            "message_type": self.message_type,
            "sender_agent": self.sender_agent,
            "receiver_agent": self.receiver_agent,
            "message_id": self.message_id,
            "timestamp": self.timestamp.isoformat(),
            "payload": self.payload
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2AMessage':
        """从字典创建"""
        return cls(
            message_type=data["message_type"],
            sender_agent=data["sender_agent"],
            receiver_agent=data["receiver_agent"],
            payload=data["payload"],
            message_id=data.get("message_id"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None
        )


# 使用
message = A2AMessage(
    message_type="request",
    sender_agent={
        "agent_id": "agent_1",
        "agent_name": "Agent 1",
        "agent_version": "1.0.0"
    },
    receiver_agent={
        "agent_id": "agent_2",
        "agent_name": "Agent 2",
        "agent_version": "1.0.0"
    },
    payload={
        "task": "写一首关于春天的诗",
        "context": {
            "language": "中文",
            "style": "诗歌"
        }
    }
)

print(message.to_dict())
```

**2. A2A 通信器**

```python
# a2a_protocol/communicator.py
import asyncio
from typing import Dict, Any, Callable, Optional
import json

class A2ACommunicator:
    """A2A 通信器"""

    def __init__(self, agent_id: str, agent_name: str, agent_version: str):
        """
        初始化 A2A 通信器

        Args:
            agent_id: Agent ID
            agent_name: Agent 名称
            agent_version: Agent 版本
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.agent_version = agent_version

        # Agent 信息
        self.agent_info = {
            "agent_id": agent_id,
            "agent_name": agent_name,
            "agent_version": agent_version
        }

        # 消息处理器
        self.message_handlers: Dict[str, Callable] = {}

        # 通信通道
        self.communication_channels: Dict[str, asyncio.Queue] = {}

    def register_message_handler(
        self,
        message_type: str,
        handler: Callable
    ):
        """
        注册消息处理器

        Args:
            message_type: 消息类型
            handler: 处理函数
        """
        self.message_handlers[message_type] = handler

    async def send_message(
        self,
        receiver_agent_id: str,
        message_type: str,
        payload: Dict[str, Any]
    ) -> A2AMessage:
        """
        发送消息

        Args:
            receiver_agent_id: 接收者 Agent ID
            message_type: 消息类型
            payload: 消息载荷

        Returns:
            响应消息
        """
        # 创建消息
        message = A2AMessage(
            message_type=message_type,
            sender_agent=self.agent_info,
            receiver_agent={
                "agent_id": receiver_agent_id,
                "agent_name": "Unknown",
                "agent_version": "1.0.0"
            },
            payload=payload
        )

        # 发送到通信通道
        if receiver_agent_id not in self.communication_channels:
            self.communication_channels[receiver_agent_id] = asyncio.Queue()

        queue = self.communication_channels[receiver_agent_id]
        await queue.put(message)

        # 等待响应
        response = await queue.get()

        return response

    async def receive_message(self) -> A2AMessage:
        """
        接收消息

        Returns:
            消息
        """
        # 从任意通信通道获取消息
        for queue in self.communication_channels.values():
            if not queue.empty():
                return await queue.get()

        return None

    async def handle_message(self, message: A2AMessage) -> A2AMessage:
        """
        处理消息

        Args:
            message: 消息

        Returns:
            响应消息
        """
        # 查找消息处理器
        handler = self.message_handlers.get(message.message_type)

        if handler is None:
            # 返回错误消息
            return A2AMessage(
                message_type="error",
                sender_agent=self.agent_info,
                receiver_agent=message.sender_agent,
                payload={
                    "error": f"未知的消息类型：{message.message_type}"
                }
            )

        # 执行处理器
        try:
            result = await handler(message.payload)
            return A2AMessage(
                message_type="response",
                sender_agent=self.agent_info,
                receiver_agent=message.sender_agent,
                payload={
                    "result": result
                }
            )
        except Exception as e:
            # 返回错误消息
            return A2AMessage(
                message_type="error",
                sender_agent=self.agent_info,
                receiver_agent=message.sender_agent,
                payload={
                    "error": str(e)
                }
            )


# 使用
async def main():
    """主函数"""
    # 创建通信器
    communicator = A2ACommunicator(
        agent_id="agent_1",
        agent_name="Agent 1",
        agent_version="1.0.0"
    )

    # 注册消息处理器
    @communicator.register_message_handler("request")
    async def handle_request(payload: dict):
        """处理请求"""
        return f"收到请求：{payload['task']}"

    # 创建接收者通信器
    receiver_communicator = A2ACommunicator(
        agent_id="agent_2",
        agent_name="Agent 2",
        agent_version="1.0.0"
    )

    @receiver_communicator.register_message_handler("request")
    async def handle_request(payload: dict):
        """处理请求"""
        return f"收到请求：{payload['task']}"

    # 创建通信任务
    async def send_task():
        """发送任务"""
        # 发送消息
        response = await communicator.send_message(
            receiver_agent_id="agent_2",
            message_type="request",
            payload={
                "task": "写一首关于春天的诗"
            }
        )

        print(f"响应：{response.payload}")

    # 创建接收任务
    async def receive_task():
        """接收任务"""
        while True:
            # 接收消息
            message = await receiver_communicator.receive_message()

            if message is None:
                continue

            # 处理消息
            response = await receiver_communicator.handle_message(message)

            # 发送响应
            await communicator.send_message(
                receiver_agent_id="agent_1",
                message_type="response",
                payload=response.payload
            )

    # 并发执行
    await asyncio.gather(send_task(), receive_task())


asyncio.run(main())
```

**3. A2A 协议服务器**

```python
# a2a_protocol/server.py
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import json

app = FastAPI(
    title="A2A 协议服务器",
    version="1.0.0",
    description="Agent-to-Agent 协议服务器"
)

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# A2A 通信器
communicator = A2ACommunicator(
    agent_id="agent_1",
    agent_name="Agent 1",
    agent_version="1.0.0"
)


@app.post("/a2a/message")
async def receive_message(message: dict):
    """
    接收 A2A 消息

    Args:
        message: A2A 消息

    Returns:
        响应消息
    """
    try:
        # 解析消息
        a2a_message = A2AMessage.from_dict(message)

        # 处理消息
        response = await communicator.handle_message(a2a_message)

        return response.to_dict()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/a2a/status")
async def get_status():
    """获取状态"""
    return {
        "agent_id": communicator.agent_id,
        "agent_name": communicator.agent_name,
        "agent_version": communicator.agent_version,
        "message_handlers": list(communicator.message_handlers.keys())
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

## 26.2 MCP 协议实现

### 26.2.1 MCP 协议设计

**1. MCP 协议概述**

**MCP 协议**（Model Context Protocol）是模型上下文协议，定义了 Agent 与模型之间的通信格式和规则。

**2. MCP 协议结构**

```json
{
  "protocol": "MCP",
  "version": "1.0.0",
  "message_type": "request",
  "model": {
    "model_id": "gpt-4",
    "model_name": "GPT-4",
    "model_version": "1.0.0"
  },
  "agent": {
    "agent_id": "agent_1",
    "agent_name": "Agent 1",
    "agent_version": "1.0.0"
  },
  "message_id": "msg_1234567890",
  "timestamp": "2026-07-28T12:00:00Z",
  "payload": {
    "prompt": "写一首关于春天的诗",
    "parameters": {
      "temperature": 0.7,
      "max_tokens": 1000
    }
  }
}
```

**3. MCP 协议消息类型**

| 消息类型 | 说明 | 用途 |
|---------|------|------|
| **request** | 请求消息 | Agent 请求模型生成内容 |
| **response** | 响应消息 | 模型响应 Agent 的请求 |
| **error** | 错误消息 | 模型报告错误 |

### 26.2.2 MCP 协议实现

**1. MCP 消息类**

```python
# mcp_protocol/message.py
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

class MCPMessage:
    """MCP 消息"""

    def __init__(
        self,
        message_type: str,
        model: Dict[str, Any],
        agent: Dict[str, Any],
        payload: Dict[str, Any],
        message_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        初始化 MCP 消息

        Args:
            message_type: 消息类型（request/response/error）
            model: 模型信息
            agent: Agent 信息
            payload: 消息载荷
            message_id: 消息 ID
            timestamp: 时间戳
        """
        self.message_type = message_type
        self.model = model
        self.agent = agent
        self.payload = payload
        self.message_id = message_id or str(uuid.uuid4())
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "protocol": "MCP",
            "version": "1.0.0",
            "message_type": self.message_type,
            "model": self.model,
            "agent": self.agent,
            "message_id": self.message_id,
            "timestamp": self.timestamp.isoformat(),
            "payload": self.payload
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPMessage':
        """从字典创建"""
        return cls(
            message_type=data["message_type"],
            model=data["model"],
            agent=data["agent"],
            payload=data["payload"],
            message_id=data.get("message_id"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None
        )


# 使用
message = MCPMessage(
    message_type="request",
    model={
        "model_id": "gpt-4",
        "model_name": "GPT-4",
        "model_version": "1.0.0"
    },
    agent={
        "agent_id": "agent_1",
        "agent_name": "Agent 1",
        "agent_version": "1.0.0"
    },
    payload={
        "prompt": "写一首关于春天的诗",
        "parameters": {
            "temperature": 0.7,
            "max_tokens": 1000
        }
    }
)

print(message.to_dict())
```

**2. MCP 客户端**

```python
# mcp_protocol/client.py
import asyncio
from typing import Dict, Any, Optional
import json

class MCPClient:
    """MCP 客户端"""

    def __init__(self, model_id: str, model_name: str, model_version: str):
        """
        初始化 MCP 客户端

        Args:
            model_id: 模型 ID
            model_name: 模型名称
            model_version: 模型版本
        """
        self.model_id = model_id
        self.model_name = model_name
        self.model_version = model_version

        # 模型信息
        self.model_info = {
            "model_id": model_id,
            "model_name": model_name,
            "model_version": model_version
        }

        # Agent 信息
        self.agent_info = {
            "agent_id": "agent_1",
            "agent_name": "Agent 1",
            "agent_version": "1.0.0"
        }

    async def generate(
        self,
        prompt: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        生成内容

        Args:
            prompt: 提示
            parameters: 参数

        Returns:
            生成的内容
        """
        # 创建请求消息
        request = MCPMessage(
            message_type="request",
            model=self.model_info,
            agent=self.agent_info,
            payload={
                "prompt": prompt,
                "parameters": parameters or {}
            }
        )

        # 发送到模型 API
        response = await self._call_model_api(request)

        # 返回生成的内容
        return response.payload.get("content", "")

    async def _call_model_api(self, request: MCPMessage) -> MCPMessage:
        """
        调用模型 API

        Args:
            request: 请求消息

        Returns:
            响应消息
        """
        # 模拟调用模型 API
        await asyncio.sleep(1)

        # 返回响应
        return MCPMessage(
            message_type="response",
            model=self.model_info,
            agent=self.agent_info,
            payload={
                "content": f"模型生成的内容：{request.payload['prompt']}"
            }
        )


# 使用
async def main():
    """主函数"""
    # 创建 MCP 客户端
    client = MCPClient(
        model_id="gpt-4",
        model_name="GPT-4",
        model_version="1.0.0"
    )

    # 生成内容
    content = await client.generate(
        prompt="写一首关于春天的诗",
        parameters={
            "temperature": 0.7,
            "max_tokens": 1000
        }
    )

    print(f"生成内容：{content}")


asyncio.run(main())
```

## 26.3 OKF 协议实现

### 26.3.1 OKF 协议设计

**1. OKF 协议概述**

**OKF 协议**（Open Knowledge Framework）是开放知识框架，定义了 Agent 知识的存储、检索和共享机制。

**2. OKF 协议结构**

```json
{
  "protocol": "OKF",
  "version": "1.0.0",
  "message_type": "request",
  "knowledge_type": "knowledge_graph",
  "knowledge_id": "kg_1234567890",
  "timestamp": "2026-07-28T12:00:00Z",
  "payload": {
    "operation": "retrieve",
    "parameters": {
      "query": "AI Agent",
      "limit": 10
    }
  }
}
```

**3. OKF 协议消息类型**

| 消息类型 | 说明 | 用途 |
|---------|------|------|
| **request** | 请求消息 | Agent 请求知识 |
| **response** | 响应消息 | Agent 响应知识请求 |
| **notification** | 通知消息 | Agent 通知知识变化 |

### 26.3.2 OKF 协议实现

**1. OKF 知识管理器**

```python
# okf_protocol/knowledge_manager.py
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

class OKFKnowledgeManager:
    """OKF 知识管理器"""

    def __init__(self, knowledge_type: str):
        """
        初始化知识管理器

        Args:
            knowledge_type: 知识类型（knowledge_graph、knowledge_base、knowledge_base）
        """
        self.knowledge_type = knowledge_type
        self.knowledge_base: Dict[str, Any] = {}

    def add_knowledge(self, knowledge_id: str, knowledge: Dict[str, Any]):
        """
        添加知识

        Args:
            knowledge_id: 知识 ID
            knowledge: 知识内容
        """
        self.knowledge_base[knowledge_id] = {
            "knowledge_id": knowledge_id,
            "knowledge": knowledge,
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_knowledge(self, knowledge_id: str) -> Optional[Dict[str, Any]]:
        """
        获取知识

        Args:
            knowledge_id: 知识 ID

        Returns:
            知识
        """
        return self.knowledge_base.get(knowledge_id)

    def search_knowledge(
        self,
        query: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索知识

        Args:
            query: 查询
            limit: 限制数量

        Returns:
            知识列表
        """
        results = []

        for knowledge_id, knowledge_data in self.knowledge_base.items():
            knowledge = knowledge_data["knowledge"]

            # 简单的关键词匹配
            if query.lower() in json.dumps(knowledge).lower():
                results.append(knowledge_data)

                # 达到限制数量时停止
                if limit and len(results) >= limit:
                    break

        return results

    def delete_knowledge(self, knowledge_id: str):
        """
        删除知识

        Args:
            knowledge_id: 知识 ID
        """
        if knowledge_id in self.knowledge_base:
            del self.knowledge_base[knowledge_id]

    def list_knowledge(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        列出知识

        Args:
            limit: 限制数量

        Returns:
            知识列表
        """
        knowledge_list = list(self.knowledge_base.values())

        # 按时间戳排序
        knowledge_list.sort(key=lambda x: x["timestamp"], reverse=True)

        # 达到限制数量时停止
        if limit:
            knowledge_list = knowledge_list[:limit]

        return knowledge_list


# 使用
manager = OKFKnowledgeManager(knowledge_type="knowledge_graph")

# 添加知识
manager.add_knowledge(
    knowledge_id="kg_1",
    knowledge={
        "name": "AI Agent",
        "description": "AI Agent 是一种能够自主执行任务的 AI 系统",
        "type": "概念",
        "keywords": ["AI", "Agent", "自主"]
    }
)

manager.add_knowledge(
    knowledge_id="kg_2",
    knowledge={
        "name": "LLM",
        "description": "LLM 是一种大语言模型",
        "type": "概念",
        "keywords": ["AI", "语言模型", "大语言模型"]
    }
)

# 搜索知识
results = manager.search_knowledge("AI", limit=10)

for result in results:
    print(f"知识 ID：{result['knowledge_id']}")
    print(f"知识：{result['knowledge']}")
    print()

# 列出知识
knowledge_list = manager.list_knowledge(limit=10)

for knowledge in knowledge_list:
    print(f"知识 ID：{knowledge['knowledge_id']}")
    print(f"知识：{knowledge['knowledge']}")
    print()
```

**2. OKF 协议处理器**

```python
# okf_protocol/handler.py
from typing import Dict, Any, Optional
import json

class OKFHandler:
    """OKF 协议处理器"""

    def __init__(self, knowledge_manager: OKFKnowledgeManager):
        """
        初始化处理器

        Args:
            knowledge_manager: 知识管理器
        """
        self.knowledge_manager = knowledge_manager

    def handle_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理请求

        Args:
            payload: 载荷

        Returns:
            响应
        """
        operation = payload.get("operation")

        if operation == "retrieve":
            return self._handle_retrieve(payload)
        elif operation == "add":
            return self._handle_add(payload)
        elif operation == "delete":
            return self._handle_delete(payload)
        elif operation == "list":
            return self._handle_list(payload)
        else:
            return {
                "status": "error",
                "error": f"未知的操作：{operation}"
            }

    def _handle_retrieve(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理检索"""
        query = payload.get("parameters", {}).get("query", "")
        limit = payload.get("parameters", {}).get("limit")

        results = self.knowledge_manager.search_knowledge(query, limit)

        return {
            "status": "success",
            "results": results,
            "count": len(results)
        }

    def _handle_add(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理添加"""
        knowledge = payload.get("knowledge")

        if knowledge is None:
            return {
                "status": "error",
                "error": "知识内容不能为空"
            }

        # 生成知识 ID
        knowledge_id = f"kg_{int(datetime.utcnow().timestamp())}"

        # 添加知识
        self.knowledge_manager.add_knowledge(knowledge_id, knowledge)

        return {
            "status": "success",
            "knowledge_id": knowledge_id
        }

    def _handle_delete(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理删除"""
        knowledge_id = payload.get("knowledge_id")

        if knowledge_id is None:
            return {
                "status": "error",
                "error": "知识 ID 不能为空"
            }

        # 删除知识
        self.knowledge_manager.delete_knowledge(knowledge_id)

        return {
            "status": "success"
        }

    def _handle_list(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理列表"""
        limit = payload.get("parameters", {}).get("limit")

        knowledge_list = self.knowledge_manager.list_knowledge(limit)

        return {
            "status": "success",
            "knowledge_list": knowledge_list,
            "count": len(knowledge_list)
        }


# 使用
manager = OKFKnowledgeManager(knowledge_type="knowledge_graph")
handler = OKFHandler(manager)

# 处理请求
payload = {
    "operation": "retrieve",
    "parameters": {
        "query": "AI",
        "limit": 10
    }
}

response = handler.handle_request(payload)

print(f"响应：{response}")
```

## 26.4 本章总结

### 核心要点

1. **A2A 协议实现**: A2A 消息类、A2A 通信器、A2A 协议服务器
2. **MCP 协议实现**: MCP 消息类、MCP 客户端
3. **OKF 协议实现**: OKF 知识管理器、OKF 协议处理器

### 实战技巧

- **A2A 协议**: 定义 Agent 之间的通信格式、实现消息处理器、实现通信通道
- **MCP 协议**: 定义模型与 Agent 之间的通信格式、实现模型客户端
- **OKF 协议**: 定义知识的存储、检索和共享机制、实现知识管理器

### 练习题

1. 实现 A2A 协议
2. 实现 MCP 协议
3. 实现 OKF 协议
4. 实现多协议协作

### 下章预告

第27章将介绍 **Agent 记忆系统实现**，包括：
- 记忆架构设计
- 记忆存储实现
- 记忆检索实现

---

**本章完**

**下一章**: [第27章：Agent 记忆系统实现](./27-chapter26-protocols.md)
