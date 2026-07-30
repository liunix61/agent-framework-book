# 第7章：Loop 循环控制

## 本章目标

掌握 Agent 的循环控制机制，包括循环控制的概念、循环控制器的实现、循环控制与 Agent 的结合。

## 前置知识

- **基础 Python/C++**: 循环、条件判断
- **基础 Agent**: Harness 工具框架
- **基础 LLM API**: Function Calling

## 7.1 循环控制的概念

### 7.1.1 什么是循环控制

**循环控制（Loop Control）** 是指 Agent 能够自主决定何时停止或继续执行任务的能力。

**核心功能**:
- **循环判断**: 决定是否继续执行
- **循环终止**: 决定何时停止执行
- **循环条件**: 定义循环的执行条件
- **循环计数**: 记录循环次数

### 7.1.2 循环控制的工作流程

```
┌─────────────────────────────────────────────────────────┐
│                    循环控制工作流程                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 初始化循环                                            │
│     - 设置循环次数                                        │
│     - 初始化循环状态                                      │
│         ↓                                               │
│  2. 循环判断                                             │
│     - 检查循环条件是否满足                                │
│     - 检查循环次数是否达到上限                            │
│         ↓                                               │
│  3. 执行循环体                                           │
│     - 执行任务                                            │
│     - 调用工具                                            │
│     - 更新循环状态                                        │
│         ↓                                               │
│  4. 循环更新                                             │
│     - 更新循环次数                                        │
│     - 更新循环条件                                        │
│         ↓                                               │
│  5. 循环判断（返回步骤2）                                │
│     - 如果条件满足，继续循环                              │
│     - 如果条件不满足，退出循环                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 7.1.3 循环控制 vs 循环语句

**循环控制（Agent 级别）**:
- **自主决策**: Agent 自己决定是否继续执行
- **动态调整**: Agent 根据情况动态调整循环条件
- **工具调用**: Agent 可以在循环中调用工具

**循环语句（编程级别）**:
- **固定条件**: 循环条件在代码中固定
- **静态执行**: 循环次数固定
- **无工具调用**: 循环中只能执行代码逻辑

## 7.2 循环控制器的实现

### 7.2.1 循环控制器基类

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import time

class LoopController(ABC):
    """循环控制器基类"""

    def __init__(self, max_iterations: int = 10, timeout: int = 60):
        """
        初始化循环控制器

        Args:
            max_iterations: 最大循环次数
            timeout: 超时时间（秒）
        """
        self.max_iterations = max_iterations
        self.timeout = timeout
        self.current_iteration = 0
        self.start_time = time.time()

    def should_continue(self) -> bool:
        """
        判断是否应该继续循环

        Returns:
            True: 继续循环
            False: 退出循环
        """
        # 检查循环次数
        if self.current_iteration >= self.max_iterations:
            print(f"达到最大循环次数：{self.max_iterations}")
            return False

        # 检查超时
        elapsed_time = time.time() - self.start_time
        if elapsed_time > self.timeout:
            print(f"循环超时：{elapsed_time:.2f}秒")
            return False

        # 检查循环条件（由子类实现）
        if not self._check_loop_condition():
            print("循环条件不满足")
            return False

        return True

    def _check_loop_condition(self) -> bool:
        """
        检查循环条件（由子类实现）

        Returns:
            True: 循环条件满足
            False: 循环条件不满足
        """
        raise NotImplementedError

    def increment_iteration(self):
        """增加循环次数"""
        self.current_iteration += 1

    def get_iteration(self) -> int:
        """获取当前循环次数"""
        return self.current_iteration

    def get_elapsed_time(self) -> float:
        """获取已用时间"""
        return time.time() - self.start_time


# 使用
controller = LoopController(max_iterations=5, timeout=10)

while controller.should_continue():
    print(f"当前循环次数：{controller.get_iteration()}")
    controller.increment_iteration()
    time.sleep(1)
```

### 7.2.2 条件循环控制器

```python
class ConditionLoopController(LoopController):
    """条件循环控制器"""

    def __init__(self, condition_func, max_iterations: int = 10, timeout: int = 60):
        """
        初始化条件循环控制器

        Args:
            condition_func: 循环条件函数（返回 bool）
            max_iterations: 最大循环次数
            timeout: 超时时间（秒）
        """
        super().__init__(max_iterations, timeout)
        self.condition_func = condition_func

    def _check_loop_condition(self) -> bool:
        """检查循环条件"""
        return self.condition_func()


# 使用
def is_finished():
    """循环条件函数"""
    return False  # 假设任务已经完成

controller = ConditionLoopController(
    condition_func=is_finished,
    max_iterations=10,
    timeout=10
)

while controller.should_continue():
    print(f"当前循环次数：{controller.get_iteration()}")
    controller.increment_iteration()
    time.sleep(1)
```

### 7.2.3 工具调用循环控制器

```python
class ToolCallingLoopController(LoopController):
    """工具调用循环控制器"""

    def __init__(
        self,
        tool_caller,
        condition_func,
        max_iterations: int = 10,
        timeout: int = 60
    ):
        """
        初始化工具调用循环控制器

        Args:
            tool_caller: 工具调用器
            condition_func: 循环条件函数（返回 bool）
            max_iterations: 最大循环次数
            timeout: 超时时间（秒）
        """
        super().__init__(max_iterations, timeout)
        self.tool_caller = tool_caller
        self.condition_func = condition_func

    def _check_loop_condition(self) -> bool:
        """检查循环条件"""
        return self.condition_func()

    def execute_loop(self, user_message: str) -> str:
        """执行循环"""
        while self.should_continue():
            print(f"\n当前循环次数：{self.get_iteration()}")

            # 调用工具
            result = self.tool_caller.call_tool_with_llm(user_message)

            print(f"工具结果：{result}")

            # 检查是否完成
            if self.condition_func():
                print("任务完成！")
                return result

            # 增加循环次数
            self.increment_iteration()

        print("循环终止")
        return result


# 使用
tool_caller = ToolCaller(registry)

def is_finished():
    """循环条件函数"""
    # 假设工具调用返回的结果包含"完成"字样
    result = tool_caller.call_tool_with_llm("搜索北京的天气")
    return "完成" in result

controller = ToolCallingLoopController(
    tool_caller=tool_caller,
    condition_func=is_finished,
    max_iterations=5,
    timeout=10
)

result = controller.execute_loop("搜索北京的天气")
print(f"\n最终结果：{result}")
```

## 7.3 循环控制与 Agent 的结合

### 7.3.1 循环 Agent

```python
class LoopingAgent:
    """循环 Agent"""

    def __init__(self, tool_caller, max_iterations: int = 10, timeout: int = 60):
        """
        初始化循环 Agent

        Args:
            tool_caller: 工具调用器
            max_iterations: 最大循环次数
            timeout: 超时时间（秒）
        """
        self.tool_caller = tool_caller
        self.controller = ToolCallingLoopController(
            tool_caller=tool_caller,
            condition_func=self._check_condition,
            max_iterations=max_iterations,
            timeout=timeout
        )

    def _check_condition(self) -> bool:
        """检查循环条件"""
        # 调用工具获取结果
        result = self.tool_caller.call_tool_with_llm("请告诉我任务是否完成")

        # 判断是否完成
        return "完成" in result

    def execute(self, user_message: str) -> str:
        """执行 Agent"""
        print(f"用户问题：{user_message}")
        print("\n开始执行循环...")

        result = self.controller.execute_loop(user_message)

        print(f"\n最终结果：{result}")
        return result


# 使用
looping_agent = LoopingAgent(tool_caller=tool_caller)

result = looping_agent.execute("帮我完成一个任务")
print(result)
```

### 7.3.2 循环 Agent 示例：批量处理

```python
class BatchProcessingAgent:
    """批量处理 Agent"""

    def __init__(self, tool_caller, batch_size: int = 10, max_iterations: int = 100):
        """
        初始化批量处理 Agent

        Args:
            tool_caller: 工具调用器
            batch_size: 批量大小
            max_iterations: 最大循环次数
        """
        self.tool_caller = tool_caller
        self.batch_size = batch_size
        self.max_iterations = max_iterations
        self.processed_count = 0

    def execute(self, tasks: List[str]) -> List[str]:
        """执行批量处理"""
        results = []

        for i, task in enumerate(tasks):
            print(f"\n处理任务 {i+1}/{len(tasks)}：{task}")

            # 执行任务
            result = self.tool_caller.call_tool_with_llm(task)

            results.append({
                "task": task,
                "result": result,
                "status": "完成"
            })

            self.processed_count += 1

            # 显示进度
            progress = (self.processed_count / self.max_iterations) * 100
            print(f"进度：{progress:.2f}%")

        return results


# 使用
batch_agent = BatchProcessingAgent(tool_caller=tool_caller)

tasks = [
    "写一首关于春天的诗",
    "写一篇关于AI的文章",
    "写一个Python排序函数",
    "写一个C++快速排序",
    "写一个JavaScript斐波那契数列"
]

results = batch_agent.execute(tasks)

print("\n批量处理结果：")
for result in results:
    print(f"\n任务：{result['task']}")
    print(f"结果：{result['result']}")
    print(f"状态：{result['status']}")
```

### 7.3.3 循环 Agent 示例：递归任务

```python
class RecursiveAgent:
    """递归 Agent"""

    def __init__(self, tool_caller, max_depth: int = 5):
        """
        初始化递归 Agent

        Args:
            tool_caller: 工具调用器
            max_depth: 最大递归深度
        """
        self.tool_caller = tool_caller
        self.max_depth = max_depth

    def execute(self, task: str, depth: int = 0) -> str:
        """
        执行递归任务

        Args:
            task: 任务
            depth: 当前深度

        Returns:
            任务结果
        """
        # 检查递归深度
        if depth >= self.max_depth:
            print(f"达到最大递归深度：{self.max_depth}")
            return "递归深度达到上限"

        print(f"执行任务（深度 {depth}）：{task}")

        # 调用工具
        result = self.tool_caller.call_tool_with_llm(task)

        # 检查是否需要递归
        if "继续" in result:
            print("任务需要继续，开始递归...")
            sub_task = "继续完成任务"
            sub_result = self.execute(sub_task, depth + 1)
            return f"{result}\n递归结果：{sub_result}"
        else:
            print("任务完成！")
            return result

    def execute_with_loop(self, task: str) -> str:
        """使用循环控制执行递归任务"""
        loop_controller = LoopController(max_iterations=self.max_depth)

        while loop_controller.should_continue():
            print(f"\n当前循环次数：{loop_controller.get_iteration()}")

            # 调用工具
            result = self.tool_caller.call_tool_with_llm(task)

            print(f"工具结果：{result}")

            # 检查是否完成
            if "完成" in result:
                print("任务完成！")
                return result

            # 更新任务
            task = "继续完成任务"

            # 增加循环次数
            loop_controller.increment_iteration()

        print("循环终止")
        return "任务终止"


# 使用
recursive_agent = RecursiveAgent(tool_caller=tool_caller)

# 递归执行
result = recursive_agent.execute("写一首诗")
print(f"\n递归结果：{result}")

# 循环控制执行
result2 = recursive_agent.execute_with_loop("写一首诗")
print(f"\n循环控制结果：{result2}")
```

## 7.4 循环控制优化

### 7.4.1 智能循环终止

```python
class SmartLoopController(LoopController):
    """智能循环控制器"""

    def __init__(self, tool_caller, max_iterations: int = 10, timeout: int = 60):
        super().__init__(max_iterations, timeout)
        self.tool_caller = tool_caller

    def _check_loop_condition(self) -> bool:
        """智能检查循环条件"""
        # 调用工具检查是否完成
        result = self.tool_caller.call_tool_with_llm("请告诉我任务是否完成")

        # 判断是否完成
        is_finished = "完成" in result

        # 如果完成，提前退出循环
        if is_finished:
            print("任务完成！提前退出循环")

        return is_finished

    def execute_loop(self, user_message: str) -> str:
        """执行循环"""
        while self.should_continue():
            print(f"\n当前循环次数：{self.get_iteration()}")

            # 调用工具
            result = self.tool_caller.call_tool_with_llm(user_message)

            print(f"工具结果：{result}")

            # 增加循环次数
            self.increment_iteration()

        print("循环终止")
        return result


# 使用
smart_controller = SmartLoopController(
    tool_caller=tool_caller,
    max_iterations=10,
    timeout=60
)

result = smart_controller.execute_loop("帮我完成一个任务")
print(f"\n最终结果：{result}")
```

### 7.4.2 循环状态保存

```python
class StatefulLoopController(LoopController):
    """有状态的循环控制器"""

    def __init__(self, max_iterations: int = 10, timeout: int = 60):
        super().__init__(max_iterations, timeout)
        self.state = {}

    def update_state(self, key: str, value: Any):
        """更新状态"""
        self.state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        """获取状态"""
        return self.state.get(key, default)

    def reset_state(self):
        """重置状态"""
        self.state = {}

    def execute_loop(self, user_message: str) -> str:
        """执行循环"""
        while self.should_continue():
            print(f"\n当前循环次数：{self.get_iteration()}")

            # 获取当前状态
            current_state = self.get_state("state")

            # 调用工具（传入状态）
            result = self.tool_caller.call_tool_with_llm(user_message)

            # 更新状态
            self.update_state("last_result", result)

            print(f"工具结果：{result}")

            # 增加循环次数
            self.increment_iteration()

        print("循环终止")
        return result


# 使用
stateful_controller = StatefulLoopController(
    max_iterations=5,
    timeout=10
)

stateful_controller.update_state("step", 0)
result = stateful_controller.execute_loop("写一首诗")
print(f"\n最终结果：{result}")
print(f"最终状态：{stateful_controller.get_state('state')}")
```

## 7.5 本章总结

### 核心要点

1. **循环控制概念**: Agent 自主决定是否继续执行
2. **循环控制器**: 继承 LoopController 基类
3. **条件循环**: 使用条件函数控制循环
4. **工具调用循环**: 在循环中调用工具
5. **循环 Agent**: 结合循环控制和 Agent
6. **循环优化**: 智能循环终止、循环状态保存

### 实战技巧

- **循环控制器**: 使用基类和子类实现不同的循环控制逻辑
- **条件判断**: 使用函数参数化循环条件
- **工具调用**: 在循环中调用工具获取结果
- **智能终止**: 检查工具结果决定是否继续
- **状态保存**: 保存循环状态以便后续使用

### 练习题

1. 实现一个条件循环控制器
2. 实现一个工具调用循环控制器
3. 实现一个循环 Agent
4. 实现一个有状态的循环控制器

### 下章预告

第8章将介绍 **Graph 图结构设计**，包括：
- Graph 的概念
- 图结构设计
- Graph 与 Agent 的结合

---

**本章完**

**下一章**: [第8章：Graph 图结构设计](./08-chapter8-graph-design.md)
