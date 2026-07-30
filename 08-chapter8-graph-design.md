# 第8章：Graph 图结构设计

## 本章目标

掌握 Agent 的图结构设计，包括 Graph 的概念、图结构设计、Graph 与 Agent 的结合。

## 前置知识

- **基础 Python/C++**: 类、继承、装饰器
- **基础 Agent**: Harness 工具框架、Loop 循环控制
- **基础图论**: 图、节点、边、路径

## 8.1 什么是 Graph

### 8.1.1 Graph 的概念

**Graph（图）** 是由节点和边组成的非线性数据结构。

**核心组件**:
- **节点（Node）**: 图的基本单元（例如：任务、步骤、Agent）
- **边（Edge）**: 节点之间的连接（例如：依赖关系、数据流）
- **路径（Path）**: 节点之间的序列（例如：执行顺序）

### 8.1.2 Graph 在 Agent 中的应用

**Agent Graph（Agent 图）** 是一种将 Agent 组织成图结构的框架。

**核心思想**:
```
用户输入 → Agent A → Agent B → Agent C → 答案
           ↓         ↓         ↓
         工具1     工具2     工具3
```

**Agent Graph 的优势**:
- **模块化**: 每个 Agent 是独立的模块
- **可组合**: Agent 可以组合成更复杂的系统
- **可扩展**: 可以轻松添加新的 Agent
- **可测试**: 每个 Agent 可以独立测试

### 8.1.3 Graph vs 其他架构

| 架构 | 特点 | 适用场景 |
|------|------|---------|
| **Linear（线性）** | 顺序执行 | 简单任务 |
| **Branching（分支）** | 条件分支 | 多路径任务 |
| **Looping（循环）** | 循环执行 | 重复任务 |
| **Graph（图）** | 网络结构 | 复杂任务 |

## 8.2 Graph 结构设计

### 8.2.1 Graph 基类

```python
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
import networkx as nx

@dataclass
class Node:
    """节点类"""
    id: str
    name: str
    description: str
    function: Callable
    inputs: List[str]
    outputs: List[str]
    dependencies: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class Edge:
    """边类"""
    from_node: str
    to_node: str
    label: str = ""
    condition: Optional[Callable] = None


class AgentGraph:
    """Agent 图"""

    def __init__(self):
        """初始化 Agent 图"""
        self.nodes = {}  # 节点字典
        self.edges = []  # 边列表
        self.graph = nx.DiGraph()  # NetworkX 图

    def add_node(self, node: Node):
        """添加节点"""
        self.nodes[node.id] = node
        self.graph.add_node(node.id)
        print(f"已添加节点：{node.id}")

    def add_edge(self, edge: Edge):
        """添加边"""
        self.edges.append(edge)
        self.graph.add_edge(edge.from_node, edge.to_node)
        print(f"已添加边：{edge.from_node} → {edge.to_node}")

    def get_node(self, node_id: str) -> Optional[Node]:
        """获取节点"""
        return self.nodes.get(node_id)

    def get_neighbors(self, node_id: str) -> List[str]:
        """获取邻居节点"""
        return list(self.graph.successors(node_id))

    def execute(self, start_node_id: str, **kwargs) -> Dict[str, Any]:
        """执行图"""
        # 检查起始节点
        if start_node_id not in self.nodes:
            raise ValueError(f"节点 {start_node_id} 不存在")

        # 初始化状态
        state = {**kwargs}

        # 执行起始节点
        self._execute_node(start_node_id, state)

        return state

    def _execute_node(self, node_id: str, state: Dict[str, Any]):
        """执行节点"""
        node = self.get_node(node_id)

        if node is None:
            raise ValueError(f"节点 {node_id} 不存在")

        # 检查依赖节点是否执行
        for dep_id in node.dependencies:
            if dep_id not in state:
                raise ValueError(f"依赖节点 {dep_id} 未执行")

        # 执行节点函数
        print(f"\n执行节点：{node.name}")
        print(f"输入：{node.inputs}")
        print(f"输出：{node.outputs}")

        result = node.function(**state)

        # 更新状态
        for output in node.outputs:
            state[output] = result

        print(f"结果：{result}")

        # 执行后续节点
        for neighbor_id in self.get_neighbors(node_id):
            edge = self._find_edge(node_id, neighbor_id)

            # 检查边条件
            if edge and edge.condition:
                if not edge.condition(state):
                    print(f"跳过边：{node.name} → {neighbor_id}")
                    continue

            # 执行邻居节点
            self._execute_node(neighbor_id, state)

    def _find_edge(self, from_node: str, to_node: str) -> Optional[Edge]:
        """查找边"""
        for edge in self.edges:
            if edge.from_node == from_node and edge.to_node == to_node:
                return edge
        return None


# 使用
graph = AgentGraph()

# 创建节点
node1 = Node(
    id="start",
    name="开始",
    description="开始任务",
    function=lambda: "开始任务",
    inputs=[],
    outputs=["result"]
)

node2 = Node(
    id="process",
    name="处理",
    description="处理数据",
    function=lambda: "处理完成",
    inputs=["result"],
    outputs=["result"]
)

node3 = Node(
    id="end",
    name="结束",
    description="结束任务",
    function=lambda: "任务完成",
    inputs=["result"],
    outputs=["result"]
)

# 添加节点
graph.add_node(node1)
graph.add_node(node2)
graph.add_node(node3)

# 添加边
graph.add_edge(Edge(from_node="start", to_node="process"))
graph.add_edge(Edge(from_node="process", to_node="end"))

# 执行图
result = graph.execute("start")
print(f"\n最终结果：{result}")
```

### 8.2.2 Graph 示例：代码生成流程

```python
def generate_code(task: str) -> str:
    """生成代码"""
    return f"生成的代码：def {task}(): pass"


def analyze_code(code: str) -> str:
    """分析代码"""
    return f"代码分析：{code} 语法正确"


def test_code(code: str) -> str:
    """测试代码"""
    return f"代码测试：{code} 通过"


# 创建图
code_generation_graph = AgentGraph()

# 创建节点
start_node = Node(
    id="start",
    name="开始",
    description="开始代码生成",
    function=lambda: "开始代码生成",
    inputs=[],
    outputs=["task"]
)

generate_node = Node(
    id="generate",
    name="生成代码",
    description="根据任务生成代码",
    function=generate_code,
    inputs=["task"],
    outputs=["code"]
)

analyze_node = Node(
    id="analyze",
    name="分析代码",
    description="分析代码语法",
    function=analyze_code,
    inputs=["code"],
    outputs=["analysis"]
)

test_node = Node(
    id="test",
    name="测试代码",
    description="测试代码功能",
    function=test_code,
    inputs=["code"],
    outputs=["test_result"]
)

end_node = Node(
    id="end",
    name="结束",
    description="结束代码生成",
    function=lambda: "代码生成完成",
    inputs=["test_result"],
    outputs=["result"]
)

# 添加节点
code_generation_graph.add_node(start_node)
code_generation_graph.add_node(generate_node)
code_generation_graph.add_node(analyze_node)
code_generation_graph.add_node(test_node)
code_generation_graph.add_node(end_node)

# 添加边
code_generation_graph.add_edge(Edge(from_node="start", to_node="generate"))
code_generation_graph.add_edge(Edge(from_node="generate", to_node="analyze"))
code_generation_graph.add_edge(Edge(from_node="analyze", to_node="test"))
code_generation_graph.add_edge(Edge(from_node="test", to_node="end"))

# 执行图
result = code_generation_graph.execute("start", task="calculate_sum")
print(f"\n最终结果：{result}")
```

### 8.2.3 Graph 示例：多 Agent 协作

```python
def user_intent_analysis(message: str) -> str:
    """分析用户意图"""
    if "写" in message:
        return "writing"
    elif "搜索" in message or "查找" in message:
        return "search"
    elif "计算" in message:
        return "calculation"
    else:
        return "unknown"


def writing_agent(message: str) -> str:
    """写作 Agent"""
    return f"写作结果：{message}"


def search_agent(message: str) -> str:
    """搜索 Agent"""
    return f"搜索结果：{message}"


def calculation_agent(message: str) -> str:
    """计算 Agent"""
    return f"计算结果：{message}"


def unknown_agent(message: str) -> str:
    """未知 Agent"""
    return f"抱歉，我无法处理这个请求：{message}"


# 创建图
multi_agent_graph = AgentGraph()

# 创建节点
intent_analysis_node = Node(
    id="intent_analysis",
    name="意图分析",
    description="分析用户意图",
    function=user_intent_analysis,
    inputs=["message"],
    outputs=["intent"]
)

writing_node = Node(
    id="writing",
    name="写作 Agent",
    description="执行写作任务",
    function=writing_agent,
    inputs=["message"],
    outputs=["result"]
)

search_node = Node(
    id="search",
    name="搜索 Agent",
    description="执行搜索任务",
    function=search_agent,
    inputs=["message"],
    outputs=["result"]
)

calculation_node = Node(
    id="calculation",
    name="计算 Agent",
    description="执行计算任务",
    function=calculation_agent,
    inputs=["message"],
    outputs=["result"]
)

unknown_node = Node(
    id="unknown",
    name="未知 Agent",
    description="处理未知请求",
    function=unknown_agent,
    inputs=["message"],
    outputs=["result"]
)

end_node = Node(
    id="end",
    name="结束",
    description="结束多 Agent 协作",
    function=lambda: "任务完成",
    inputs=["result"],
    outputs=["result"]
)

# 添加节点
multi_agent_graph.add_node(intent_analysis_node)
multi_agent_graph.add_node(writing_node)
multi_agent_graph.add_node(search_node)
multi_agent_graph.add_node(calculation_node)
multi_agent_graph.add_node(unknown_node)
multi_agent_graph.add_node(end_node)

# 添加边（带条件）
def check_intent(state: dict) -> bool:
    """检查意图"""
    return state.get("intent") == "writing"

multi_agent_graph.add_edge(
    Edge(from_node="intent_analysis", to_node="writing", condition=check_intent)
)

multi_agent_graph.add_edge(
    Edge(from_node="intent_analysis", to_node="search", condition=lambda s: s.get("intent") == "search")
)

multi_agent_graph.add_edge(
    Edge(from_node="intent_analysis", to_node="calculation", condition=lambda s: s.get("intent") == "calculation")
)

multi_agent_graph.add_edge(
    Edge(from_node="intent_analysis", to_node="unknown", condition=lambda s: s.get("intent") == "unknown")
)

multi_agent_graph.add_edge(Edge(from_node="writing", to_node="end"))
multi_agent_graph.add_edge(Edge(from_node="search", to_node="end"))
multi_agent_graph.add_edge(Edge(from_node="calculation", to_node="end"))
multi_agent_graph.add_edge(Edge(from_node="unknown", to_node="end"))

# 执行图
result = multi_agent_graph.execute("intent_analysis", message="写一首诗")
print(f"\n最终结果：{result}")
```

## 8.3 Graph 与 Agent 的结合

### 8.3.1 Agent Graph 实现

```python
class AgentGraph:
    """Agent 图（增强版）"""

    def __init__(self):
        """初始化 Agent 图"""
        self.nodes = {}
        self.edges = []
        self.graph = nx.DiGraph()

    def add_agent(self, agent):
        """添加 Agent"""
        self.nodes[agent.id] = agent
        self.graph.add_node(agent.id)
        print(f"已添加 Agent：{agent.id}")

    def add_connection(self, from_agent: str, to_agent: str, condition: Optional[Callable] = None):
        """添加连接"""
        self.edges.append(Edge(from_agent, to_agent, condition=condition))
        self.graph.add_edge(from_agent, to_agent)
        print(f"已添加连接：{from_agent} → {to_agent}")

    def execute(self, start_agent: str, **kwargs) -> Dict[str, Any]:
        """执行 Agent 图"""
        # 检查起始 Agent
        if start_agent not in self.nodes:
            raise ValueError(f"Agent {start_agent} 不存在")

        # 初始化状态
        state = {**kwargs}

        # 执行起始 Agent
        self._execute_agent(start_agent, state)

        return state

    def _execute_agent(self, agent_id: str, state: Dict[str, Any]):
        """执行 Agent"""
        agent = self.nodes[agent_id]

        if agent is None:
            raise ValueError(f"Agent {agent_id} 不存在")

        # 检查依赖 Agent 是否执行
        for dep_id in agent.dependencies:
            if dep_id not in state:
                raise ValueError(f"依赖 Agent {dep_id} 未执行")

        # 执行 Agent
        print(f"\n执行 Agent：{agent.name}")
        print(f"输入：{agent.inputs}")
        print(f"输出：{agent.outputs}")

        result = agent.execute(**state)

        # 更新状态
        for output in agent.outputs:
            state[output] = result

        print(f"结果：{result}")

        # 执行后续 Agent
        for neighbor_id in self.get_neighbors(agent_id):
            edge = self._find_edge(agent_id, neighbor_id)

            # 检查边条件
            if edge and edge.condition:
                if not edge.condition(state):
                    print(f"跳过连接：{agent.name} → {neighbor_id}")
                    continue

            # 执行邻居 Agent
            self._execute_agent(neighbor_id, state)


# 使用
class Agent:
    """Agent 基类"""

    def __init__(self, id: str, name: str, description: str, inputs: List[str], outputs: List[str]):
        self.id = id
        self.name = name
        self.description = description
        self.inputs = inputs
        self.outputs = outputs
        self.dependencies = []

    def execute(self, **kwargs) -> Any:
        """执行 Agent"""
        raise NotImplementedError


class WritingAgent(Agent):
    """写作 Agent"""

    def __init__(self):
        super().__init__(
            id="writing",
            name="写作 Agent",
            description="执行写作任务",
            inputs=["task"],
            outputs=["result"]
        )

    def execute(self, **kwargs) -> str:
        """执行 Agent"""
        task = kwargs.get("task", "")
        return f"写作结果：{task}"


class SearchAgent(Agent):
    """搜索 Agent"""

    def __init__(self):
        super().__init__(
            id="search",
            name="搜索 Agent",
            description="执行搜索任务",
            inputs=["query"],
            outputs=["result"]
        )

    def execute(self, **kwargs) -> str:
        """执行 Agent"""
        query = kwargs.get("query", "")
        return f"搜索结果：{query}"


# 创建图
agent_graph = AgentGraph()

# 添加 Agent
agent_graph.add_agent(WritingAgent())
agent_graph.add_agent(SearchAgent())

# 添加连接
agent_graph.add_connection("writing", "search")

# 执行图
result = agent_graph.execute("writing", task="写一首诗")
print(f"\n最终结果：{result}")
```

### 8.3.2 Graph 与 LLM 结合

```python
from openai import OpenAI
import json

class LLMAgent(Agent):
    """LLM Agent"""

    def __init__(self, id: str, name: str, description: str, inputs: List[str], outputs: List[str]):
        super().__init__(id, name, description, inputs, outputs)
        self.client = OpenAI(api_key="your-api-key")

    def execute(self, **kwargs) -> str:
        """执行 Agent"""
        # 构造 Prompt
        prompt = f"""
        你是一个{self.description}。

        输入：
        {json.dumps(kwargs, ensure_ascii=False)}

        请输出结果。
        """

        # 调用 LLM
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"你是一个{self.description}"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1024
        )

        return response.choices[0].message.content


# 创建图
llm_graph = AgentGraph()

# 添加 LLM Agent
llm_graph.add_agent(LLMAgent(
    id="analyzer",
    name="分析 Agent",
    description="分析文本内容",
    inputs=["text"],
    outputs=["analysis"]
))

llm_graph.add_agent(LLMAgent(
    id="summarizer",
    name="摘要 Agent",
    description="生成文本摘要",
    inputs=["text"],
    outputs=["summary"]
))

llm_graph.add_agent(LLMAgent(
    id="translator",
    name="翻译 Agent",
    description="翻译文本",
    inputs=["text", "target_language"],
    outputs=["translation"]
))

# 添加连接
llm_graph.add_connection("analyzer", "summarizer")
llm_graph.add_connection("analyzer", "translator", condition=lambda s: s.get("target_language") == "英语")

# 执行图
result = llm_graph.execute("analyzer", text="AI Agent 是一个能够自主感知、决策、行动的智能体", target_language="英语")
print(f"\n最终结果：{result}")
```

## 8.4 Graph 实现案例

### 8.4.1 代码审查 Graph

```python
def lint_code(code: str) -> str:
    """代码检查"""
    return "代码检查通过"


def test_code(code: str) -> str:
    """代码测试"""
    return "代码测试通过"


def review_code(code: str) -> str:
    """代码审查"""
    return "代码审查通过"


def generate_report(results: dict) -> str:
    """生成报告"""
    return "代码审查报告：所有检查通过"


# 创建图
code_review_graph = AgentGraph()

# 创建节点
lint_node = Node(
    id="lint",
    name="代码检查",
    description="使用 linter 检查代码",
    function=lint_code,
    inputs=["code"],
    outputs=["lint_result"]
)

test_node = Node(
    id="test",
    name="代码测试",
    description="运行单元测试",
    function=test_code,
    inputs=["code"],
    outputs=["test_result"]
)

review_node = Node(
    id="review",
    name="代码审查",
    description="人工审查代码",
    function=review_code,
    inputs=["code"],
    outputs=["review_result"]
)

report_node = Node(
    id="report",
    name="生成报告",
    description="生成代码审查报告",
    function=generate_report,
    inputs=["lint_result", "test_result", "review_result"],
    outputs=["report"]
)

# 添加节点
code_review_graph.add_node(lint_node)
code_review_graph.add_node(test_node)
code_review_graph.add_node(review_node)
code_review_graph.add_node(report_node)

# 添加边
code_review_graph.add_edge(Edge(from_node="lint", to_node="test"))
code_review_graph.add_edge(Edge(from_node="test", to_node="review"))
code_review_graph.add_edge(Edge(from_node="review", to_node="report"))

# 执行图
result = code_review_graph.execute("lint", code="def hello(): pass")
print(f"\n最终结果：{result}")
```

### 8.4.2 数据处理 Graph

```python
def extract_data(raw_data: str) -> dict:
    """提取数据"""
    return {"name": "Alice", "age": 30, "city": "北京"}


def validate_data(data: dict) -> bool:
    """验证数据"""
    return "name" in data and "age" in data


def clean_data(data: dict) -> dict:
    """清理数据"""
    return {
        "name": data["name"].strip(),
        "age": int(data["age"]),
        "city": data["city"].upper()
    }


def save_data(data: dict) -> str:
    """保存数据"""
    return f"数据已保存：{data}"


# 创建图
data_processing_graph = AgentGraph()

# 创建节点
extract_node = Node(
    id="extract",
    name="提取数据",
    description="从原始数据中提取信息",
    function=extract_data,
    inputs=["raw_data"],
    outputs=["data"]
)

validate_node = Node(
    id="validate",
    name="验证数据",
    description="验证数据格式",
    function=validate_data,
    inputs=["data"],
    outputs=["is_valid"]
)

clean_node = Node(
    id="clean",
    name="清理数据",
    description="清理和转换数据",
    function=clean_data,
    inputs=["data"],
    outputs=["cleaned_data"]
)

save_node = Node(
    id="save",
    name="保存数据",
    description="保存数据到数据库",
    function=save_data,
    inputs=["cleaned_data"],
    outputs=["result"]
)

# 添加节点
data_processing_graph.add_node(extract_node)
data_processing_graph.add_node(validate_node)
data_processing_graph.add_node(clean_node)
data_processing_graph.add_node(save_node)

# 添加边（带条件）
data_processing_graph.add_edge(Edge(from_node="extract", to_node="validate"))
data_processing_graph.add_edge(
    Edge(from_node="validate", to_node="clean", condition=lambda s: s.get("is_valid"))
)
data_processing_graph.add_edge(Edge(from_node="clean", to_node="save"))

# 执行图
result = data_processing_graph.execute("extract", raw_data="Alice,30,北京")
print(f"\n最终结果：{result}")
```

## 8.5 本章总结

### 核心要点

1. **Graph 概念**: 图由节点和边组成，用于组织 Agent
2. **Graph 基类**: 定义节点、边、执行流程
3. **Agent Graph**: 结合 Graph 和 Agent
4. **Graph 与 LLM**: 使用 LLM Agent 扩展功能
5. **实现案例**: 代码审查、数据处理

### 实战技巧

- **节点设计**: 每个节点是一个独立的功能模块
- **边设计**: 定义节点之间的依赖关系
- **条件边**: 使用条件函数控制流程
- **状态传递**: 通过状态传递数据
- **模块化**: 每个 Agent 可以独立开发和测试

### 练习题

1. 实现一个简单的 Graph
2. 实现一个多 Agent 协作 Graph
3. 实现一个与 LLM 结合的 Graph
4. 实现一个代码审查 Graph

### 下章预告

第9章将介绍 **Multi-Agent 协作**，包括：
- Multi-Agent 架构
- Agent 通信机制
- Agent 协作模式

---

**本章完**

**下一章**: [第9章：Multi-Agent 协作](./09-chapter9-multi-agent.md)
