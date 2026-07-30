# 第21章：Agent 性能优化实战

## 本章目标

通过实战项目，掌握 Agent 性能优化的方法。

## 前置知识

- **基础 性能**: 性能分析、性能指标
- **基础 Agent**: Harness、Loop、Graph
- **基础 优化**: 缓存、异步、并发

## 21.1 性能分析实战

### 21.1.1 性能分析工具

**1. cProfile 使用**

```python
import cProfile
import pstats
from io import StringIO

# 定义待分析的函数
def complex_agent_task():
    """复杂 Agent 任务"""
    import time
    time.sleep(1)
    return "完成"


# 性能分析
pr = cProfile.Profile()
pr.enable()

complex_agent_task()

pr.disable()

# 输出性能报告
s = StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
ps.print_stats(20)

print(s.getvalue())
```

**2. Py-Spy 使用**

```bash
# 安装 Py-Spy
pip install py-spy

# 运行性能分析
py-spy top --pid <pid>

# 保存性能报告
py-spy record -o profile.svg --pid <pid>
```

**3. 性能分析脚本**

```python
import time
from typing import Dict, Any
import cProfile

class PerformanceAnalyzer:
    """性能分析器"""

    def __init__(self):
        """初始化性能分析器"""
        self.metrics = {}

    def analyze_agent_execution(self, agent, task: str) -> Dict[str, Any]:
        """
        分析 Agent 执行性能

        Args:
            agent: Agent 实例
            task: 任务

        Returns:
            性能指标
        """
        # 创建性能分析器
        pr = cProfile.Profile()

        # 开始性能分析
        pr.enable()

        # 执行 Agent
        start_time = time.time()
        result = agent.execute(task)
        end_time = time.time()

        # 停止性能分析
        pr.disable()

        # 计算执行时间
        elapsed_time = end_time - start_time

        # 获取性能报告
        s = StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(20)

        # 返回性能指标
        return {
            "elapsed_time": elapsed_time,
            "execution_time": s.getvalue()
        }


# 使用
analyzer = PerformanceAnalyzer()

# 性能分析
metrics = analyzer.analyze_agent_execution(agent, "任务")
print(f"执行时间：{metrics['elapsed_time']:.4f}秒")
print(f"性能报告：\n{metrics['execution_time']}")
```

### 21.1.2 性能瓶颈定位

**1. 性能瓶颈定位示例**

```python
import time
import cProfile
from io import StringIO

class Agent:
    """Agent 类"""

    def __init__(self):
        """初始化 Agent"""
        self.cache = {}

    def execute(self, task: str) -> str:
        """执行任务"""
        # 检查缓存
        if task in self.cache:
            return self.cache[task]

        # 耗时操作
        time.sleep(1)

        # 缓存结果
        self.cache[task] = f"结果：{task}"
        return self.cache[task]


# 性能分析
pr = cProfile.Profile()
pr.enable()

agent = Agent()
for i in range(10):
    agent.execute(f"任务{i}")

pr.disable()

# 输出性能报告
s = StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
ps.print_stats(20)

print(s.getvalue())
```

**2. 性能优化建议**

根据性能分析报告，识别性能瓶颈：

- **CPU 密集型**: 优化算法、使用更高效的数据结构
- **I/O 密集型**: 使用缓存、异步 I/O
- **内存密集型**: 优化内存使用、使用更高效的数据结构
- **数据库查询**: 优化查询语句、添加索引

## 21.2 缓存优化实战

### 21.2.1 Redis 缓存优化

**1. 缓存 Agent 结果**

```python
import redis
import json
from typing import Optional

class CachedAgent:
    """缓存 Agent"""

    def __init__(self, agent, redis_url: str = "redis://localhost:6379/0"):
        """
        初始化缓存 Agent

        Args:
            agent: Agent 实例
            redis_url: Redis URL
        """
        self.agent = agent
        self.redis = redis.Redis.from_url(redis_url)

    def execute(self, task: str, ttl: int = 3600) -> str:
        """
        执行任务（带缓存）

        Args:
            task: 任务
            ttl: 过期时间（秒）

        Returns:
            执行结果
        """
        # 生成缓存键
        cache_key = f"agent:task:{task}"

        # 检查缓存
        cached_result = self.redis.get(cache_key)
        if cached_result:
            return cached_result.decode('utf-8')

        # 执行 Agent
        result = self.agent.execute(task)

        # 缓存结果
        self.redis.setex(cache_key, ttl, json.dumps(result))

        return result


# 使用
agent = Agent()
cached_agent = CachedAgent(agent)

result1 = cached_agent.execute("任务1")
result2 = cached_agent.execute("任务1")  # 从缓存获取
```

**2. 缓存 Agent 工具结果**

```python
from functools import wraps

class CachedTool:
    """缓存工具"""

    def __init__(self, tool, cache: redis.Redis):
        """
        初始化缓存工具

        Args:
            tool: 工具实例
            cache: Redis 实例
        """
        self.tool = tool
        self.cache = cache

    def __call__(self, **kwargs) -> str:
        """调用工具（带缓存）"""
        # 生成缓存键
        cache_key = f"tool:{self.tool.name}:{str(kwargs)}"

        # 检查缓存
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result.decode('utf-8')

        # 调用工具
        result = self.tool.execute(**kwargs)

        # 缓存结果
        self.cache.setex(cache_key, 3600, json.dumps(result))

        return result


# 使用
tool = GetWeatherTool()
cached_tool = CachedTool(tool, redis)

result1 = cached_tool(city="北京")
result2 = cached_tool(city="北京")  # 从缓存获取
```

### 21.2.2 内存缓存优化

**1. LRU 缓存优化**

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_agent_task(param: str) -> str:
    """
    耗时 Agent 任务

    Args:
        param: 参数

    Returns:
        结果
    """
    import time
    time.sleep(1)
    return f"结果：{param}"


# 使用
result1 = expensive_agent_task("参数1")
result2 = expensive_agent_task("参数1")  # 从缓存获取
```

**2. TTL 缓存优化**

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

## 21.3 异步优化实战

### 21.3.1 异步 Agent 优化

**1. 异步 Agent 实现**

```python
import asyncio
from typing import Dict, Any

class AsyncAgent:
    """异步 Agent"""

    def __init__(self, agent_id: str):
        """初始化异步 Agent"""
        self.agent_id = agent_id

    async def execute(self, task: str) -> Dict[str, Any]:
        """
        执行任务（异步）

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


# 使用
async def main():
    """主函数"""
    # 创建异步 Agent
    agent = AsyncAgent("agent_1")

    # 执行任务
    result = await agent.execute("任务")
    print(result)

    # 并发执行多个任务
    tasks = [
        agent.execute("任务1"),
        agent.execute("任务2"),
        agent.execute("任务3")
    ]

    results = await asyncio.gather(*tasks)

    for result in results:
        print(result)


asyncio.run(main())
```

**2. 异步 API 优化**

```python
from fastapi import FastAPI
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

### 21.3.2 异步数据库优化

**1. 异步数据库查询**

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 创建异步引擎
engine = create_async_engine("postgresql+asyncpg://user:***@localhost:5432/db", echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_user(user_id: int):
    """获取用户（异步）"""
    async with async_session() as session:
        result = await session.execute(f"SELECT * FROM users WHERE id = {user_id}")
        user = result.fetchone()
        return user


# 使用
user = asyncio.run(get_user(1))
print(user)
```

**2. 异步批量查询**

```python
async def get_users(user_ids: list) -> list:
    """批量获取用户（异步）"""
    async with async_session() as session:
        results = await session.execute(
            f"SELECT * FROM users WHERE id IN ({','.join(map(str, user_ids))})"
        )
        return results.fetchall()


# 使用
users = asyncio.run(get_users([1, 2, 3]))
for user in users:
    print(user)
```

## 21.4 并发优化实战

### 21.4.1 并发 Agent 优化

**1. 并发 Agent 执行**

```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

class ConcurrentAgent:
    """并发 Agent"""

    def __init__(self, agent_id: str):
        """初始化并发 Agent"""
        self.agent_id = agent_id

    def execute(self, task: str) -> Dict[str, Any]:
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
                executor.submit(self.execute, task)
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

**2. 并发 Agent 批量执行**

```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

class BatchAgent:
    """批量 Agent"""

    def __init__(self, agent_id: str):
        """初始化批量 Agent"""
        self.agent_id = agent_id

    def execute_batch(self, tasks: List[str], batch_size: int = 5) -> List[dict]:
        """
        批量执行任务

        Args:
            tasks: 任务列表
            batch_size: 批次大小

        Returns:
            结果列表
        """
        results = []

        # 分批执行
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]

            # 并发执行批次
            with ThreadPoolExecutor(max_workers=batch_size) as executor:
                futures = [executor.submit(self.execute, task) for task in batch]
                batch_results = [future.result() for future in futures]
                results.extend(batch_results)

        return results


# 使用
agent = BatchAgent("agent_1")

tasks = [f"任务{i}" for i in range(20)]

results = agent.execute_batch(tasks)

for result in results:
    print(result)
```

### 21.4.2 并发数据库优化

**1. 并发数据库查询**

```python
from concurrent.futures import ThreadPoolExecutor

def get_user(user_id: int):
    """获取用户"""
    # 模拟数据库查询
    import time
    time.sleep(0.1)
    return {"user_id": user_id, "name": f"用户{user_id}"}


def main():
    """主函数"""
    # 并发查询多个用户
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(get_user, user_id)
            for user_id in range(1, 11)
        ]

        results = [future.result() for future in futures]

    for result in results:
        print(result)


# 使用
main()
```

**2. 并发数据库插入**

```python
from concurrent.futures import ThreadPoolExecutor
import time

def insert_user(user_id: int):
    """插入用户"""
    # 模拟数据库插入
    time.sleep(0.1)
    return f"插入用户{user_id}"


def main():
    """主函数"""
    # 并发插入多个用户
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(insert_user, user_id)
            for user_id in range(1, 11)
        ]

        results = [future.result() for future in futures]

    for result in results:
        print(result)


# 使用
main()
```

## 21.5 本章总结

### 核心要点

1. **性能分析实战**: cProfile、Py-Spy、性能瓶颈定位
2. **缓存优化实战**: Redis 缓存、内存缓存（LRU、TTL）
3. **异步优化实战**: 异步 Agent、异步 API、异步数据库
4. **并发优化实战**: 并发 Agent、并发数据库

### 实战技巧

- **性能分析**: 使用 cProfile、Py-Spy 识别性能瓶颈
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

第22章将介绍 **Agent 安全实战**，包括：
- 安全威胁分析
- 认证与授权实现
- 数据加密实战
- 安全最佳实践

---

**本章完**

**下一章**: [第22章：Agent 安全实战](./22-chapter22-security-practice.md)
