# 第11章：协议栈设计

## 本章目标

掌握 Agent 协议栈设计，包括 A2A 协议、MCP 协议、OKF 协议。

## 前置知识

- **基础 Python/C++**: 类、继承、装饰器
- **基础网络**: HTTP、WebSocket
- **基础协议**: JSON、XML

## 11.1 协议栈概念

### 11.1.1 什么是协议栈

**协议栈（Protocol Stack）** 是一组定义 Agent 之间通信、协作的协议。

**核心功能**:
- **Agent-to-Agent (A2A)**: Agent 之间通信
- **Agent-to-Tool (A2T)**: Agent 与工具通信
- **Agent-to-Client (A2C)**: Agent 与客户端通信
- **Agent-to-System (A2S)**: Agent 与系统通信

### 11.1.2 协议栈架构

```
┌─────────────────────────────────────────────────────────┐
│                    协议栈架构                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  应用层                            │  │
│  │  - A2A 协议（Agent 间通信）                        │  │
│  │  - A2T 协议（Agent 与工具通信）                    │  │
│  │  - A2C 协议（Agent 与客户端通信）                  │  │
│  │  - A2S 协议（Agent 与系统通信）                    │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  传输层                            │  │
│  │  - HTTP/REST API                                  │  │
│  │  - WebSocket                                      │  │
│  │  - gRPC                                           │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  网络层                            │  │
│  │  - TCP/IP                                          │  │
│  │  - UDP                                             │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 11.1.3 协议栈对比

| 协议 | 用途 | 通信方式 | 优点 | 缺点 |
|------|------|---------|------|------|
| **A2A** | Agent 间通信 | HTTP/REST、WebSocket | 标准、易实现 | 延迟较高 |
| **MCP** | Agent 与工具通信 | HTTP/REST、gRPC | 灵活、可扩展 | 需要定义接口 |
| **OKF** | Agent 与框架通信 | HTTP/REST | 标准、统一 | 需要适配器 |

## 11.2 A2A 协议设计

### 11.2.1 A2A 协议概述

**A2A（Agent-to-Agent）协议** 是 Agent 之间通信的协议。

**核心功能**:
- **消息传递**: Agent 之间传递消息
- **状态同步**: Agent 之间同步状态
- **任务协作**: Agent 之间协作完成任务

### 11.2.2 A2A 协议规范

**1. 消息格式**

```json
{
  "message_id": "msg_123456",
  "sender_agent": "agent_a",
  "receiver_agent": "agent_b",
  "timestamp": "2026-07-28T12:00:00Z",
  "message_type": "request|response|notification|error",
  "payload": {
    "task": "处理数据",
    "data": {...}
  },
  "metadata": {
    "priority": "high|normal|low",
    "retries": 3
  }
}
```

**2. 通信流程**

```
Agent A                          Agent B
   |                                |
   |--- 发送消息 -------------------->|
   |  (request)                      |
   |                                |
   |<--- 返回消息 -------------------|
   |  (response)                     |
   |                                |
```

**3. 完整实现**

```python
import json
import time
from typing import Dict, Any, Optional
import requests

class A2AProtocol:
    """A2A 协议"""

    def __init__(self, base_url: str):
        """
        初始化 A2A 协议

        Args:
            base_url: Agent B 的基础 URL
        """
        self.base_url = base_url

    def send_message(
        self,
        sender_agent: str,
        receiver_agent: str,
        message_type: str,
        payload: Dict[str, Any],
        priority: str = "normal",
        retries: int = 3
    ) -> Dict[str, Any]:
        """
        发送消息

        Args:
            sender_agent: 发送 Agent
            receiver_agent: 接收 Agent
            message_type: 消息类型
            payload: 消息负载
            priority: 优先级
            retries: 重试次数

        Returns:
            响应消息
        """
        # 构造消息
        message = {
            "message_id": f"msg_{int(time.time())}_{sender_agent}",
            "sender_agent": sender_agent,
            "receiver_agent": receiver_agent,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "message_type": message_type,
            "payload": payload,
            "metadata": {
                "priority": priority,
                "retries": retries
            }
        }

        # 发送消息
        for attempt in range(retries):
            try:
                response = requests.post(
                    f"{self.base_url}/api/a2a/message",
                    json=message,
                    timeout=10
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"发送失败，重试 {attempt + 1}/{retries}")
                    time.sleep(1)

            except requests.exceptions.RequestException as e:
                print(f"请求异常：{e}，重试 {attempt + 1}/{retries}")
                time.sleep(1)

        raise Exception(f"发送消息失败，重试 {retries} 次后仍失败")

    def receive_message(self, agent_id: str, callback):
        """
        接收消息

        Args:
            agent_id: Agent ID
            callback: 消息回调函数
        """
        # 这里可以实现 WebSocket 或长轮询
        # 简化实现：使用轮询
        while True:
            try:
                response = requests.get(
                    f"{self.base_url}/api/a2a/messages/{agent_id}",
                    timeout=5
                )

                if response.status_code == 200:
                    messages = response.json()

                    for message in messages:
                        callback(message)

                    # 删除已处理的消息
                    for msg_id in [m["message_id"] for m in messages]:
                        requests.delete(
                            f"{self.base_url}/api/a2a/message/{msg_id}"
                        )

            except requests.exceptions.RequestException as e:
                print(f"接收消息异常：{e}")

            time.sleep(1)


# 使用
agent_a = A2AProtocol(base_url="http://localhost:8000")

# 发送消息
response = agent_a.send_message(
    sender_agent="agent_a",
    receiver_agent="agent_b",
    message_type="request",
    payload={
        "task": "处理数据",
        "data": {"input": 5}
    },
    priority="high"
)

print(f"响应：{response}")
```

### 11.2.3 A2A 协议示例

```python
class AgentA:
    """Agent A"""

    def __init__(self, a2a_protocol: A2AProtocol):
        self.a2a = a2a_protocol

    def execute(self, input_data: dict):
        """执行任务"""
        print(f"Agent A 接收任务：{input_data}")

        # 发送请求到 Agent B
        response = self.a2a.send_message(
            sender_agent="agent_a",
            receiver_agent="agent_b",
            message_type="request",
            payload={
                "task": "处理数据",
                "data": input_data
            },
            priority="high"
        )

        print(f"Agent A 收到响应：{response}")
        return response


class AgentB:
    """Agent B"""

    def __init__(self, a2a_protocol: A2AProtocol):
        self.a2a = a2a_protocol

    def execute(self, input_data: dict):
        """执行任务"""
        print(f"Agent B 接收任务：{input_data}")

        # 处理数据
        result = input_data["data"] * 2

        # 发送响应
        response = self.a2a.send_message(
            sender_agent="agent_b",
            receiver_agent="agent_a",
            message_type="response",
            payload={
                "result": result
            }
        )

        print(f"Agent B 发送响应：{response}")
        return result

    def start_listening(self):
        """开始监听消息"""
        print("Agent B 开始监听消息...")

        def on_message(message):
            if message["message_type"] == "request":
                # 处理请求
                payload = message["payload"]
                result = self.execute(payload)
                print(f"Agent B 处理完成，结果：{result}")

        self.a2a.receive_message("agent_b", on_message)


# 使用
a2a_protocol = A2AProtocol(base_url="http://localhost:8000")

agent_a = AgentA(a2a_protocol)
agent_b = AgentB(a2a_protocol)

# 启动 Agent B（监听消息）
agent_b.start_listening()

# 执行 Agent A
result = agent_a.execute({"data": 5})
print(f"最终结果：{result}")
```

## 11.3 MCP 协议设计

### 11.3.1 MCP 协议概述

**MCP（Model Context Protocol）协议** 是 Agent 与工具通信的协议。

**核心功能**:
- **工具调用**: Agent 调用工具
- **工具注册**: Agent 注册工具
- **工具验证**: Agent 验证工具

### 11.3.2 MCP 协议规范

**1. 工具定义**

```json
{
  "tool_id": "get_weather",
  "name": "get_weather",
  "description": "获取天气信息",
  "parameters": {
    "type": "object",
    "properties": {
      "city": {
        "type": "string",
        "description": "城市名称"
      }
    },
    "required": ["city"]
  },
  "version": "1.0",
  "author": "MCP Team"
}
```

**2. 工具调用**

```json
{
  "call_id": "call_123456",
  "tool_id": "get_weather",
  "arguments": {
    "city": "北京"
  },
  "timestamp": "2026-07-28T12:00:00Z"
}
```

**3. 工具响应**

```json
{
  "call_id": "call_123456",
  "status": "success|error",
  "result": {
    "weather": "晴",
    "temperature": "15-25°C"
  },
  "error": null
}
```

**4. 完整实现**

```python
import json
import time
from typing import Dict, Any, List, Optional
import requests

class MCPProtocol:
    """MCP 协议"""

    def __init__(self, base_url: str):
        """
        初始化 MCP 协议

        Args:
            base_url: 工具服务的基础 URL
        """
        self.base_url = base_url

    def register_tool(self, tool: Dict[str, Any]):
        """注册工具"""
        url = f"{self.base_url}/api/mcp/tools/register"
        response = requests.post(url, json=tool, timeout=10)

        if response.status_code == 200:
            print(f"工具注册成功：{tool['name']}")
        else:
            print(f"工具注册失败：{response.text}")

    def call_tool(self, tool_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用工具

        Args:
            tool_id: 工具 ID
            arguments: 工具参数

        Returns:
            工具执行结果
        """
        # 构造调用请求
        call_id = f"call_{int(time.time())}"
        request = {
            "call_id": call_id,
            "tool_id": tool_id,
            "arguments": arguments,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

        # 发送调用请求
        url = f"{self.base_url}/api/mcp/tools/call"
        response = requests.post(url, json=request, timeout=10)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"工具调用失败：{response.text}")

    def list_tools(self) -> List[Dict[str, Any]]:
        """列出所有工具"""
        url = f"{self.base_url}/api/mcp/tools/list"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"获取工具列表失败：{response.text}")


# 使用
mcp_protocol = MCPProtocol(base_url="http://localhost:8000")

# 注册工具
tool = {
    "tool_id": "get_weather",
    "name": "get_weather",
    "description": "获取天气信息",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "城市名称"
            }
        },
        "required": ["city"]
    },
    "version": "1.0",
    "author": "MCP Team"
}

mcp_protocol.register_tool(tool)

# 调用工具
result = mcp_protocol.call_tool(
    tool_id="get_weather",
    arguments={"city": "北京"}
)

print(f"工具调用结果：{result}")

# 列出所有工具
tools = mcp_protocol.list_tools()
print(f"所有工具：{[tool['name'] for tool in tools]}")
```

### 11.3.3 MCP 协议示例

```python
class ToolAgent:
    """工具 Agent"""

    def __init__(self, mcp_protocol: MCPProtocol):
        self.mcp = mcp_protocol

    def execute(self, task: str):
        """执行任务"""
        print(f"Agent 接收任务：{task}")

        # 调用工具
        result = self.mcp.call_tool(
            tool_id="get_weather",
            arguments={"city": "北京"}
        )

        print(f"工具调用结果：{result}")
        return result

    def list_available_tools(self):
        """列出可用工具"""
        tools = self.mcp.list_tools()
        print(f"可用工具：")
        for tool in tools:
            print(f"- {tool['name']}: {tool['description']}")


# 使用
mcp_protocol = MCPProtocol(base_url="http://localhost:8000")

agent = ToolAgent(mcp_protocol)

# 列出可用工具
agent.list_available_tools()

# 执行任务
result = agent.execute("获取北京的天气")
```

## 11.4 OKF 协议设计

### 11.4.1 OKF 协议概述

**OKF（Open Knowledge Framework）协议** 是 Agent 与框架通信的协议。

**核心功能**:
- **框架通信**: Agent 与框架通信
- **框架管理**: Agent 管理框架
- **框架监控**: Agent 监控框架

### 11.4.2 OKF 协议规范

**1. 框架注册**

```json
{
  "framework_id": "framework_123456",
  "name": "Agent Framework",
  "version": "1.0",
  "description": "Agent 框架",
  "agents": ["agent_a", "agent_b"],
  "tools": ["tool_1", "tool_2"],
  "timestamp": "2026-07-28T12:00:00Z"
}
```

**2. 框架状态查询**

```json
{
  "framework_id": "framework_123456",
  "status": "running|stopped|error",
  "agents_count": 2,
  "tools_count": 2,
  "active_agents": ["agent_a"],
  "timestamp": "2026-07-28T12:00:00Z"
}
```

**3. 完整实现**

```python
import json
import time
from typing import Dict, Any, List, Optional
import requests

class OKFProtocol:
    """OKF 协议"""

    def __init__(self, base_url: str):
        """
        初始化 OKF 协议

        Args:
            base_url: 框架的基础 URL
        """
        self.base_url = base_url

    def register_framework(self, framework: Dict[str, Any]):
        """注册框架"""
        url = f"{self.base_url}/api/okf/frameworks/register"
        response = requests.post(url, json=framework, timeout=10)

        if response.status_code == 200:
            print(f"框架注册成功：{framework['name']}")
        else:
            print(f"框架注册失败：{response.text}")

    def get_framework_status(self, framework_id: str) -> Dict[str, Any]:
        """
        获取框架状态

        Args:
            framework_id: 框架 ID

        Returns:
            框架状态
        """
        url = f"{self.base_url}/api/okf/frameworks/{framework_id}/status"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"获取框架状态失败：{response.text}")

    def list_frameworks(self) -> List[Dict[str, Any]]:
        """列出所有框架"""
        url = f"{self.base_url}/api/okf/frameworks/list"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"获取框架列表失败：{response.text}")


# 使用
okf_protocol = OKFProtocol(base_url="http://localhost:8000")

# 注册框架
framework = {
    "framework_id": "framework_123456",
    "name": "Agent Framework",
    "version": "1.0",
    "description": "Agent 框架",
    "agents": ["agent_a", "agent_b"],
    "tools": ["tool_1", "tool_2"],
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
}

okf_protocol.register_framework(framework)

# 获取框架状态
status = okf_protocol.get_framework_status("framework_123456")
print(f"框架状态：{status}")

# 列出所有框架
frameworks = okf_protocol.list_frameworks()
print(f"所有框架：{[f['name'] for f in frameworks]}")
```

## 11.5 本章总结

### 核心要点

1. **协议栈概念**: A2A、MCP、OKF 协议
2. **A2A 协议**: Agent 间通信、消息格式、通信流程
3. **MCP 协议**: Agent 与工具通信、工具定义、工具调用
4. **OKF 协议**: Agent 与框架通信、框架注册、框架状态查询

### 实战技巧

- **A2A 协议**: 使用 HTTP/REST 或 WebSocket 实现消息传递
- **MCP 协议**: 定义工具接口、参数验证
- **OKF 协议**: 管理框架状态、监控框架
- **协议设计**: 定义清晰的接口和消息格式
- **错误处理**: 处理网络异常、超时等

### 练习题

1. 实现一个简单的 A2A 协议
2. 实现一个 MCP 协议工具调用器
3. 实现一个 OKF 协议框架管理器
4. 实现一个多协议栈集成

### 下章预告

第12章将介绍 **Agent 系统部署**，包括：
- Agent 系统部署架构
- Docker 部署
- K8s 部署
- 监控与日志

---

**本章完**

**下一章**: [第12章：Agent 系统部署](./12-chapter12-deployment.md)
