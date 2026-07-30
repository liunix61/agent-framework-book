# 第15章：Agent 性能优化

## 本章目标

掌握 Agent 系统性能优化方法，包括性能分析、缓存优化、异步优化、并发优化。

## 前置知识

- **基础 性能**: 性能分析、性能指标
- **基础 Python/C++**: 异步编程、并发编程
- **基础 缓存**: Redis、内存缓存

## 15.1 性能分析

### 15.1.1 性能指标

**关键性能指标（KPI）**:

| 指标 | 说明 | 目标值 |
|------|------|--------|
| **QPS**（每秒查询数） | 每秒处理的请求数 | > 1000 |
| **响应时间**（RT） | 请求的平均响应时间 | < 100ms |
| **错误率** | 请求失败的比例 | < 0.1% |
| **吞吐量** | 每秒处理的请求数 | > 1000 |
| **资源利用率** | CPU、内存、磁盘、网络的使用率 | < 80% |

### 15.1.2 性能分析工具

**1. Python 性能分析**

```python
import cProfile
import pstats
from io import StringIO

def profile_function(func):
    """性能分析装饰器"""
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()

        result = func(*args, **kwargs)

        pr.disable()

        # 输出性能报告
        s = StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(20)

        print(s.getvalue())

        return result

    return wrapper


# 使用
@profile_function
def complex_task():
    """复杂任务"""
    import time
    time.sleep(1)
    return "完成"


complex_task()
```

**2. cProfile 使用**

```bash
# 运行性能分析
python -m cProfile -s cumulative complex_task.py

# 保存性能报告到文件
python -m cProfile -s cumulative -o profile.stats complex_task.py

# 分析性能报告
python -m pstats profile.stats
```

**3. Py-Spy（实时性能分析）**

```bash
# 安装 Py-Spy
pip install py-spy

# 运行性能分析
py-spy top --pid <pid>

# 保存性能报告
py-spy record -o profile.svg --pid <pid>
```

### 15.1.3 性能分析示例

**1. 分析 Agent 执行时间**

```python
import time
from functools import wraps

def measure_time(func):
    """测量执行时间装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        elapsed_time = end_time - start_time
        print(f"{func.__name__} 执行时间：{elapsed_time:.4f} 秒")

        return result

    return wrapper


@measure_time
def agent_task():
    """Agent 任务"""
    import time
    time.sleep(0.5)
    return "完成"


agent_task()
```

## 15.2 缓存优化

### 15.2.1 Redis 缓存

**1. 缓存 Agent 结果**

```python
import redis
import json
from typing import Optional

class AgentCache:
    """Agent 缓存"""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        """
        初始化缓存

        Args:
            host: Redis 主机
            port: Redis 端口
            db: Redis 数据库
        """
        self.redis = redis.Redis(host=host, port=port, db=db)

    def cache_result(
        self,
        task_id: str,
        result: dict,
        ttl: int = 3600
    ):
        """
        缓存结果

        Args:
            task_id: 任务 ID
            result: 结果
            ttl: 过期时间（秒）
        """
        key = f"agent:task:{task_id}"
        self.redis.setex(
            key,
            ttl,
            json.dumps(result)
        )

    def get_result(self, task_id: str) -> Optional[dict]:
        """
        获取缓存结果

        Args:
            task_id: 任务 ID

        Returns:
            结果
        """
        key = f"agent:task:{task_id}"
        cached_data = self.redis.get(key)

        if cached_data:
            return json.loads(cached_data)

        return None

    def invalidate_cache(self, task_id: str):
        """
        使缓存失效

        Args:
            task_id: 任务 ID
        """
        key = f"agent:task:{task_id}"
        self.redis.delete(key)


# 使用
cache = AgentCache()

# 缓存结果
cache.cache_result(
    task_id="task_123",
    result={"data": "Agent 结果"},
    ttl=3600
)

# 获取缓存结果
cached_result = cache.get_result("task_123")
print(f"缓存结果：{cached_result}")

# 使缓存失效
cache.invalidate_cache("task_123")
```

**2. 缓存 Agent 工具结果**

```python
from functools import wraps

class CachedTool:
    """缓存工具"""

    def __init__(self, cache: AgentCache, tool):
        """
        初始化缓存工具

        Args:
            cache: 缓存实例
            tool: 工具实例
        """
        self.cache = cache
        self.tool = tool

    def __call__(self, **kwargs):
        """调用工具"""
        # 生成缓存键
        cache_key = f"tool:{self.tool.name}:{str(kwargs)}"

        # 检查缓存
        cached_result = self.cache.get_result(cache_key)
        if cached_result:
            print(f"从缓存获取结果：{cache_key}")
            return cached_result["result"]

        # 调用工具
        result = self.tool.execute(**kwargs)

        # 缓存结果
        self.cache.cache_result(
            task_id=cache_key,
            result={"result": result},
            ttl=3600
        )

        return result


# 使用
tool = GetWeatherTool()
cached_tool = CachedTool(cache, tool)

result = cached_tool(city="北京")
print(f"结果：{result}")
```

### 15.2.2 内存缓存

**1. LRU 缓存**

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_function(param: str) -> str:
    """
    耗时函数

    Args:
        param: 参数

    Returns:
        结果
    """
    import time
    time.sleep(1)
    return f"结果：{param}"


# 使用
result1 = expensive_function("param1")
result2 = expensive_function("param1")  # 从缓存获取

print(f"结果1：{result1}")
print(f"结果2：{result2}")
```

**2. TTL 缓存**

```python
import time
from typing import Dict, Any

class TTLCache:
    """TTL 缓存"""

    def __init__(self, max_size: int = 128, default_ttl: int = 3600):
        """
        初始化 TTL 缓存

        Args:
            max_size: 最大缓存大小
            default_ttl: 默认过期时间（秒）
        """
        self.cache: Dict[str, tuple] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存

        Args:
            key: 缓存键

        Returns:
            缓存值
        """
        if key not in self.cache:
            return None

        value, timestamp = self.cache[key]

        # 检查是否过期
        if time.time() - timestamp > self.default_ttl:
            del self.cache[key]
            return None

        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        设置缓存

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）
        """
        if ttl is None:
            ttl = self.default_ttl

        self.cache[key] = (value, time.time() + ttl)

        # 检查缓存大小
        if len(self.cache) > self.max_size:
            # 删除最旧的缓存
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]

    def clear(self):
        """清空缓存"""
        self.cache.clear()


# 使用
ttl_cache = TTLCache(default_ttl=60)

# 设置缓存
ttl_cache.set("key1", "value1", ttl=120)
ttl_cache.set("key2", "value2")

# 获取缓存
value1 = ttl_cache.get("key1")
value2 = ttl_cache.get("key2")

print(f"key1: {value1}")
print(f"key2: {value2}")
```

## 15.3 异步优化

### 15.3.1 异步编程

**1. Asyncio 基础**

```python
import asyncio
import time

async def async_task(name: str, delay: float):
    """
    异步任务

    Args:
        name: 任务名称
        delay: 延迟时间（秒）
    """
    print(f"{name} 开始")
    await asyncio.sleep(delay)
    print(f"{name} 完成")
    return f"{name} 的结果"


async def main():
    """主函数"""
    print("开始执行异步任务...")

    # 并发执行多个异步任务
    tasks = [
        async_task("任务1", 1),
        async_task("任务2", 2),
        async_task("任务3", 1.5)
    ]

    # 等待所有任务完成
    results = await asyncio.gather(*tasks)

    print(f"所有任务完成：{results}")


# 使用
asyncio.run(main())
```

**2. 异步 Agent 执行**

```python
import asyncio
from typing import List

class AsyncAgent:
    """异步 Agent"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id

    async def execute_task(self, task: str) -> dict:
        """
        执行任务

        Args:
            task: 任务

        Returns:
            执行结果
        """
        # 模拟异步操作
        await asyncio.sleep(1)
        return {
            "agent_id": self.agent_id,
            "task": task,
            "result": f"{task} 的结果"
        }


async def batch_execute_agents(agents: List[AsyncAgent], tasks: List[str]):
    """
    批量执行 Agent 任务

    Args:
        agents: Agent 列表
        tasks: 任务列表
    """
    # 创建任务
    agent_tasks = [
        agent.execute_task(task)
        for agent, task in zip(agents, tasks)
    ]

    # 并发执行
    results = await asyncio.gather(*agent_tasks)

    return results


async def main():
    """主函数"""
    # 创建 Agent
    agents = [
        AsyncAgent("agent_1"),
        AsyncAgent("agent_2"),
        AsyncAgent("agent_3")
    ]

    # 任务列表
    tasks = ["任务1", "任务2", "任务3"]

    # 批量执行
    results = await batch_execute_agents(agents, tasks)

    # 输出结果
    for result in results:
        print(result)


# 使用
asyncio.run(main())
```

### 15.3.2 异步 API

**1. FastAPI 异步 API**

```python
from fastapi import FastAPI
from typing import List
import asyncio

app = FastAPI()

@app.get("/agents")
async def get_agents():
    """获取所有 Agent（异步）"""
    # 模拟异步操作
    await asyncio.sleep(0.1)

    return {
        "agents": [
            {"id": "agent_1", "name": "Agent 1"},
            {"id": "agent_2", "name": "Agent 2"},
            {"id": "agent_3", "name": "Agent 3"}
        ]
    }

@app.post("/agents/{agent_id}/execute")
async def execute_agent(agent_id: str, task: str):
    """执行 Agent（异步）"""
    # 模拟异步操作
    await asyncio.sleep(1)

    return {
        "agent_id": agent_id,
        "task": task,
        "result": f"{task} 的结果"
    }
```

## 15.4 并发优化

### 15.4.1 并发编程

**1. 线程池**

```python
from concurrent.futures import ThreadPoolExecutor
import time

def task(name: str, delay: float) -> str:
    """
    任务函数

    Args:
        name: 任务名称
        delay: 延迟时间（秒）

    Returns:
        结果
    """
    time.sleep(delay)
    return f"{name} 完成"


def main():
    """主函数"""
    # 创建线程池
    with ThreadPoolExecutor(max_workers=5) as executor:
        # 提交任务
        futures = [
            executor.submit(task, f"任务{i}", 1)
            for i in range(1, 6)
        ]

        # 获取结果
        results = [future.result() for future in futures]

    print(f"所有任务完成：{results}")


# 使用
main()
```

**2. 进程池**

```python
from concurrent.futures import ProcessPoolExecutor
import time

def cpu_intensive_task(name: str) -> str:
    """
    CPU 密集型任务

    Args:
        name: 任务名称

    Returns:
        结果
    """
    # CPU 密集型操作
    result = sum(i ** 2 for i in range(1000000))
    return f"{name} 完成，结果：{result}"


def main():
    """主函数"""
    # 创建进程池
    with ProcessPoolExecutor(max_workers=4) as executor:
        # 提交任务
        futures = [
            executor.submit(cpu_intensive_task, f"任务{i}")
            for i in range(1, 5)
        ]

        # 获取结果
        results = [future.result() for future in futures]

    print(f"所有任务完成：{results}")


# 使用
main()
```

### 15.4.2 并发 Agent

**1. 并发 Agent 执行**

```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

class ConcurrentAgent:
    """并发 Agent"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id

    def execute_task(self, task: str) -> dict:
        """
        执行任务

        Args:
            task: 任务

        Returns:
            执行结果
        """
        import time
        time.sleep(1)
        return {
            "agent_id": self.agent_id,
            "task": task,
            "result": f"{task} 的结果"
        }

    def execute_tasks_concurrently(self, tasks: List[str]) -> List[dict]:
        """
        并发执行任务

        Args:
            tasks: 任务列表

        Returns:
            结果列表
        """
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(self.execute_task, task)
                for task in tasks
            ]

            results = [future.result() for future in futures]

        return results


# 使用
agent = ConcurrentAgent("agent_1")

tasks = ["任务1", "任务2", "任务3", "任务4", "任务5"]

results = agent.execute_tasks_concurrently(tasks)

for result in results:
    print(result)
```

## 15.5 本章总结

### 核心要点

1. **性能分析**: 性能指标、性能分析工具（cProfile、Py-Spy）
2. **缓存优化**: Redis 缓存、内存缓存（LRU、TTL）
3. **异步优化**: Asyncio、异步 API
4. **并发优化**: 线程池、进程池、并发 Agent

### 实战技巧

- **性能分析**: 使用 cProfile、Py-Spy 分析性能瓶颈
- **缓存优化**: 使用 Redis 缓存 Agent 结果，减少重复计算
- **异步优化**: 使用 Asyncio 提高并发能力
- **并发优化**: 使用线程池和进程池提高性能
- **监控**: 监控 QPS、响应时间、错误率

### 练习题

1. 使用 cProfile 分析 Agent 执行性能
2. 实现 Redis 缓存 Agent 结果
3. 实现异步 Agent 执行
4. 实现并发 Agent 执行

### 下章预告

第16章将介绍 **Agent 应用案例**，包括：
- Agent 在写作领域的应用
- Agent 在量化交易中的应用
- Agent 在代码审查中的应用

---

**本章完**

**下一章**: [第16章：Agent 应用案例](./16-chapter16-applications.md)
