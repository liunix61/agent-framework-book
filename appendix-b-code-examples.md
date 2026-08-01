#| 附录B：完整代码示例

## B.1 Agent Admin 项目示例

### 1. 基础配置

```python
# src/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Agent Admin"
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/agent_admin"
    redis_url: str = "redis://localhost:***@app.post("/users/")
async def create_user(user, db: AsyncSession = Depends(get_db)):
    # 检查用户名是否已存在
    result = await db.execute(select(SysUser).where(SysUser.username == user.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already registered")

    # 创建新用户
    db_user = SysUser(id=str(uuid.uuid4()), username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}")
async def read_user(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SysUser).where(SysUser.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

## B.2 UniAgents 项目示例

### 1. Agent 定义

```python
# uniagents/agents/code_reviewer.py
from typing import List
from uniagents.core import Agent, Task, Tool

class CodeReviewerAgent(Agent):
    def __init__(self):
        super().__init__(
            name="CodeReviewer",
            description="Review code for bugs and improvements"
        )
        self.tools = [
            Tool(name="analyze_code", description="Analyze code structure"),
            Tool(name="find_bugs", description="Find potential bugs")
        ]

    async def review_code(self, code: str) -> dict:
        # 调用工具
        analysis = await self.call_tool("analyze_code", {"code": code})
        bugs = await self.call_tool("find_bugs", {"code": code})

        return {
            "summary": analysis["summary"],
            "bugs": bugs["bugs"],
            "suggestions": bugs["suggestions"]
        }
```

### 2. DAG 编排

```python
# uniagents/workflows/code_review_workflow.py
from uniagents.core import Workflow, Task, Agent

def create_code_review_workflow():
    workflow = Workflow(name="Code Review Workflow")

    # 创建 Agent
    reviewer = CodeReviewerAgent()
    optimizer = OptimizerAgent()

    # 创建任务
    review_task = Task(
        name="Review Code",
        agent=reviewer,
        input_schema={"code": str},
        output_schema={"summary": str, "bugs": List[str], "suggestions": List[str]}
    )

    optimize_task = Task(
        name="Optimize Code",
        agent=optimizer,
        input_schema={"review_result": dict},
        output_schema={"optimized_code": str}
    )

    # 定义依赖关系
    review_task.set_dependency(optimize_task)

    # 添加到工作流
    workflow.add_task(review_task)
    workflow.add_task(optimize_task)

    return workflow
```

### 3. 协议栈集成

```python
# uniagents/protocols/a2a_protocol.py
from uniagents.protocols import Protocol

class A2AProtocol(Protocol):
    """Agent-to-Agent Protocol"""

    async def send_message(self, from_agent: str, to_agent: str, message: dict):
        # 实现 A2A 协议
        pass

    async def receive_message(self, agent_id: str) -> dict:
        # 实现 A2A 协议
        pass
```

## B.3 MindFlow 项目示例

### 1. Agent 定义

```python
# mindflow/agents/writer_agent.py
from mindflow.agents.base import Agent
from mindflow.core import Task

class WriterAgent(Agent):
    """写作 Agent"""

    def __init__(self):
        super().__init__(
            name="Writer",
            description="Write articles, essays, and stories"
        )
        self.core_modules = [
            "content_generator",
            "style_checker",
            "grammar_checker"
        ]

    async def write_article(self, topic: str, length: str = "medium") -> dict:
        # 生成内容
        content = await self.call_core_module("content_generator", {
            "topic": topic,
            "length": length
        })

        # 检查风格
        style_score = await self.call_core_module("style_checker", {
            "content": content,
            "target_style": "professional"
        })

        # 检查语法
        grammar_score = await self.call_core_module("grammar_checker", {
            "content": content
        })

        return {
            "content": content,
            "style_score": style_score,
            "grammar_score": grammar_score
        }
```

### 2. Pipeline 编排

```python
# mindflow/workflows/article_pipeline.py
from mindflow.workflows import Pipeline

def create_article_pipeline():
    pipeline = Pipeline(name="Article Pipeline")

    # 创建 Agent
    researcher = ResearchAgent()
    writer = WriterAgent()
    editor = EditorAgent()

    # 创建阶段
    research_stage = Stage(
        name="Research",
        agent=researcher,
        tasks=["gather_sources", "analyze_sources"]
    )

    writing_stage = Stage(
        name="Writing",
        agent=writer,
        tasks=["draft_article", "generate_outline"]
    )

    editing_stage = Stage(
        name="Editing",
        agent=editor,
        tasks=["proofread", "format"]
    )

    # 添加阶段
    pipeline.add_stage(research_stage)
    pipeline.add_stage(writing_stage)
    pipeline.add_stage(editing_stage)

    return pipeline
```

## B.4 QuantFlow 项目示例

### 1. 策略 Agent

```python
# quantflow/agents/strategy_agent.py
from quantflow.agents.base import Agent
from quantflow.core import Task, Tool

class StrategyAgent(Agent):
    """策略 Agent"""

    def __init__(self):
        super().__init__(
            name="StrategyAgent",
            description="Generate trading strategies"
        )
        self.tools = [
            Tool(name="analyze_market", description="Analyze market data"),
            Tool(name="generate_signal", description="Generate trading signals")
        ]

    async def generate_strategy(self, market_data: dict) -> dict:
        # 分析市场
        analysis = await self.call_tool("analyze_market", {"data": market_data})

        # 生成信号
        signal = await self.call_tool("generate_signal", {
            "analysis": analysis,
            "risk_tolerance": "medium"
        })

        return {
            "strategy_name": "TrendFollowing",
            "signals": signal,
            "confidence": 0.85,
            "risk_metrics": analysis["risk_metrics"]
        }
```

### 2. 风控 Agent

```python
# quantflow/agents/risk_agent.py
from quantflow.agents.base import Agent

class RiskAgent(Agent):
    """风控 Agent"""

    async def assess_risk(self, strategy: dict) -> dict:
        # 计算风险指标
        value_at_risk = await self.calculate_var(strategy)
        max_drawdown = await self.calculate_drawdown(strategy)
        position_size = await self.calculate_position_size(strategy)

        return {
            "var_95": value_at_risk,
            "max_drawdown": max_drawdown,
            "position_size": position_size,
            "risk_score": await self.calculate_risk_score(
                value_at_risk, max_drawdown, position_size
            )
        }
```

### 3. 交易 Agent

```python
# quantflow/agents/trading_agent.py
from quantflow.agents.base import Agent

class TradingAgent(Agent):
    """交易 Agent"""

    async def execute_order(self, signal: dict) -> dict:
        # 创建订单
        order = {
            "symbol": signal["symbol"],
            "side": signal["side"],
            "quantity": signal["quantity"],
            "price": signal["price"],
            "order_type": "market"
        }

        # 提交订单
        result = await self.submit_order(order)

        return {
            "order_id": result["order_id"],
            "status": result["status"],
            "filled_price": result["filled_price"],
            "filled_quantity": result["filled_quantity"]
        }
```

## B.5 OPCOS 项目示例

### 1. 插件系统

```python
# opcos/plugins/base_plugin.py
from abc import ABC, abstractmethod

class BasePlugin(ABC):
    """插件基类"""

    def __init__(self, plugin_id: str, name: str, version: str):
        self.plugin_id = plugin_id
        self.name = name
        self.version = version
        self.enabled = True

    @abstractmethod
    async def initialize(self, config: dict):
        """初始化插件"""
        pass

    @abstractmethod
    async def execute(self, input_data: dict) -> dict:
        """执行插件功能"""
        pass

    @abstractmethod
    async def cleanup(self):
        """清理插件资源"""
        pass
```

### 2. 协议栈实现

```python
# opcos/protocols/a2a_protocol.py
from typing import Dict, Any

class A2AProtocol:
    """Agent-to-Agent Protocol"""

    def __init__(self):
        self.agents = {}
        self.message_queue = []

    async def register_agent(self, agent_id: str, agent):
        """注册 Agent"""
        self.agents[agent_id] = agent

    async def send_message(self, from_agent: str, to_agent: str, message: Dict[str, Any]):
        """发送消息"""
        # 实现 A2A 协议
        pass

    async def receive_message(self, agent_id: str) -> Dict[str, Any]:
        """接收消息"""
        # 实现 A2A 协议
        pass
```

## B.6 测试示例

### 1. 单元测试

```python
# tests/test_auth.py
import pytest
from src.auth import verify_password, get_password_hash

def test_verify_password():
    password = "test_password"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) == True
    assert verify_password("wrong_password", hashed) == False

def test_get_password_hash():
    password = "test_password"
    hashed = get_password_hash(password)
    assert len(hashed) > 0
    assert hashed != password
```

### 2. 集成测试

```python
# tests/test_api.py
import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/users/", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "test_password"
        })
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"
```

## B.7 总结

以上示例展示了：
- **Agent Admin**：用户认证、数据库模型、FastAPI 路由
- **UniAgents**：Agent 定义、DAG 编排、协议栈集成
- **MindFlow**：Agent 定义、Pipeline 编排、写作流程
- **QuantFlow**：策略、风控、交易 Agent
- **OPCOS**：插件系统、协议栈实现

所有代码都遵循最佳实践，包括类型提示、异步编程、错误处理等。
