# 第9章：Multi-Agent 协作

## 本章目标

掌握 Multi-Agent 协作机制，包括 Multi-Agent 架构、Agent 通信机制、Agent 协作模式。

## 前置知识

- **基础 Python/C++**: 类、继承、装饰器
- **基础 Agent**: Harness 工具框架、Graph 图结构
- **基础网络**: HTTP、消息队列

## 9.1 Multi-Agent 架构

### 9.1.1 什么是 Multi-Agent

**Multi-Agent（多智能体）** 是指多个 Agent 协作完成复杂任务。

**核心特点**:
- **分工**: 每个 Agent 负责不同的任务
- **协作**: Agent 之间相互配合
- **通信**: Agent 之间交换信息
- **协调**: Agent 之间协调行动

### 9.1.2 Multi-Agent vs 单 Agent

| 维度 | 单 Agent | Multi-Agent |
|------|---------|-------------|
| **任务复杂度** | 低 | 高 |
| **性能** | 单一 Agent 有限 | 多个 Agent 并行 |
| **可扩展性** | 差 | 好 |
| **容错性** | 差 | 好 |
| **开发难度** | 低 | 高 |

### 9.1.3 Multi-Agent 架构类型

**1. 线性架构（Linear Architecture）**

```
Agent A → Agent B → Agent C → 答案
```

**2. 分支架构（Branching Architecture）**

```
Agent A → Agent B
            ↓
          Agent C
            ↓
          Agent D
```

**3. 循环架构（Looping Architecture）**

```
Agent A → Agent B → Agent C → Agent A
```

**4. 图架构（Graph Architecture）**

```
Agent A → Agent B
 ↓         ↓
Agent C → Agent D
```

### 9.1.4 Multi-Agent 架构示例

```python
class LinearAgent:
    """线性 Agent"""

    def __init__(self, id: str, name: str, function):
        self.id = id
        self.name = name
        self.function = function

    def execute(self, input_data: dict) -> dict:
        """执行 Agent"""
        print(f"执行 Agent：{self.name}")
        result = self.function(**input_data)
        return {"agent_id": self.id, "result": result}


# 创建线性 Agent
agent_a = LinearAgent("a", "Agent A", lambda x: x * 2)
agent_b = LinearAgent("b", "Agent B", lambda x: x + 10)
agent_c = LinearAgent("c", "Agent C", lambda x: x ** 2)

# 执行线性流程
result_a = agent_a.execute({"input": 5})
result_b = agent_b.execute(result_a)
result_c = agent_c.execute(result_b)

print(f"\n最终结果：{result_c['result']}")
```

## 9.2 Agent 通信机制

### 9.2.1 通信方式

**1. 函数调用（Function Call）**

```python
def agent_a(input_data: dict) -> dict:
    """Agent A"""
    result = input_data["input"] * 2
    return {"agent_a_result": result}


def agent_b(input_data: dict) -> dict:
    """Agent B"""
    result = input_data["agent_a_result"] + 10
    return {"agent_b_result": result}


def agent_c(input_data: dict) -> dict:
    """Agent C"""
    result = input_data["agent_b_result"] ** 2
    return {"final_result": result}


# 通信方式1：函数调用
input_data = {"input": 5}
result_a = agent_a(input_data)
result_b = agent_b(result_a)
result_c = agent_c(result_b)

print(f"最终结果：{result_c['final_result']}")
```

**2. 消息队列（Message Queue）**

```python
import queue

# 创建消息队列
message_queue = queue.Queue()

def agent_a(input_data: dict):
    """Agent A"""
    result = input_data["input"] * 2
    message_queue.put(result)
    print(f"Agent A 完成，结果：{result}")


def agent_b():
    """Agent B"""
    result = message_queue.get()
    result = result + 10
    message_queue.put(result)
    print(f"Agent B 完成，结果：{result}")


def agent_c():
    """Agent C"""
    result = message_queue.get()
    result = result ** 2
    print(f"Agent C 完成，最终结果：{result}")


# 执行流程
input_data = {"input": 5}
agent_a(input_data)
agent_b()
agent_c()
```

**3. 共享状态（Shared State）**

```python
class SharedState:
    """共享状态"""

    def __init__(self):
        self.data = {}


# 创建共享状态
shared_state = SharedState()

def agent_a(input_data: dict):
    """Agent A"""
    result = input_data["input"] * 2
    shared_state.data["agent_a_result"] = result
    print(f"Agent A 完成，结果：{result}")


def agent_b():
    """Agent B"""
    result = shared_state.data["agent_a_result"] + 10
    shared_state.data["agent_b_result"] = result
    print(f"Agent B 完成，结果：{result}")


def agent_c():
    """Agent C"""
    result = shared_state.data["agent_b_result"] ** 2
    print(f"Agent C 完成，最终结果：{result}")


# 执行流程
input_data = {"input": 5}
agent_a(input_data)
agent_b()
agent_c()
```

**4. HTTP API（REST API）**

```python
import requests

BASE_URL = "http://localhost:8000"

def agent_a(input_data: dict):
    """Agent A（HTTP API）"""
    response = requests.post(
        f"{BASE_URL}/agent_a",
        json=input_data
    )
    return response.json()


def agent_b(input_data: dict):
    """Agent B（HTTP API）"""
    response = requests.post(
        f"{BASE_URL}/agent_b",
        json=input_data
    )
    return response.json()


def agent_c(input_data: dict):
    """Agent C（HTTP API）"""
    response = requests.post(
        f"{BASE_URL}/agent_c",
        json=input_data
    )
    return response.json()


# 执行流程
input_data = {"input": 5}
result_a = agent_a(input_data)
result_b = agent_b(result_a)
result_c = agent_c(result_b)

print(f"最终结果：{result_c['final_result']}")
```

### 9.2.2 通信协议

**1. Agent-to-Agent (A2A)**

```python
class Agent:
    """Agent 基类"""

    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

    def execute(self, input_data: dict) -> dict:
        """执行 Agent"""
        raise NotImplementedError


class A2AProtocol:
    """A2A 协议"""

    def __init__(self):
        self.agents = {}

    def register_agent(self, agent: Agent):
        """注册 Agent"""
        self.agents[agent.id] = agent
        print(f"已注册 Agent：{agent.name}")

    def call_agent(self, agent_id: str, input_data: dict) -> dict:
        """调用 Agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} 不存在")

        agent = self.agents[agent_id]
        return agent.execute(input_data)


# 使用
agent_a = Agent("a", "Agent A")
agent_b = Agent("b", "Agent B")

protocol = A2AProtocol()
protocol.register_agent(agent_a)
protocol.register_agent(agent_b)

result = protocol.call_agent("a", {"input": 5})
print(f"Agent A 结果：{result}")
```

**2. Agent-to-Tool (A2T)**

```python
class ToolRegistry:
    """工具注册器"""

    def __init__(self):
        self.tools = {}

    def register_tool(self, name: str, tool_func):
        """注册工具"""
        self.tools[name] = tool_func

    def call_tool(self, name: str, **kwargs):
        """调用工具"""
        if name not in self.tools:
            raise ValueError(f"工具 {name} 不存在")

        return self.tools[name](**kwargs)


# 使用
registry = ToolRegistry()

def get_weather(city: str) -> str:
    """获取天气"""
    return f"{city}今天天气晴"


def search_web(query: str) -> str:
    """搜索网页"""
    return f"搜索结果：{query}"


registry.register_tool("get_weather", get_weather)
registry.register_tool("search_web", search_web)


class Agent:
    """Agent（使用工具）"""

    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
        self.registry = registry

    def execute(self, input_data: dict) -> dict:
        """执行 Agent"""
        print(f"执行 Agent：{self.name}")

        # 调用工具
        if "tool" in input_data:
            result = self.registry.call_tool(
                input_data["tool"],
                **input_data.get("params", {})
            )
            return {"result": result}

        return {"result": "任务完成"}


# 使用
agent_a = Agent("a", "Agent A")

result = agent_a.execute({
    "tool": "get_weather",
    "params": {"city": "北京"}
})

print(f"结果：{result}")
```

## 9.3 Agent 协作模式

### 9.3.1 轮询模式（Polling Pattern）

**特点**: Agent 主动轮询任务队列

```python
import queue
import time

class TaskQueue:
    """任务队列"""

    def __init__(self):
        self.queue = queue.Queue()

    def add_task(self, task: dict):
        """添加任务"""
        self.queue.put(task)

    def get_task(self) -> dict:
        """获取任务"""
        return self.queue.get()


class PollingAgent:
    """轮询 Agent"""

    def __init__(self, id: str, name: str, task_queue: TaskQueue):
        self.id = id
        self.name = name
        self.task_queue = task_queue

    def execute(self):
        """执行 Agent（轮询）"""
        while True:
            task = self.task_queue.get_task()
            print(f"Agent {self.name} 接收到任务：{task}")

            # 处理任务
            result = self._process_task(task)
            print(f"Agent {self.name} 处理结果：{result}")

            # 检查是否完成
            if task.get("complete", False):
                print(f"Agent {self.name} 任务完成")
                break

            # 等待一段时间
            time.sleep(1)

    def _process_task(self, task: dict) -> str:
        """处理任务"""
        return f"处理结果：{task}"


# 使用
task_queue = TaskQueue()
task_queue.add_task({"task": "任务1", "complete": False})
task_queue.add_task({"task": "任务2", "complete": False})
task_queue.add_task({"task": "任务3", "complete": True})

agent = PollingAgent("1", "Agent 1", task_queue)
agent.execute()
```

### 9.3.2 发布订阅模式（Publish-Subscribe Pattern）

**特点**: Agent 发布/订阅消息

```python
import threading

class MessageBroker:
    """消息代理"""

    def __init__(self):
        self.subscribers = {}

    def subscribe(self, topic: str, callback):
        """订阅主题"""
        if topic not in self.subscribers:
            self.subscribers[topic] = []

        self.subscribers[topic].append(callback)

    def publish(self, topic: str, message: dict):
        """发布消息"""
        if topic not in self.subscribers:
            return

        for callback in self.subscribers[topic]:
            callback(message)


class PublishingAgent:
    """发布 Agent"""

    def __init__(self, id: str, name: str, broker: MessageBroker):
        self.id = id
        self.name = name
        self.broker = broker

    def execute(self):
        """执行 Agent（发布消息）"""
        print(f"Agent {self.name} 开始执行")

        # 发布消息
        self.broker.publish("task", {"task": "处理数据"})

        print(f"Agent {self.name} 执行完成")


class SubscribingAgent:
    """订阅 Agent"""

    def __init__(self, id: str, name: str, broker: MessageBroker):
        self.id = id
        self.name = name
        self.broker = broker

    def execute(self):
        """执行 Agent（订阅消息）"""
        print(f"Agent {self.name} 开始执行")

        # 订阅主题
        self.broker.subscribe("task", self._on_message)

        # 等待消息
        while True:
            time.sleep(1)

    def _on_message(self, message: dict):
        """处理消息"""
        print(f"Agent {self.name} 接收到消息：{message}")
        print(f"Agent {self.name} 处理完成")

        # 检查是否完成
        if message.get("complete", False):
            print(f"Agent {self.name} 任务完成")


# 使用
broker = MessageBroker()

agent_a = PublishingAgent("1", "Agent A", broker)
agent_b = SubscribingAgent("2", "Agent B", broker)

# 启动 Agent
agent_thread_a = threading.Thread(target=agent_a.execute)
agent_thread_b = threading.Thread(target=agent_b.execute)

agent_thread_a.start()
agent_thread_b.start()

agent_thread_a.join()
agent_thread_b.join()
```

### 9.3.3 协调器模式（Orchestrator Pattern）

**特点**: 协调器 Agent 协调其他 Agent

```python
class OrchestratorAgent:
    """协调器 Agent"""

    def __init__(self, id: str, name: str, agents: dict):
        self.id = id
        self.name = name
        self.agents = agents

    def execute(self, task: dict):
        """执行协调器"""
        print(f"协调器 {self.name} 开始执行任务：{task}")

        # 分配任务
        for agent_id, agent in self.agents.items():
            print(f"协调器 {self.name} 分配任务给 Agent {agent.name}")
            result = agent.execute(task)
            print(f"Agent {agent.name} 返回结果：{result}")

        print(f"协调器 {self.name} 任务完成")


class WorkerAgent:
    """工作 Agent"""

    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

    def execute(self, task: dict) -> dict:
        """执行任务"""
        print(f"Agent {self.name} 处理任务：{task}")
        return {"agent": self.name, "result": f"处理结果：{task}"}


# 使用
worker1 = WorkerAgent("1", "Worker 1")
worker2 = WorkerAgent("2", "Worker 2")

agents = {
    "1": worker1,
    "2": worker2
}

orchestrator = OrchestratorAgent("orchestrator", "协调器", agents)

orchestrator.execute("处理数据")
```

## 9.4 Multi-Agent 实现案例

### 9.4.1 写作团队（Writing Team）

```python
class WritingAgent:
    """写作 Agent"""

    def __init__(self, id: str, name: str, role: str):
        self.id = id
        self.name = name
        self.role = role

    def execute(self, input_data: dict) -> dict:
        """执行任务"""
        print(f"【{self.role}】{self.name} 开始工作")

        if self.role == "planner":
            # 规划员：规划文章结构
            return {
                "structure": [
                    "引言",
                    "正文1",
                    "正文2",
                    "结论"
                ]
            }
        elif self.role == "writer":
            # 写作者：撰写内容
            structure = input_data.get("structure", [])
            return {
                "content": f"撰写内容：{structure}"
            }
        elif self.role == "reviewer":
            # 审阅者：审查内容
            content = input_data.get("content", "")
            return {
                "review": "审查通过"
            }
        elif self.role == "editor":
            # 编辑：编辑内容
            review = input_data.get("review", "")
            return {
                "edited": f"编辑结果：{review}"
            }

        return {"result": "任务完成"}


# 创建写作团队
planner = WritingAgent("1", "规划员", "planner")
writer = WritingAgent("2", "写作者", "writer")
reviewer = WritingAgent("3", "审阅者", "reviewer")
editor = WritingAgent("4", "编辑", "editor")


# 执行写作流程
def execute_writing_team():
    """执行写作团队"""
    print("=== 写作团队开始工作 ===\n")

    # 1. 规划
    structure = planner.execute({})
    print(f"结构：{structure['structure']}\n")

    # 2. 撰写
    content = writer.execute({"structure": structure["structure"]})
    print(f"内容：{content['content']}\n")

    # 3. 审阅
    review = reviewer.execute({"content": content["content"]})
    print(f"审查：{review['review']}\n")

    # 4. 编辑
    edited = editor.execute({"review": review["review"]})
    print(f"编辑：{edited['edited']}\n")

    print("=== 写作团队完成工作 ===")


execute_writing_team()
```

### 9.4.2 代码审查团队（Code Review Team）

```python
class CodeReviewer:
    """代码审查 Agent"""

    def __init__(self, id: str, name: str, role: str):
        self.id = id
        self.name = name
        self.role = role

    def execute(self, input_data: dict) -> dict:
        """执行任务"""
        print(f"【{self.role}】{self.name} 开始工作")

        if self.role == "linter":
            # Linter：代码检查
            code = input_data.get("code", "")
            return {
                "lint_result": "Linter：代码检查通过"
            }
        elif self.role == "tester":
            # Tester：单元测试
            code = input_data.get("code", "")
            return {
                "test_result": "Tester：单元测试通过"
            }
        elif self.role == "security":
            # Security：安全检查
            code = input_data.get("code", "")
            return {
                "security_result": "Security：安全检查通过"
            }
        elif self.role == "performance":
            # Performance：性能检查
            code = input_data.get("code", "")
            return {
                "performance_result": "Performance：性能检查通过"
            }
        elif self.role == "final":
            # Final：最终审查
            lint = input_data.get("lint_result", "")
            test = input_data.get("test_result", "")
            security = input_data.get("security_result", "")
            performance = input_data.get("performance_result", "")

            return {
                "final_review": "代码审查完成，所有检查通过"
            }

        return {"result": "任务完成"}


# 创建代码审查团队
linter = CodeReviewer("1", "Linter", "linter")
tester = CodeReviewer("2", "Tester", "tester")
security = CodeReviewer("3", "Security", "security")
performance = CodeReviewer("4", "Performance", "performance")
final = CodeReviewer("5", "Final", "final")


# 执行代码审查流程
def execute_code_review(code: str):
    """执行代码审查流程"""
    print("=== 代码审查团队开始工作 ===\n")

    # 1. Linter
    lint_result = linter.execute({"code": code})
    print(f"{lint_result['lint_result']}\n")

    # 2. Tester
    test_result = tester.execute({"code": code})
    print(f"{test_result['test_result']}\n")

    # 3. Security
    security_result = security.execute({"code": code})
    print(f"{security_result['security_result']}\n")

    # 4. Performance
    performance_result = performance.execute({"code": code})
    print(f"{performance_result['performance_result']}\n")

    # 5. Final
    final_result = final.execute({
        "lint_result": lint_result["lint_result"],
        "test_result": test_result["test_result"],
        "security_result": security_result["security_result"],
        "performance_result": performance_result["performance_result"]
    })
    print(f"{final_result['final_review']}\n")

    print("=== 代码审查团队完成工作 ===")


execute_code_review("def hello(): pass")
```

## 9.5 本章总结

### 核心要点

1. **Multi-Agent 架构**: 多个 Agent 协作完成复杂任务
2. **通信方式**: 函数调用、消息队列、共享状态、HTTP API
3. **通信协议**: A2A、A2T
4. **协作模式**: 轮询模式、发布订阅模式、协调器模式
5. **实现案例**: 写作团队、代码审查团队

### 实战技巧

- **通信方式**: 根据场景选择合适的通信方式
- **通信协议**: 定义清晰的通信协议
- **协作模式**: 选择合适的协作模式
- **角色分配**: 每个 Agent 负责不同的任务
- **协调器**: 使用协调器协调多个 Agent

### 练习题

1. 实现一个简单的 Multi-Agent 系统
2. 实现一个发布订阅模式的多 Agent 系统
3. 实现一个协调器模式的多 Agent 系统
4. 实现一个写作团队 Multi-Agent 系统

### 下章预告

第10章将介绍 **记忆与知识管理**，包括：
- 知识管理架构
- 知识图谱
- 记忆压缩与检索

---

**本章完**

**下一章**: [第10章：记忆与知识管理](./10-chapter10-knowledge.md)
