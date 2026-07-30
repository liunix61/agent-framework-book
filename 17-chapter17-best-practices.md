# 第17章：Agent 最佳实践

## 本章目标

掌握 Agent 开发和运维的最佳实践，包括设计原则、开发流程、运维最佳实践。

## 前置知识

- **基础 Agent**: Harness、Loop、Graph
- **基础 开发**: Python/C++、测试、部署
- **基础 运维**: 监控、日志、安全

## 17.1 Agent 设计原则

### 17.1.1 SOLID 原则

**SOLID 原则在 Agent 开发中的应用**:

**1. 单一职责原则（Single Responsibility Principle）**

```python
class Agent:
    """Agent 基类（单一职责）"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id

    def execute(self, task: str) -> str:
        """执行任务"""
        raise NotImplementedError


class ToolRegistry:
    """工具注册器（单一职责）"""

    def __init__(self):
        self.tools = {}

    def register_tool(self, name: str, tool_func):
        """注册工具"""
        self.tools[name] = tool_func

    def get_tool(self, name: str):
        """获取工具"""
        return self.tools.get(name)


class ContextManager:
    """上下文管理器（单一职责）"""

    def __init__(self):
        self.context = {}

    def add_context(self, key: str, value: Any):
        """添加上下文"""
        self.context[key] = value

    def get_context(self, key: str, default: Any = None):
        """获取上下文"""
        return self.context.get(key, default)
```

**2. 开闭原则（Open/Closed Principle）**

```python
class Agent:
    """Agent 基类（开闭原则）"""

    def execute(self, task: str) -> str:
        """执行任务"""
        raise NotImplementedError


class LoggingAgent(Agent):
    """日志 Agent（扩展功能，不修改基类）"""

    def execute(self, task: str) -> str:
        """执行任务"""
        print(f"[日志] 执行任务：{task}")
        result = super().execute(task)
        print(f"[日志] 任务完成：{result}")
        return result


class MetricsAgent(Agent):
    """指标 Agent（扩展功能，不修改基类）"""

    def execute(self, task: str) -> str:
        """执行任务"""
        import time
        start_time = time.time()

        result = super().execute(task)

        elapsed_time = time.time() - start_time
        print(f"[指标] 任务执行时间：{elapsed_time:.4f}秒")

        return result
```

**3. 里氏替换原则（Liskov Substitution Principle）**

```python
class Agent:
    """Agent 基类"""

    def execute(self, task: str) -> str:
        """执行任务"""
        raise NotImplementedError


class SimpleAgent(Agent):
    """简单 Agent"""

    def execute(self, task: str) -> str:
        return f"简单 Agent 执行：{task}"


class AdvancedAgent(Agent):
    """高级 Agent（可以替换 SimpleAgent）"""

    def execute(self, task: str) -> str:
        return f"高级 Agent 执行：{task}"


# 使用
def process_agent(agent: Agent, task: str) -> str:
    """处理 Agent"""
    return agent.execute(task)


# 可以替换 SimpleAgent 和 AdvancedAgent
result1 = process_agent(SimpleAgent(), "任务1")
result2 = process_agent(AdvancedAgent(), "任务2")

print(result1)  # 简单 Agent 执行：任务1
print(result2)  # 高级 Agent 执行：任务2
```

**4. 接口隔离原则（Interface Segregation Principle）**

```python
class AgentInterface:
    """Agent 接口（接口隔离）"""

    def execute(self, task: str) -> str:
        """执行任务"""
        pass

    def stop(self):
        """停止任务"""
        pass


class LoggingAgent(AgentInterface):
    """日志 Agent"""

    def execute(self, task: str) -> str:
        """执行任务"""
        print(f"执行任务：{task}")
        return f"结果：{task}"

    def stop(self):
        """停止任务"""
        print("停止任务")


class MetricsAgent(AgentInterface):
    """指标 Agent"""

    def execute(self, task: str) -> str:
        """执行任务"""
        print(f"执行任务：{task}")
        return f"结果：{task}"

    def stop(self):
        """停止任务"""
        print("停止任务")
```

**5. 依赖倒置原则（Dependency Inversion Principle）**

```python
class Tool:
    """工具（依赖抽象）"""

    def execute(self, **kwargs) -> Any:
        """执行工具"""
        raise NotImplementedError


class ToolRegistry:
    """工具注册器（依赖抽象）"""

    def __init__(self):
        self.tools = {}

    def register_tool(self, tool: Tool):
        """注册工具"""
        self.tools[tool.name] = tool

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """执行工具"""
        tool = self.tools.get(tool_name)
        if tool:
            return tool.execute(**kwargs)
        raise ValueError(f"工具 {tool_name} 不存在")


# 使用
class GetWeatherTool(Tool):
    """获取天气工具"""

    def __init__(self):
        self.name = "get_weather"

    def execute(self, city: str) -> str:
        """执行工具"""
        return f"{city}今天天气晴"


class SearchWebTool(Tool):
    """搜索网页工具"""

    def __init__(self):
        self.name = "search_web"

    def execute(self, query: str) -> str:
        """执行工具"""
        return f"搜索结果：{query}"


# 依赖抽象
registry = ToolRegistry()
registry.register_tool(GetWeatherTool())
registry.register_tool(SearchWebTool())

result1 = registry.execute_tool("get_weather", city="北京")
result2 = registry.execute_tool("search_web", query="AI Agent")

print(result1)  # 北京今天天气晴
print(result2)  # 搜索结果：AI Agent
```

### 17.1.2 设计模式

**1. 工厂模式**

```python
class AgentFactory:
    """Agent 工厂"""

    @staticmethod
    def create_agent(agent_type: str) -> Agent:
        """创建 Agent"""
        if agent_type == "simple":
            return SimpleAgent()
        elif agent_type == "advanced":
            return AdvancedAgent()
        elif agent_type == "logging":
            return LoggingAgent()
        else:
            raise ValueError(f"未知的 Agent 类型：{agent_type}")


# 使用
agent = AgentFactory.create_agent("logging")
result = agent.execute("任务")
```

**2. 策略模式**

```python
class Agent:
    """Agent（策略模式）"""

    def __init__(self, strategy: AgentStrategy):
        """初始化 Agent"""
        self.strategy = strategy

    def execute(self, task: str) -> str:
        """执行任务"""
        return self.strategy.execute(task)


class AgentStrategy:
    """Agent 策略接口"""

    def execute(self, task: str) -> str:
        """执行策略"""
        raise NotImplementedError


class SimpleStrategy(AgentStrategy):
    """简单策略"""

    def execute(self, task: str) -> str:
        return f"简单策略执行：{task}"


class AdvancedStrategy(AgentStrategy):
    """高级策略"""

    def execute(self, task: str) -> str:
        return f"高级策略执行：{task}"


# 使用
agent1 = Agent(SimpleStrategy())
agent2 = Agent(AdvancedStrategy())

print(agent1.execute("任务1"))  # 简单策略执行：任务1
print(agent2.execute("任务2"))  # 高级策略执行：任务2
```

**3. 装饰器模式**

```python
def logging_decorator(func):
    """日志装饰器"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[日志] 开始执行：{func.__name__}")
        result = func(*args, **kwargs)
        print(f"[日志] 执行完成：{func.__name__}")
        return result

    return wrapper


def metrics_decorator(func):
    """指标装饰器"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        import time
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        print(f"[指标] 执行时间：{elapsed_time:.4f}秒")
        return result

    return wrapper


@logging_decorator
@metrics_decorator
def execute_task(task: str) -> str:
    """执行任务"""
    return f"任务结果：{task}"


# 使用
result = execute_task("任务")
```

## 17.2 Agent 开发流程

### 17.2.1 开发阶段

**1. 需求分析**

```python
class RequirementAnalyzer:
    """需求分析器"""

    def analyze(self, user_requirement: str) -> dict:
        """
        分析需求

        Args:
            user_requirement: 用户需求

        Returns:
            需求分析结果
        """
        # 分析需求
        requirements = {
            "user_requirement": user_requirement,
            "agent_type": self._determine_agent_type(user_requirement),
            "tools": self._determine_tools(user_requirement),
            "context": self._determine_context(user_requirement),
            "performance_requirements": self._determine_performance(user_requirement)
        }

        return requirements

    def _determine_agent_type(self, requirement: str) -> str:
        """确定 Agent 类型"""
        if "写" in requirement:
            return "writing"
        elif "交易" in requirement or "策略" in requirement:
            return "quantitative"
        elif "审查" in requirement or "检查" in requirement:
            return "review"
        else:
            return "general"

    def _determine_tools(self, requirement: str) -> list:
        """确定工具"""
        tools = []

        if "写" in requirement:
            tools.append("llm_api")

        if "交易" in requirement or "策略" in requirement:
            tools.append("data_fetcher")
            tools.append("strategy_engine")

        if "审查" in requirement or "检查" in requirement:
            tools.append("linter")
            tools.append("tester")

        return tools

    def _determine_context(self, requirement: str) -> dict:
        """确定上下文"""
        return {
            "language": "python",
            "framework": "fastapi",
            "database": "postgresql"
        }

    def _determine_performance(self, requirement: str) -> dict:
        """确定性能要求"""
        return {
            "qps": 100,
            "latency": 100  # ms
        }


# 使用
analyzer = RequirementAnalyzer()

requirement = "写一篇关于 AI Agent 的文章"
requirements = analyzer.analyze(requirement)

print(f"Agent 类型：{requirements['agent_type']}")
print(f"工具：{requirements['tools']}")
print(f"上下文：{requirements['context']}")
print(f"性能要求：{requirements['performance_requirements']}")
```

**2. 设计阶段**

```python
class AgentDesigner:
    """Agent 设计器"""

    def design(self, requirements: dict) -> dict:
        """
        设计 Agent

        Args:
            requirements: 需求

        Returns:
            设计方案
        """
        design = {
            "agent_id": self._generate_agent_id(requirements),
            "name": self._generate_agent_name(requirements),
            "description": self._generate_description(requirements),
            "architecture": self._determine_architecture(requirements),
            "components": self._determine_components(requirements),
            "interfaces": self._determine_interfaces(requirements),
            "data_flow": self._determine_data_flow(requirements)
        }

        return design

    def _generate_agent_id(self, requirements: dict) -> str:
        """生成 Agent ID"""
        return f"agent_{requirements['agent_type']}_{int(time.time())}"

    def _generate_agent_name(self, requirements: dict) -> str:
        """生成 Agent 名称"""
        return f"{requirements['agent_type']} Agent"

    def _generate_description(self, requirements: dict) -> str:
        """生成描述"""
        return f"负责{requirements['user_requirement']}的 Agent"

    def _determine_architecture(self, requirements: dict) -> str:
        """确定架构"""
        return "graph"

    def _determine_components(self, requirements: dict) -> list:
        """确定组件"""
        return requirements['tools']

    def _determine_interfaces(self, requirements: dict) -> list:
        """确定接口"""
        return ["execute", "stop", "get_status"]

    def _determine_data_flow(self, requirements: dict) -> dict:
        """确定数据流"""
        return {
            "input": ["task"],
            "output": ["result"],
            "intermediate": ["processed_data"]
        }


# 使用
analyzer = RequirementAnalyzer()
requirements = analyzer.analyze("写一篇关于 AI Agent 的文章")

designer = AgentDesigner()
design = designer.design(requirements)

print(f"Agent ID：{design['agent_id']}")
print(f"Agent 名称：{design['name']}")
print(f"架构：{design['architecture']}")
print(f"组件：{design['components']}")
print(f"接口：{design['interfaces']}")
```

**3. 实现阶段**

```python
class AgentDeveloper:
    """Agent 开发者"""

    def develop(self, design: dict) -> Agent:
        """
        开发 Agent

        Args:
            design: 设计方案

        Returns:
            Agent 实例
        """
        # 创建 Agent
        agent = Agent(
            agent_id=design['agent_id'],
            name=design['name'],
            description=design['description'],
            architecture=design['architecture']
        )

        # 注册组件
        for component in design['components']:
            agent.register_component(component)

        # 实现接口
        agent.implement_interfaces(design['interfaces'])

        return agent


# 使用
designer = AgentDesigner()
requirements = analyzer.analyze("写一篇关于 AI Agent 的文章")
design = designer.design(requirements)

developer = AgentDeveloper()
agent = developer.develop(design)

result = agent.execute("写一篇关于 AI Agent 的文章")
print(result)
```

### 17.2.2 开发工作流

**1. Git 工作流**

```bash
# 创建功能分支
git checkout -b feature/agent-writing

# 提交代码
git add .
git commit -m "feat: 实现写作 Agent"

# 推送到远程
git push origin feature/agent-writing

# 创建 Pull Request
# 代码审查、合并到 main 分支
```

**2. CI/CD 工作流**

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

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

    - name: Upload coverage
      uses: codecov/codecov-action@v2

  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Build Docker image
      run: docker build -t agent-framework:latest .

    - name: Push to Docker Hub
      run: docker push agent-framework:latest
```

## 17.3 Agent 运维最佳实践

### 17.3.1 监控

**1. 关键指标监控**

```python
import time
from typing import Dict, Any

class AgentMonitor:
    """Agent 监控器"""

    def __init__(self):
        """初始化监控器"""
        self.metrics = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_time": 0.0,
            "avg_time": 0.0,
            "error_rate": 0.0
        }

    def record_execution(self, success: bool, elapsed_time: float):
        """
        记录执行

        Args:
            success: 是否成功
            elapsed_time: 执行时间
        """
        self.metrics["total_executions"] += 1

        if success:
            self.metrics["successful_executions"] += 1
        else:
            self.metrics["failed_executions"] += 1

        self.metrics["total_time"] += elapsed_time
        self.metrics["avg_time"] = self.metrics["total_time"] / self.metrics["total_executions"]
        self.metrics["error_rate"] = self.metrics["failed_executions"] / self.metrics["total_executions"]

    def get_metrics(self) -> Dict[str, Any]:
        """获取指标"""
        return self.metrics

    def get_status(self) -> str:
        """获取状态"""
        if self.metrics["error_rate"] > 0.1:
            return "critical"
        elif self.metrics["error_rate"] > 0.05:
            return "warning"
        else:
            return "healthy"


# 使用
monitor = AgentMonitor()

# 模拟执行
for i in range(10):
    success = i % 3 != 0  # 2/3 成功
    elapsed_time = 1.0 + i * 0.1
    monitor.record_execution(success, elapsed_time)

print(f"总执行次数：{monitor.metrics['total_executions']}")
print(f"成功次数：{monitor.metrics['successful_executions']}")
print(f"失败次数：{monitor.metrics['failed_executions']}")
print(f"平均执行时间：{monitor.metrics['avg_time']:.2f}秒")
print(f"错误率：{monitor.metrics['error_rate']:.2%}")
print(f"状态：{monitor.get_status()}")
```

**2. Prometheus 监控集成**

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# 定义指标
execution_counter = Counter('agent_executions_total', 'Total number of agent executions')
execution_duration = Histogram('agent_execution_duration_seconds', 'Agent execution duration')
error_counter = Counter('agent_errors_total', 'Total number of agent errors', ['error_type'])


class AgentMonitor:
    """Agent 监控器（Prometheus）"""

    def __init__(self):
        """初始化监控器"""
        self.execution_counter = execution_counter
        self.execution_duration = execution_duration
        self.error_counter = error_counter

    def record_execution(self, success: bool, elapsed_time: float, error_type: str = None):
        """
        记录执行

        Args:
            success: 是否成功
            elapsed_time: 执行时间
            error_type: 错误类型
        """
        # 记录执行次数
        self.execution_counter.inc()

        # 记录执行时间
        self.execution_duration.observe(elapsed_time)

        # 记录错误
        if not success:
            self.error_counter.labels(error_type=error_type).inc()


# 使用
monitor = AgentMonitor()

# 模拟执行
for i in range(10):
    success = i % 3 != 0
    elapsed_time = 1.0 + i * 0.1
    error_type = "timeout" if not success else None
    monitor.record_execution(success, elapsed_time, error_type)
```

### 17.3.2 日志

**1. 结构化日志**

```python
import logging
import json
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("agent_framework")


class AgentLogger:
    """Agent 日志记录器"""

    def __init__(self, agent_id: str):
        """
        初始化日志记录器

        Args:
            agent_id: Agent ID
        """
        self.agent_id = agent_id

    def log_execution_start(self, task: str):
        """记录执行开始"""
        log_data = {
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "event": "execution_start",
            "task": task
        }

        logger.info(json.dumps(log_data))

    def log_execution_success(self, task: str, elapsed_time: float, result: str):
        """记录执行成功"""
        log_data = {
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "event": "execution_success",
            "task": task,
            "elapsed_time": elapsed_time,
            "result": result
        }

        logger.info(json.dumps(log_data))

    def log_execution_failure(self, task: str, elapsed_time: float, error: str):
        """记录执行失败"""
        log_data = {
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "event": "execution_failure",
            "task": task,
            "elapsed_time": elapsed_time,
            "error": error
        }

        logger.error(json.dumps(log_data))


# 使用
logger = AgentLogger(agent_id="agent_1")

logger.log_execution_start("写一篇关于 AI Agent 的文章")

try:
    time.sleep(1)
    result = "文章完成"
    logger.log_execution_success("写一篇关于 AI Agent 的文章", 1.0, result)
except Exception as e:
    logger.log_execution_failure("写一篇关于 AI Agent 的文章", 0, str(e))
```

**2. 日志聚合**

```python
import logging
from logging.handlers import RotatingFileHandler
import json

# 配置日志
logger = logging.getLogger("agent_framework")

# 日志文件（轮转）
file_handler = RotatingFileHandler(
    'agent_framework.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)

# 日志格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class AgentLogger:
    """Agent 日志记录器（聚合）"""

    def __init__(self, agent_id: str):
        """
        初始化日志记录器

        Args:
            agent_id: Agent ID
        """
        self.agent_id = agent_id

    def log_execution_start(self, task: str):
        """记录执行开始"""
        log_data = {
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "event": "execution_start",
            "task": task
        }

        logger.info(json.dumps(log_data))

    def log_execution_success(self, task: str, elapsed_time: float, result: str):
        """记录执行成功"""
        log_data = {
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "event": "execution_success",
            "task": task,
            "elapsed_time": elapsed_time,
            "result": result
        }

        logger.info(json.dumps(log_data))

    def log_execution_failure(self, task: str, elapsed_time: float, error: str):
        """记录执行失败"""
        log_data = {
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "event": "execution_failure",
            "task": task,
            "elapsed_time": elapsed_time,
            "error": error
        }

        logger.error(json.dumps(log_data))


# 使用
logger = AgentLogger(agent_id="agent_1")

logger.log_execution_start("写一篇关于 AI Agent 的文章")

try:
    time.sleep(1)
    result = "文章完成"
    logger.log_execution_success("写一篇关于 AI Agent 的文章", 1.0, result)
except Exception as e:
    logger.log_execution_failure("写一篇关于 AI Agent 的文章", 0, str(e))
```

### 17.3.3 故障排查

**1. 调试工具**

```python
import pdb
import time

def debug_agent_execution(agent, task: str):
    """调试 Agent 执行"""

    # 开始调试
    pdb.set_trace()

    # 执行任务
    result = agent.execute(task)

    return result


# 使用
def execute_task(task: str) -> str:
    """执行任务"""
    agent = Agent(agent_id="agent_1")
    return agent.execute(task)


# 调试执行
result = debug_agent_execution(execute_task, "任务")
```

**2. 日志分析**

```python
import re
from typing import List, Dict, Any

class LogAnalyzer:
    """日志分析器"""

    def __init__(self, log_file: str):
        """
        初始化日志分析器

        Args:
            log_file: 日志文件路径
        """
        self.log_file = log_file

    def analyze_errors(self) -> List[Dict[str, Any]]:
        """分析错误"""
        errors = []

        with open(self.log_file, 'r') as f:
            for line in f:
                # 匹配错误日志
                if "error" in line.lower():
                    error_data = {
                        "timestamp": self._extract_timestamp(line),
                        "message": line.strip(),
                        "level": "error"
                    }
                    errors.append(error_data)

        return errors

    def analyze_performance(self) -> Dict[str, Any]:
        """分析性能"""
        execution_times = []

        with open(self.log_file, 'r') as f:
            for line in f:
                # 匹配执行时间
                match = re.search(r'execution_time: (\d+\.\d+)', line)
                if match:
                    execution_times.append(float(match.group(1)))

        if execution_times:
            return {
                "count": len(execution_times),
                "min": min(execution_times),
                "max": max(execution_times),
                "avg": sum(execution_times) / len(execution_times),
                "p95": self._percentile(execution_times, 95)
            }

        return {}

    def _extract_timestamp(self, line: str) -> str:
        """提取时间戳"""
        match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', line)
        return match.group(1) if match else ""

    def _percentile(self, data: List[float], percentile: int) -> float:
        """计算百分位数"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[index]


# 使用
analyzer = LogAnalyzer("agent_framework.log")

# 分析错误
errors = analyzer.analyze_errors()
print(f"错误数量：{len(errors)}")

# 分析性能
performance = analyzer.analyze_performance()
print(f"性能统计：{performance}")
```

## 17.4 本章总结

### 核心要点

1. **设计原则**: SOLID 原则（单一职责、开闭原则、里氏替换、接口隔离、依赖倒置）
2. **设计模式**: 工厂模式、策略模式、装饰器模式
3. **开发流程**: 需求分析、设计、实现、CI/CD
4. **运维最佳实践**: 监控、日志、故障排查

### 实战技巧

- **设计原则**: 使用 SOLID 原则设计 Agent
- **设计模式**: 使用工厂模式创建 Agent、策略模式实现不同策略
- **开发流程**: 遵循 Git 工作流、CI/CD 流程
- **监控**: 监控关键指标（QPS、响应时间、错误率）
- **日志**: 使用结构化日志、日志聚合
- **故障排查**: 使用调试工具、日志分析

### 练习题

1. 使用 SOLID 原则设计一个 Agent 系统
2. 使用工厂模式创建 Agent
3. 实现一个 Agent 监控器
4. 实现一个日志分析器

### 下章预告

第18章将介绍 **Agent 未来展望**，包括：
- Agent 技术趋势
- Agent 应用拓展
- Agent 挑战与机遇

---

**本章完**

**下一章**: [第18章：Agent 未来展望](./18-chapter18-future.md)
