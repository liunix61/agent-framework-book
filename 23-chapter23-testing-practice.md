# 第23章：Agent 测试实战

## 本章目标

通过实战项目，掌握 Agent 测试的最佳实践。

## 前置知识

- **基础 测试**: pytest、unittest
- **基础 Agent**: Harness、Loop、Graph
- **基础 项目**: 项目结构、代码组织

## 23.1 单元测试实战

### 23.1.1 单元测试框架

**1. pytest 基础**

```python
import pytest

def test_add():
    """测试加法"""
    assert 1 + 1 == 2

def test_subtract():
    """测试减法"""
    assert 5 - 3 == 2

def test_multiply():
    """测试乘法"""
    assert 3 * 4 == 12

def test_divide():
    """测试除法"""
    assert 10 / 2 == 5
```

**2. 运行测试**

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest test_calculator.py::test_add

# 详细输出
pytest -v

# 显示打印输出
pytest -s

# 只显示失败的测试
pytest -x
```

### 23.1.2 Agent 单元测试实战

**1. 测试 Agent 类**

```python
# tests/test_agent.py
import pytest
from agent_framework.agent import Agent

def test_agent_execute():
    """测试 Agent 执行"""
    agent = Agent(agent_id="test_agent")

    result = agent.execute("测试任务")

    assert result is not None
    assert "test_agent" in result
    assert "测试任务" in result

def test_agent_execute_with_context():
    """测试 Agent 执行（带上下文）"""
    agent = Agent(agent_id="test_agent")

    context = {
        "data": "测试数据"
    }

    result = agent.execute("测试任务", context=context)

    assert result is not None
    assert "test_agent" in result
    assert "测试数据" in result

def test_agent_stop():
    """测试 Agent 停止"""
    agent = Agent(agent_id="test_agent")

    agent.stop()

    # 验证 Agent 已停止
    assert agent.is_stopped() == True
```

**2. 测试 Harness 工具**

```python
# tests/test_harness.py
import pytest
from agent_framework.harness import ToolRegistry, GetWeatherTool

def test_tool_registry():
    """测试工具注册"""
    registry = ToolRegistry()

    # 注册工具
    tool = GetWeatherTool()
    registry.register_tool(tool)

    # 获取工具
    retrieved_tool = registry.get_tool("get_weather")
    assert retrieved_tool is not None
    assert retrieved_tool.name == "get_weather"

def test_tool_execution():
    """测试工具执行"""
    registry = ToolRegistry()
    tool = GetWeatherTool()
    registry.register_tool(tool)

    # 执行工具
    result = tool.execute(city="北京")
    assert "北京" in result
    assert "天气" in result

def test_tool_caller():
    """测试工具调用器"""
    registry = ToolRegistry()
    tool = GetWeatherTool()
    registry.register_tool(tool)

    caller = ToolCaller(registry)

    # 调用工具
    result = caller.call_tool("get_weather", city="北京")
    assert "北京" in result
    assert "天气" in result
```

**3. 测试 Loop 控制器**

```python
# tests/test_loop.py
import pytest
from agent_framework.loop import ConditionLoopController

def test_loop_condition():
    """测试循环条件"""
    def condition_func():
        return False  # 假设任务已经完成

    controller = ConditionLoopController(
    condition_func=condition_func,
    max_iterations=10
    )

    # 检查是否应该继续
    assert not controller.should_continue()

def test_loop_increment():
    """测试循环次数增加"""
    def condition_func():
        return True

    controller = ConditionLoopController(
    condition_func=condition_func,
    max_iterations=5
    )

    # 增加循环次数
    controller.increment_iteration()
    assert controller.get_iteration() == 1

def test_loop_max_iterations():
    """测试循环最大次数"""
    def condition_func():
        return True

    controller = ConditionLoopController(
    condition_func=condition_func,
    max_iterations=3
    )

    # 增加循环次数
    controller.increment_iteration()
    controller.increment_iteration()
    controller.increment_iteration()

    # 应该已经达到最大次数
    assert controller.get_iteration() == 3
```

**4. 测试 Graph 结构**

```python
# tests/test_graph.py
import pytest
from agent_framework.graph import Graph, Node, Edge

def test_graph_creation():
    """测试 Graph 创建"""
    graph = Graph()

    # 创建节点
    node1 = Node(node_id="node1", agent=Agent(agent_id="agent1"))
    node2 = Node(node_id="node2", agent=Agent(agent_id="agent2"))

    # 创建边
    edge1 = Edge(from_node="node1", to_node="node2")

    # 添加节点
    graph.add_node(node1)
    graph.add_node(node2)

    # 添加边
    graph.add_edge(edge1)

    # 验证
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1

def test_graph_execution():
    """测试 Graph 执行"""
    graph = Graph()

    # 创建节点
    node1 = Node(node_id="node1", agent=Agent(agent_id="agent1"))
    node2 = Node(node_id="node2", agent=Agent(agent_id="agent2"))

    # 创建边
    edge1 = Edge(from_node="node1", to_node="node2")

    # 添加节点
    graph.add_node(node1)
    graph.add_node(node2)

    # 添加边
    graph.add_edge(edge1)

    # 执行 Graph
    result = graph.execute()

    # 验证
    assert result is not None
    assert "agent1" in result or "agent2" in result
```

## 23.2 集成测试实战

### 23.2.1 API 集成测试

**1. 测试 FastAPI 应用**

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from agent_framework.main import app

client = TestClient(app)

def test_health_check():
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_get_agents():
    """测试获取 Agent 列表"""
    response = client.get("/agents")
    assert response.status_code == 200
    assert "agents" in response.json()

def test_execute_agent():
    """测试执行 Agent"""
    response = client.post(
        "/agents/agent_1/execute",
        json={"task": "测试任务"}
    )
    assert response.status_code == 200
    assert "result" in response.json()
```

### 23.2.2 数据库集成测试

**1. 测试数据库连接**

```python
# tests/test_database.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from agent_framework.database import Base

@pytest.fixture
def db_session():
    """数据库会话 fixture"""
    # 创建内存数据库
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()

def test_create_user(db_session):
    """测试创建用户"""
    from agent_framework.models import User

    # 创建用户
    user = User(username="test_user", email="test@example.com")
    db_session.add(user)
    db_session.commit()

    # 验证
    result = db_session.query(User).filter(User.username == "test_user").first()
    assert result is not None
    assert result.email == "test@example.com"

def test_get_user(db_session):
    """测试获取用户"""
    from agent_framework.models import User

    # 创建用户
    user = User(username="test_user", email="test@example.com")
    db_session.add(user)
    db_session.commit()

    # 获取用户
    result = db_session.query(User).filter(User.username == "test_user").first()

    # 验证
    assert result is not None
    assert result.username == "test_user"
    assert result.email == "test@example.com"
```

### 23.2.3 工具集成测试

**1. 测试工具调用链**

```python
# tests/test_tools_integration.py
import pytest
from agent_framework.harness import ToolRegistry, ToolCaller
from agent_framework.tools import GetWeatherTool, SearchWebTool

def test_tool_chain():
    """测试工具调用链"""
    registry = ToolRegistry()
    registry.register_tool(GetWeatherTool())
    registry.register_tool(SearchWebTool())

    caller = ToolCaller(registry)

    # 调用工具链
    result = caller.call_tool("get_weather", city="北京")
    assert "北京" in result

    result = caller.call_tool("search_web", query="AI Agent")
    assert "AI Agent" in result

def test_tool_dependencies():
    """测试工具依赖"""
    registry = ToolRegistry()
    registry.register_tool(GetWeatherTool())
    registry.register_tool(SearchWebTool())

    caller = ToolCaller(registry)

    # 测试工具依赖
    with pytest.raises(ValueError):
        caller.call_tool("nonexistent_tool")
```

## 23.3 E2E 测试实战

### 23.3.1 Playwright E2E 测试

**1. 测试 Agent 界面**

```python
# tests/e2e/test_agent_flow.py
from playwright.sync_api import Page, expect

def test_agent_flow(page: Page):
    """测试 Agent 完整流程"""
    # 访问首页
    page.goto("http://localhost:3000")

    # 填写任务
    page.fill('input[name="task"]', "写一首关于春天的诗")
    page.click('button[type="submit"]')

    # 等待结果
    page.wait_for_selector('.result')

    # 验证结果
    result = page.text_content('.result')
    assert result is not None
    assert len(result) > 0

def test_agent_error_handling(page: Page):
    """测试 Agent 错误处理"""
    # 访问首页
    page.goto("http://localhost:3000")

    # 填写空任务
    page.fill('input[name="task"]', "")
    page.click('button[type="submit"]')

    # 验证错误提示
    error_message = page.text_content('.error')
    assert error_message is not None
    assert len(error_message) > 0
```

### 23.3.2 E2E 测试关键流程

**1. 测试 Agent 执行流程**

```python
# tests/e2e/test_agent_execution.py
import pytest
from agent_framework.main import app

def test_agent_execution_e2e():
    """测试 Agent 执行 E2E"""
    # 创建测试数据
    user_id = "test_user_123"

    # 执行 Agent 任务
    response = app.post(
        "/api/agent/execute",
        json={
            "task": "写一首关于春天的诗",
            "user_id": user_id
        }
    )

    assert response.status_code == 200
    data = response.json()

    # 验证响应结构
    assert "result" in data
    assert "agent_id" in data
    assert "timestamp" in data

    # 验证结果内容
    assert len(data["result"]) > 0

def test_agent_error_handling_e2e():
    """测试 Agent 错误处理 E2E"""
    # 执行 Agent 任务（无任务）
    response = app.post(
        "/api/agent/execute",
        json={
            "task": "",
            "user_id": "test_user_123"
        }
    )

    assert response.status_code == 400
    assert "error" in response.json()
```

## 23.4 测试覆盖率实战

### 23.4.1 生成覆盖率报告

**1. 安装覆盖率工具**

```bash
pip install pytest-cov
```

**2. 运行测试并生成覆盖率报告**

```bash
# 生成覆盖率报告
pytest --cov=agent_framework --cov-report=html

# 输出覆盖率到终端
pytest --cov=agent_framework --cov-report=term-missing

# 生成覆盖率报告到 XML（用于 CI/CD）
pytest --cov=agent_framework --cov-report=xml
```

**3. 查看覆盖率报告**

```bash
# 打开 HTML 报告
open htmlcov/index.html

# 查看终端输出示例
$ pytest --cov=agent_framework --cov-report=term-missing

Name                      Stmts   Miss  Cover   Missing
------------------------------------------------------
agent_framework/__init__      2      0   100%
agent_framework/agent.py     45     10    78%   23-27
agent_framework/tools.py     30      5    83%   12-15
agent_framework/utils.py     20      2    90%   8-9
------------------------------------------------------
TOTAL                        97     17    82%
```

### 23.4.2 覆盖率要求

**覆盖率标准**:

| 项目 | 覆盖率要求 |
|------|-----------|
| **核心业务逻辑** | ≥ 90% |
| **工具模块** | ≥ 85% |
| **工具类** | ≥ 80% |
| **工具函数** | ≥ 75% |
| **辅助工具** | ≥ 70% |

**配置覆盖率要求**:

```ini
# pytest.ini
[pytest]
min_coverage = 80
min_branch_coverage = 70
```

### 23.4.3 CI/CD 集成

**1. GitHub Actions**

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run tests
      run: pytest --cov=agent_framework --cov-report=xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v2
      with:
        file: ./coverage.xml
```

**2. GitLab CI**

```yaml
# .gitlab-ci.yml
test:
  stage: test
  image: python:3.11

  script:
    - pip install -r requirements.txt
    - pip install pytest pytest-cov
    - pytest --cov=agent_framework --cov-report=xml

  coverage: '/TOTAL.*\s+([\d\.]+)%/'
```

## 23.5 本章总结

### 核心要点

1. **单元测试实战**: pytest 基础、Agent 单元测试、Harness 工具测试、Loop 控制器测试、Graph 结构测试
2. **集成测试实战**: API 集成测试、数据库集成测试、工具集成测试
3. **E2E 测试实战**: Playwright E2E 测试、Agent 执行流程测试
4. **测试覆盖率实战**: 覆盖率报告、覆盖率要求、CI/CD 集成

### 实战技巧

- **单元测试**: 测试最小功能单元，使用 Mock 隔离依赖
- **集成测试**: 测试模块间协作，确保 API 正常工作
- **E2E 测试**: 测试完整用户流程，确保端到端功能正常
- **覆盖率**: 设置覆盖率要求，集成到 CI/CD 流程
- **Mock**: 使用 Mock 隔离外部依赖，提高测试速度

### 练习题

1. 为 Agent 工具编写单元测试
2. 为 Agent API 编写集成测试
3. 编写一个 E2E 测试
4. 配置 pytest-cov 生成覆盖率报告

### 下章预告

第24章将介绍 **Agent 部署实战**，包括：
- Docker 部署实战
- K8s 部署实战
- 监控与日志实战

---

**本章完**

**下一章**: [第24章：Agent 部署实战](./24-chapter23-testing-practice.md)
