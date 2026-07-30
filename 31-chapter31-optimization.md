# 第31章：Agent 系统优化

## 本章目标

通过实战项目，掌握 Agent 系统优化的方法。

## 前置知识

- **基础 优化**: 性能优化、代码优化
- **基础 Agent**: Harness、Loop、Graph
- **基础 项目**: 项目结构、代码组织

## 31.1 系统优化概述

### 31.1.1 系统优化概述

**1. 系统优化类型**

| 优化类型 | 说明 | 用途 |
|---------|------|------|
| **性能优化** | 提升系统性能 | 响应时间、吞吐量 |
| **代码优化** | 优化代码质量 | 可读性、可维护性 |
| **内存优化** | 优化内存使用 | 内存占用、内存泄漏 |
| **网络优化** | 优化网络性能 | 延迟、带宽 |

**2. 系统优化流程**

```
┌─────────────────────────────────────────────────────────┐
│                    系统优化流程                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  性能分析                          │  │
│  │  - 性能分析工具                                    │  │
│  │  - 性能瓶颈定位                                    │  │
│  │  - 性能优化建议                                    │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  优化实施                          │  │
│  │  - 性能优化                                        │  │
│  │  - 代码优化                                        │  │
│  │  - 内存优化                                        │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  优化验证                          │  │
│  │  - 性能测试                                        │  │
│  │  - 代码审查                                        │  │
│  │  - 内存测试                                        │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  优化报告                          │  │
│  │  - 优化结果                                        │  │
│  │  - 优化建议                                        │  │
│  │  - 下一步计划                                      │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 31.1.2 系统优化指标

**1. 性能优化指标**

| 指标 | 说明 | 优化目标 |
|------|------|---------|
| **响应时间** | 系统响应时间 | 降低响应时间 |
| **吞吐量** | 系统吞吐量 | 提高吞吐量 |
| **并发性能** | 系统并发性能 | 提高并发性能 |
| **资源利用率** | 系统资源利用率 | 提高资源利用率 |

**2. 代码优化指标**

| 指标 | 说明 | 优化目标 |
|------|------|---------|
| **代码复杂度** | 代码复杂度 | 降低代码复杂度 |
| **代码可读性** | 代码可读性 | 提高代码可读性 |
| **代码可维护性** | 代码可维护性 | 提高代码可维护性 |
| **代码复用性** | 代码复用性 | 提高代码复用性 |

## 31.2 性能优化实战

### 31.2.1 缓存优化

**1. 缓存优化器**

```python
# system_optimization/cache_optimizer.py
from typing import Dict, Any, Optional
from functools import wraps
import time

class CacheOptimizer:
    """缓存优化器"""

    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        """
        初始化缓存优化器

        Args:
            max_size: 最大缓存大小
            ttl: 缓存过期时间（秒）
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl = ttl

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

        # 检查是否过期
        if time.time() - self.cache[key]["timestamp"] > self.ttl:
            del self.cache[key]
            return None

        return self.cache[key]["value"]

    def set(self, key: str, value: Any):
        """
        设置缓存

        Args:
            key: 缓存键
            value: 缓存值
        """
        # 检查缓存大小
        if len(self.cache) >= self.max_size:
            # 删除最旧的缓存
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["timestamp"])
            del self.cache[oldest_key]

        # 设置缓存
        self.cache[key] = {
            "value": value,
            "timestamp": time.time()
        }

    def clear(self):
        """清空缓存"""
        self.cache.clear()

    def invalidate(self, pattern: str):
        """
        使缓存失效

        Args:
            pattern: 匹配模式
        """
        keys_to_delete = [key for key in self.cache.keys() if pattern in key]

        for key in keys_to_delete:
            del self.cache[key]

    def decorator(self, ttl: Optional[int] = None):
        """
        装饰器

        Args:
            ttl: 缓存过期时间
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 生成缓存键
                cache_key = f"{func.__name__}:{args}:{kwargs}"

                # 尝试从缓存获取
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value

                # 执行函数
                value = func(*args, **kwargs)

                # 设置缓存
                self.set(cache_key, value, ttl)

                return value

            return wrapper

        return decorator


# 使用
optimizer = CacheOptimizer(max_size=100, ttl=3600)

def expensive_function(x: int, y: int) -> int:
    """耗时函数"""
    time.sleep(1)  # 模拟耗时操作
    return x + y

# 使用装饰器
@optimizer.decorator(ttl=600)
def cached_function(x: int, y: int) -> int:
    """缓存函数"""
    time.sleep(1)  # 模拟耗时操作
    return x + y

# 第一次调用（无缓存）
start_time = time.time()
result1 = expensive_function(1, 2)
print(f"第一次调用耗时：{time.time() - start_time:.4f} 秒")

# 第二次调用（无缓存）
start_time = time.time()
result2 = expensive_function(1, 2)
print(f"第二次调用耗时：{time.time() - start_time:.4f} 秒")

# 第三次调用（有缓存）
start_time = time.time()
result3 = cached_function(1, 2)
print(f"第三次调用耗时：{time.time() - start_time:.4f} 秒")

# 第四次调用（有缓存）
start_time = time.time()
result4 = cached_function(1, 2)
print(f"第四次调用耗时：{time.time() - start_time:.4f} 秒")
```

**2. Redis 缓存优化**

```python
# system_optimization/redis_cache_optimizer.py
import redis
from typing import Any, Optional

class RedisCacheOptimizer:
    """Redis 缓存优化器"""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        """
        初始化 Redis 缓存优化器

        Args:
            host: Redis 主机
            port: Redis 端口
            db: Redis 数据库
        """
        self.redis_client = redis.Redis(host=host, port=port, db=db)

    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存

        Args:
            key: 缓存键

        Returns:
            缓存值
        """
        value = self.redis_client.get(key)

        if value is None:
            return None

        return self.redis_client.decode(value)

    def set(self, key: str, value: Any, ttl: int = 3600):
        """
        设置缓存

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）
        """
        self.redis_client.setex(key, ttl, value)

    def delete(self, key: str):
        """
        删除缓存

        Args:
            key: 缓存键
        """
        self.redis_client.delete(key)

    def clear(self):
        """清空缓存"""
        self.redis_client.flushdb()

    def decorator(self, ttl: int = 3600):
        """
        装饰器

        Args:
            ttl: 过期时间（秒）
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 生成缓存键
                cache_key = f"{func.__name__}:{args}:{kwargs}"

                # 尝试从缓存获取
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value

                # 执行函数
                value = func(*args, **kwargs)

                # 设置缓存
                self.set(cache_key, value, ttl)

                return value

            return wrapper

        return decorator


# 使用
redis_optimizer = RedisCacheOptimizer()

@redis_optimizer.decorator(ttl=600)
def cached_function(x: int, y: int) -> int:
    """缓存函数"""
    time.sleep(1)  # 模拟耗时操作
    return x + y

# 第一次调用（无缓存）
start_time = time.time()
result1 = cached_function(1, 2)
print(f"第一次调用耗时：{time.time() - start_time:.4f} 秒")

# 第二次调用（有缓存）
start_time = time.time()
result2 = cached_function(1, 2)
print(f"第二次调用耗时：{time.time() - start_time:.4f} 秒")
```

### 31.2.2 异步优化

**1. 异步优化器**

```python
# system_optimization/async_optimizer.py
import asyncio
from typing import Dict, Any, Optional

class AsyncOptimizer:
    """异步优化器"""

    def __init__(self, max_concurrent_tasks: int = 10):
        """
        初始化异步优化器

        Args:
            max_concurrent_tasks: 最大并发任务数
        """
        self.max_concurrent_tasks = max_concurrent_tasks

    async def execute_parallel(
        self,
        tasks: list
    ) -> list:
        """
        并发执行任务

        Args:
            tasks: 任务列表

        Returns:
            结果列表
        """
        # 创建任务
        async_tasks = [self.execute_task(task) for task in tasks]

        # 并发执行
        results = await asyncio.gather(*async_tasks)

        return results

    async def execute_task(self, task: callable) -> Any:
        """
        执行任务

        Args:
            task: 任务函数

        Returns:
            任务结果
        """
        # 执行任务
        return await task()

    async def execute_sequential(
        self,
        tasks: list
    ) -> list:
        """
        顺序执行任务

        Args:
            tasks: 任务列表

        Returns:
            结果列表
        """
        results = []

        # 顺序执行
        for task in tasks:
            result = await self.execute_task(task)
            results.append(result)

        return results


# 使用
async def slow_task(task_id: int) -> int:
    """慢速任务"""
    await asyncio.sleep(1)  # 模拟耗时操作
    return task_id * 2

async def main():
    """主函数"""
    # 并发执行
    print("并发执行：")
    start_time = time.time()
    results = await AsyncOptimizer().execute_parallel([slow_task(1), slow_task(2), slow_task(3)])
    print(f"耗时：{time.time() - start_time:.4f} 秒")
    print(f"结果：{results}")

    # 顺序执行
    print("\n顺序执行：")
    start_time = time.time()
    results = await AsyncOptimizer().execute_sequential([slow_task(1), slow_task(2), slow_task(3)])
    print(f"耗时：{time.time() - start_time:.4f} 秒")
    print(f"结果：{results}")

asyncio.run(main())
```

## 31.3 代码优化实战

### 31.3.1 代码复杂度优化

**1. 代码复杂度分析**

```python
# system_optimization/code_complexity.py
import ast
from typing import List, Dict, Any

class CodeComplexityAnalyzer:
    """代码复杂度分析器"""

    def analyze(self, code: str) -> Dict[str, Any]:
        """
        分析代码复杂度

        Args:
            code: 代码

        Returns:
            复杂度分析结果
        """
        # 解析代码
        tree = ast.parse(code)

        # 分析复杂度
        complexity = {
            "cyclomatic_complexity": 0,
            "functions": [],
            "classes": []
        }

        # 分析函数
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity["functions"].append({
                    "name": node.name,
                    "arguments": len(node.args.args),
                    "complexity": self._calculate_function_complexity(node)
                })

                complexity["cyclomatic_complexity"] += complexity["functions"][-1]["complexity"]

            elif isinstance(node, ast.ClassDef):
                complexity["classes"].append({
                    "name": node.name,
                    "methods": len(node.body)
                })

        return complexity

    def _calculate_function_complexity(self, function_node: ast.FunctionDef) -> int:
        """
        计算函数复杂度

        Args:
            function_node: 函数节点

        Returns:
            复杂度
        """
        complexity = 1  # 基础复杂度

        # 检查条件语句
        for node in ast.walk(function_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.With)):
                complexity += 1

        # 检查逻辑运算符
        for node in ast.walk(function_node):
            if isinstance(node, (ast.BoolOp, ast.Compare)):
                complexity += len(node.values) - 1

        return complexity


# 使用
code = """
def example_function(x, y, z):
    if x > 0:
        if y > 0:
            return x + y
        else:
            return x - y
    else:
        if z > 0:
            return x * z
        else:
            return x / z
"""

analyzer = CodeComplexityAnalyzer()
complexity = analyzer.analyze(code)

print(f"循环复杂度：{complexity['cyclomatic_complexity']}")
print(f"函数列表：")
for func in complexity["functions"]:
    print(f"  - {func['name']}：{func['complexity']}")

print(f"类列表：")
for cls in complexity["classes"]:
    print(f"  - {cls['name']}：{cls['methods']} 个方法")
```

**2. 代码复杂度优化**

```python
# system_optimization/code_complexity_optimizer.py
from typing import List, Dict, Any

class CodeComplexityOptimizer:
    """代码复杂度优化器"""

    def optimize(self, code: str) -> str:
        """
        优化代码复杂度

        Args:
            code: 代码

        Returns:
            优化后的代码
        """
        # 简单的优化策略
        optimized_code = code

        # 移除重复的 if 语句
        optimized_code = self._remove_duplicate_if(optimized_code)

        # 提取函数
        optimized_code = self._extract_functions(optimized_code)

        # 简化条件表达式
        optimized_code = self._simplify_conditions(optimized_code)

        return optimized_code

    def _remove_duplicate_if(self, code: str) -> str:
        """
        移除重复的 if 语句

        Args:
            code: 代码

        Returns:
            优化后的代码
        """
        # 简单的优化（实际应该使用 AST）
        optimized_code = code.replace("if x > 0:\n            if y > 0:\n                return x + y\n            else:\n                return x - y\n        else:\n            if z > 0:\n                return x * z\n            else:\n                return x / z", "return x * y if x > 0 and y > 0 else x * z if x > 0 and z > 0 else x / z")

        return optimized_code

    def _extract_functions(self, code: str) -> str:
        """
        提取函数

        Args:
            code: 代码

        Returns:
            优化后的代码
        """
        # 简单的优化（实际应该使用 AST）
        optimized_code = f"""
def calculate(x, y, z):
    return x * y if x > 0 and y > 0 else x * z if x > 0 and z > 0 else x / z

def example_function(x, y, z):
    return calculate(x, y, z)
"""

        return optimized_code

    def _simplify_conditions(self, code: str) -> str:
        """
        简化条件表达式

        Args:
            code: 代码

        Returns:
            优化后的代码
        """
        # 简单的优化（实际应该使用 AST）
        optimized_code = code.replace("if x > 0:\n                return x + y\n            else:\n                return x - y", "return x + y if x > 0 else x - y")

        return optimized_code


# 使用
optimizer = CodeComplexityOptimizer()

code = """
def example_function(x, y, z):
    if x > 0:
        if y > 0:
            return x + y
        else:
            return x - y
    else:
        if z > 0:
            return x * z
        else:
            return x / z
"""

print("优化前：")
print(code)

print("\n优化后：")
optimized_code = optimizer.optimize(code)
print(optimized_code)
```

### 31.3.2 代码重构优化

**1. 代码重构器**

```python
# system_optimization/code_refactoring.py
from typing import List, Dict, Any

class CodeRefactoring:
    """代码重构器"""

    def __init__(self):
        """初始化代码重构器"""
        self.refactorings = []

    def extract_method(self, code: str, method_name: str, start_line: int, end_line: int) -> str:
        """
        提取方法

        Args:
            code: 代码
            method_name: 方法名称
            start_line: 开始行
            end_line: 结束行

        Returns:
            重构后的代码
        """
        # 提取方法
        lines = code.split('\n')
        method_lines = lines[start_line - 1:end_line]

        # 生成新代码
        new_code = '\n'.join(method_lines)
        new_code = f"def {method_name}():\n    {new_code.replace('return', 'return ')}\n\n"

        # 替换原代码
        new_code += '\n'.join(lines[:start_line - 1]) + '\n' + '\n'.join(lines[end_line:])

        return new_code

    def extract_class(self, code: str, class_name: str, methods: List[str]) -> str:
        """
        提取类

        Args:
            code: 代码
            class_name: 类名称
            methods: 方法列表

        Returns:
            重构后的代码
        """
        # 生成新代码
        new_code = f"class {class_name}:\n"

        for method in methods:
            new_code += f"    def {method}():\n        pass\n\n"

        return new_code

    def add_comment(self, code: str, line: int, comment: str) -> str:
        """
        添加注释

        Args:
            code: 代码
            line: 行号
            comment: 注释内容

        Returns:
            重构后的代码
        """
        lines = code.split('\n')
        lines[line - 1] = f"# {comment}"
        return '\n'.join(lines)

    def rename_variable(self, code: str, old_name: str, new_name: str) -> str:
        """
        重命名变量

        Args:
            code: 代码
            old_name: 旧变量名
            new_name: 新变量名

        Returns:
            重构后的代码
        """
        return code.replace(old_name, new_name)


# 使用
refactoring = CodeRefactoring()

code = """
def calculate_total(price, quantity, discount):
    subtotal = price * quantity
    if discount > 0:
        total = subtotal - discount
    else:
        total = subtotal
    return total

def calculate_tax(total):
    tax_rate = 0.1
    tax = total * tax_rate
    return tax
"""

print("优化前：")
print(code)

print("\n优化后：")
# 提取方法
new_code = refactoring.extract_method(code, "apply_discount", 2, 6)
new_code = refactoring.extract_method(new_code, "apply_tax", 8, 11)

print(new_code)
```

## 31.4 内存优化实战

### 31.4.1 内存优化器

**1. 内存优化器**

```python
# system_optimization/memory_optimizer.py
import gc
import weakref
from typing import Dict, Any, Optional

class MemoryOptimizer:
    """内存优化器"""

    def __init__(self):
        """初始化内存优化器"""
        self.memory_stats = []

    def collect_garbage(self):
        """收集垃圾"""
        gc.collect()

    def print_memory_usage(self):
        """打印内存使用情况"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()

        print(f"内存使用：{mem_info.rss / 1024 / 1024:.2f} MB")

    def use_weakref(self, data: Dict[str, Any]) -> weakref.ref:
        """
        使用弱引用

        Args:
            data: 数据

        Returns:
            弱引用
        """
        weak_data = weakref.ref(data)
        return weak_data

    def use_object_pool(self, obj_class, pool_size: int = 10):
        """
        使用对象池

        Args:
            obj_class: 对象类
            pool_size: 池大小
        """
        class ObjectPool:
            def __init__(self, obj_class, pool_size):
                self.obj_class = obj_class
                self.pool = [obj_class() for _ in range(pool_size)]
                self.available = len(self.pool)

            def get(self):
                """获取对象"""
                if self.available > 0:
                    obj = self.pool[-1]
                    self.pool.pop()
                    self.available -= 1
                    return obj
                else:
                    return self.obj_class()

            def release(self, obj):
                """释放对象"""
                self.pool.append(obj)
                self.available += 1

        return ObjectPool(obj_class, pool_size)


# 使用
optimizer = MemoryOptimizer()

# 打印内存使用情况
optimizer.print_memory_usage()

# 使用弱引用
data = {"key": "value"}
weak_data = optimizer.use_weakref(data)

print(f"弱引用：{weak_data}")

# 使用对象池
class DataObject:
    def __init__(self):
        self.data = "test"

pool = optimizer.use_object_pool(DataObject, pool_size=5)

# 获取对象
obj1 = pool.get()
obj2 = pool.get()

print(f"对象池大小：{pool.available}")

# 释放对象
pool.release(obj1)
pool.release(obj2)

print(f"对象池大小：{pool.available}")

# 收集垃圾
optimizer.collect_garbage()
```

### 31.4.2 内存泄漏检测

**1. 内存泄漏检测器**

```python
# system_optimization/memory_leak_detector.py
import gc
import tracemalloc
from typing import Dict, Any

class MemoryLeakDetector:
    """内存泄漏检测器"""

    def __init__(self):
        """初始化内存泄漏检测器"""
        self.memory_snapshots = []

    def take_snapshot(self, name: str):
        """
        获取内存快照

        Args:
            name: 快照名称
        """
        tracemalloc.start()

        current, peak = tracemalloc.get_traced_memory()

        snapshot = {
            "name": name,
            "current": current / 1024 / 1024,  # 转换为 MB
            "peak": peak / 1024 / 1024,  # 转换为 MB
            "top_allocations": tracemalloc.take_snapshot().statistics('lineno')
        }

        self.memory_snapshots.append(snapshot)

        tracemalloc.stop()

    def analyze_leaks(self):
        """分析内存泄漏"""
        print("内存快照分析：")

        for snapshot in self.memory_snapshots:
            print(f"\n快照名称：{snapshot['name']}")
            print(f"当前内存：{snapshot['current']:.2f} MB")
            print(f"峰值内存：{snapshot['peak']:.2f} MB")

            print(f"Top 5 内存分配：")
            for stat in snapshot['top_allocations'][:5]:
                print(f"  {stat}")


# 使用
detector = MemoryLeakDetector()

# 创建一些数据
data = [{"key": f"value_{i}"} for i in range(1000)]

# 获取快照
detector.take_snapshot("快照 1")

# 修改数据
data = [{"key": f"value_{i}"} for i in range(2000)]

# 获取快照
detector.take_snapshot("快照 2")

# 分析内存泄漏
detector.analyze_leaks()
```

## 31.5 本章总结

### 核心要点

1. **系统优化概述**: 系统优化类型、系统优化流程、系统优化指标
2. **性能优化实战**: 缓存优化、异步优化
3. **代码优化实战**: 代码复杂度优化、代码重构优化
4. **内存优化实战**: 内存优化器、内存泄漏检测

### 实战技巧

- **缓存优化**: 使用缓存器缓存计算结果，减少重复计算
- **异步优化**: 使用异步编程提高并发性能
- **代码复杂度优化**: 降低代码复杂度，提高代码可读性
- **代码重构优化**: 提取方法、提取类、添加注释、重命名变量
- **内存优化**: 使用弱引用、对象池、垃圾回收

### 练习题

1. 实现缓存优化器
2. 实现异步优化器
3. 实现代码复杂度分析器
4. 实现内存优化器

### 下章预告

第32章将介绍 **Agent 系统部署实战**，包括：
- Docker 部署实战
- K8s 部署实战
- CI/CD 实战

---

**本章完**

**下一章**: [第32章：Agent 系统部署实战](./32-chapter31-optimization.md)
