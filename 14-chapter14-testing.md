# 第14章：Agent 测试

## 本章目标

掌握 Agent 系统测试方法，包括单元测试、集成测试、E2E 测试、测试覆盖率。

## 前置知识

- **基础 测试**: pytest、unittest
- **基础 开发**: Python/C++ 测试实践
- **基础 CI/CD**: GitHub Actions、GitLab CI

## 14.1 测试类型

### 14.1.1 测试金字塔

**测试金字塔**:

```
         /\
        /E2E\
       /------\
      / 集成测试 \
     /----------\
    /   单元测试  \
   /--------------\
  /                \
```

**测试层级**:

1. **单元测试（Unit Tests）**: 测试最小功能单元
2. **集成测试（Integration Tests）**: 测试模块间协作
3. **E2E 测试（End-to-End Tests）**: 测试完整用户流程

### 14.1.2 测试对比

| 测试类型 | 测试范围 | 执行速度 | 维护成本 | 适用场景 |
|---------|---------|---------|---------|---------|
| **单元测试** | 单个函数/方法 | 快 | 低 | 单个功能 |
| **集成测试** | 模块间协作 | 中等 | 中等 | API、数据库 |
| **E2E 测试** | 完整用户流程 | 慢 | 高 | 关键流程 |

## 14.2 单元测试

### 14.2.1 Pytest 基础

**1. 安装 Pytest**

```bash
pip install pytest pytest-cov pytest-mock
```

**2. 测试示例**

```python
# test_calculator.py
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

**3. 运行测试**

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

### 14.2.2 测试 Agent 工具

**1. 测试 Harness 工具**

```python
# tests/test_harness.py
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
```

**2. 测试 Loop 控制器**

```python
# tests/test_loop.py
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
```

### 14.2.3 Mock 测试

**1. Mock 模块**

```python
from unittest.mock import Mock, patch
import requests

def test_api_call():
    """测试 API 调用"""
    # Mock HTTP 请求
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}

    with patch('requests.get', return_value=mock_response) as mock_get:
        response = requests.get("http://example.com/api")

        assert mock_get.called
        assert response.status_code == 200
        assert response.json() == {"data": "test"}
```

**2. Mock 数据库**

```python
from unittest.mock import Mock, MagicMock
import psycopg2

def test_database_query():
    """测试数据库查询"""
    # Mock 数据库连接
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [("Alice", 30), ("Bob", 25)]

    with patch('psycopg2.connect', return_value=mock_conn):
        conn = psycopg2.connect("postgresql://localhost/test")
        cursor = conn.cursor()

        cursor.execute("SELECT name, age FROM users")
        results = cursor.fetchall()

        assert len(results) == 2
        assert results[0] == ("Alice", 30)
```

## 14.3 集成测试

### 14.3.1 API 集成测试

**1. 测试 Agent API**

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

def test_agent_execute():
    """测试 Agent 执行"""
    response = client.post(
        "/api/agent/execute",
        json={
            "task": "写一首诗",
            "agent_id": "writer"
        }
    )

    assert response.status_code == 200
    assert "result" in response.json()

def test_agent_execute_invalid_task():
    """测试无效任务"""
    response = client.post(
        "/api/agent/execute",
        json={
            "task": "",
            "agent_id": "writer"
        }
    )

    assert response.status_code == 400
```

### 14.3.2 数据库集成测试

**1. 测试数据库操作**

```python
# tests/test_database.py
import pytest
from agent_framework.database import DatabaseManager

@pytest.fixture
def db_manager():
    """数据库管理器 fixture"""
    db_manager = DatabaseManager(
        database_url="postgresql://localhost/test"
    )
    yield db_manager
    db_manager.close()

def test_create_user(db_manager):
    """测试创建用户"""
    user_id = db_manager.create_user(
        username="test_user",
        email="test@example.com",
        password="hashed_password"
    )

    assert user_id is not None

def test_get_user(db_manager):
    """测试获取用户"""
    user_id = db_manager.create_user(
        username="test_user",
        email="test@example.com",
        password="hashed_password"
    )

    user = db_manager.get_user(user_id)
    assert user is not None
    assert user["username"] == "test_user"
```

### 14.3.3 工具集成测试

**1. 测试工具调用链**

```python
# tests/test_tools_integration.py
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
```

## 14.4 E2E 测试

### 14.4.1 E2E 测试框架

**1. 使用 Playwright**

```python
# tests/e2e/test_agent_flow.py
from playwright.sync_api import Page, expect

def test_agent_flow(page: Page):
    """测试 Agent 完整流程"""
    # 访问首页
    page.goto("http://localhost:3000")

    # 填写任务
    page.fill('input[name="task"]', "写一首诗")
    page.click('button[type="submit"]')

    # 等待结果
    page.wait_for_selector('.result')

    # 验证结果
    result = page.text_content('.result')
    assert result is not None
    assert len(result) > 0
```

### 14.4.2 测试关键流程

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
```

## 14.5 测试覆盖率

### 14.5.1 生成覆盖率报告

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

### 14.5.2 覆盖率要求

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

### 14.5.3 CI/CD 集成

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

## 14.6 本章总结

### 核心要点

1. **测试类型**: 单元测试、集成测试、E2E 测试
2. **单元测试**: Pytest 基础、Mock 测试
3. **集成测试**: API 测试、数据库测试、工具调用测试
4. **E2E 测试**: Playwright 测试、关键流程测试
5. **测试覆盖率**: 覆盖率报告、CI/CD 集成

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

第15章将介绍 **Agent 性能优化**，包括：
- 性能分析
- 缓存优化
- 异步优化
- 并发优化

---

**本章完**

**下一章**: [第15章：Agent 性能优化](./15-chapter15-performance.md)
