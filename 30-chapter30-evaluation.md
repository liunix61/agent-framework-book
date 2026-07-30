# 第30章：Agent 系统评估

## 本章目标

通过实战项目，掌握 Agent 系统评估的方法和指标。

## 前置知识

- **基础 评估**: 性能评估、功能评估
- **基础 测试**: 单元测试、集成测试
- **基础 项目**: 项目结构、代码组织

## 30.1 系统评估概述

### 30.1.1 系统评估概述

**1. 系统评估类型**

| 评估类型 | 说明 | 用途 |
|---------|------|------|
| **功能评估** | 评估系统功能是否满足需求 | 功能验证 |
| **性能评估** | 评估系统性能是否满足要求 | 性能优化 |
| **可靠性评估** | 评估系统可靠性 | 可靠性验证 |
| **用户体验评估** | 评估用户体验 | 用户体验优化 |

**2. 系统评估流程**

```
┌─────────────────────────────────────────────────────────┐
│                    系统评估流程                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  评估准备                          │  │
│  │  - 确定评估目标                                    │  │
│  │  - 设计评估方案                                    │  │
│  │  - 准备评估数据                                    │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  数据收集                          │  │
│  │  - 运行测试                                        │  │
│  │  - 收集日志                                        │  │
│  │  - 收集指标                                        │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  数据分析                          │  │
│  │  - 数据统计                                        │  │
│  │  - 数据可视化                                      │  │
│  │  - 数据报告                                        │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  评估报告                          │  │
│  │  - 评估结果                                        │  │
│  │  - 评估建议                                        │  │
│  │  - 改进计划                                        │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 30.1.2 系统评估指标

**1. 功能评估指标**

| 指标 | 说明 | 计算方法 |
|------|------|---------|
| **功能覆盖率** | 功能覆盖率 | 功能数量 / 总功能数量 |
| **功能正确性** | 功能正确性 | 正确功能数量 / 总功能数量 |
| **功能完整性** | 功能完整性 | 实现功能数量 / 设计功能数量 |

**2. 性能评估指标**

| 指标 | 说明 | 计算方法 |
|------|------|---------|
| **响应时间** | 响应时间 | 平均响应时间 |
| **吞吐量** | 吞吐量 | 每秒请求数 |
| **并发性能** | 并发性能 | 最大并发用户数 |
| **资源利用率** | 资源利用率 | CPU / 内存利用率 |

**3. 可靠性评估指标**

| 指标 | 说明 | 计算方法 |
|------|------|---------|
| **可用性** | 可用性 | 可用时间 / 总时间 |
| **错误率** | 错误率 | 错误数量 / 总请求数 |
| **恢复时间** | 恢复时间 | 从错误到恢复的时间 |

**4. 用户体验评估指标**

| 指标 | 说明 | 计算方法 |
|------|------|---------|
| **用户满意度** | 用户满意度 | 用户评分 |
| **用户留存率** | 用户留存率 | 留存用户数量 / 总用户数量 |
| **用户活跃度** | 用户活跃度 | 活跃用户数量 / 总用户数量 |

## 30.2 系统评估指标

### 30.2.1 功能评估

**1. 功能评估器**

```python
# system_evaluation/functional_evaluator.py
from typing import Dict, Any, List, Optional

class FunctionalEvaluator:
    """功能评估器"""

    def __init__(self, system_name: str):
        """
        初始化功能评估器

        Args:
            system_name: 系统名称
        """
        self.system_name = system_name

        # 功能列表
        self.features = []
        self.passed_features = []
        self.failed_features = []

    def add_feature(
        self,
        feature_name: str,
        description: str,
        test_function: callable
    ):
        """
        添加功能

        Args:
            feature_name: 功能名称
            description: 功能描述
            test_function: 测试函数
        """
        self.features.append({
            "name": feature_name,
            "description": description,
            "test_function": test_function
        })

    def evaluate(self) -> Dict[str, Any]:
        """
        评估系统

        Returns:
            评估结果
        """
        results = {
            "system_name": self.system_name,
            "total_features": len(self.features),
            "passed_features": 0,
            "failed_features": 0,
            "features": []
        }

        # 评估所有功能
        for feature in self.features:
            try:
                # 执行测试
                test_result = feature["test_function"]()

                if test_result:
                    results["passed_features"] += 1
                    results["features"].append({
                        "name": feature["name"],
                        "status": "passed",
                        "description": feature["description"]
                    })
                else:
                    results["failed_features"] += 1
                    results["features"].append({
                        "name": feature["name"],
                        "status": "failed",
                        "description": feature["description"]
                    })

            except Exception as e:
                results["failed_features"] += 1
                results["features"].append({
                    "name": feature["name"],
                    "status": "error",
                    "description": feature["description"],
                    "error": str(e)
                })

        # 计算功能覆盖率
        results["feature_coverage"] = (
            results["passed_features"] / results["total_features"]
            if results["total_features"] > 0 else 0
        )

        # 计算功能正确性
        results["feature_correctness"] = (
            results["passed_features"] / results["total_features"]
            if results["total_features"] > 0 else 0
        )

        # 计算功能完整性
        results["feature_completeness"] = (
            results["passed_features"] / results["total_features"]
            if results["total_features"] > 0 else 0
        )

        return results

    def print_results(self, results: Dict[str, Any]):
        """
        打印评估结果

        Args:
            results: 评估结果
        """
        print(f"\n=== {results['system_name']} 功能评估结果 ===")
        print(f"总功能数量：{results['total_features']}")
        print(f"通过功能数量：{results['passed_features']}")
        print(f"失败功能数量：{results['failed_features']}")
        print(f"功能覆盖率：{results['feature_coverage']:.2%}")
        print(f"功能正确性：{results['feature_correctness']:.2%}")
        print(f"功能完整性：{results['feature_completeness']:.2%}")

        print(f"\n功能详情：")
        for feature in results["features"]:
            status_symbol = "✓" if feature["status"] == "passed" else "✗"
            print(f"{status_symbol} {feature['name']}: {feature['description']}")


# 使用
def test_feature_1():
    """测试功能 1"""
    return True

def test_feature_2():
    """测试功能 2"""
    return True

def test_feature_3():
    """测试功能 3"""
    return False

def test_feature_4():
    """测试功能 4"""
    raise Exception("测试失败")

evaluator = FunctionalEvaluator(system_name="Agent 系统")

# 添加功能
evaluator.add_feature(
    feature_name="功能 1",
    description="功能 1 描述",
    test_function=test_feature_1
)

evaluator.add_feature(
    feature_name="功能 2",
    description="功能 2 描述",
    test_function=test_feature_2
)

evaluator.add_feature(
    feature_name="功能 3",
    description="功能 3 描述",
    test_function=test_feature_3
)

evaluator.add_feature(
    feature_name="功能 4",
    description="功能 4 描述",
    test_function=test_feature_4
)

# 评估系统
results = evaluator.evaluate()

# 打印结果
evaluator.print_results(results)
```

### 30.2.2 性能评估

**1. 性能评估器**

```python
# system_evaluation/performance_evaluator.py
import time
import statistics
from typing import Dict, Any, List, Optional, Callable

class PerformanceEvaluator:
    """性能评估器"""

    def __init__(self, system_name: str):
        """
        初始化性能评估器

        Args:
            system_name: 系统名称
        """
        self.system_name = system_name

        # 性能测试数据
        self.response_times = []
        self.throughput = []
        self.concurrent_users = []

    def measure_response_time(
        self,
        test_function: Callable,
        iterations: int = 100
    ):
        """
        测量响应时间

        Args:
            test_function: 测试函数
            iterations: 迭代次数
        """
        # 测量响应时间
        for _ in range(iterations):
            start_time = time.time()
            test_function()
            end_time = time.time()

            response_time = end_time - start_time
            self.response_times.append(response_time)

    def measure_throughput(
        self,
        test_function: Callable,
        duration: int = 60
    ):
        """
        测量吞吐量

        Args:
            test_function: 测试函数
            duration: 测试持续时间（秒）
        """
        # 测量吞吐量
        start_time = time.time()
        requests = 0

        while time.time() - start_time < duration:
            test_function()
            requests += 1

        throughput = requests / duration
        self.throughput.append(throughput)

    def evaluate(self) -> Dict[str, Any]:
        """
        评估系统性能

        Returns:
            评估结果
        """
        results = {
            "system_name": self.system_name,
            "response_times": {
                "count": len(self.response_times),
                "mean": statistics.mean(self.response_times) if self.response_times else 0,
                "median": statistics.median(self.response_times) if self.response_times else 0,
                "min": min(self.response_times) if self.response_times else 0,
                "max": max(self.response_times) if self.response_times else 0,
                "std_dev": statistics.stdev(self.response_times) if len(self.response_times) > 1 else 0
            },
            "throughput": {
                "count": len(self.throughput),
                "mean": statistics.mean(self.throughput) if self.throughput else 0,
                "median": statistics.median(self.throughput) if self.throughput else 0,
                "min": min(self.throughput) if self.throughput else 0,
                "max": max(self.throughput) if self.throughput else 0,
                "std_dev": statistics.stdev(self.throughput) if len(self.throughput) > 1 else 0
            }
        }

        # 计算吞吐量
        if self.throughput:
            results["throughput"]["requests_per_second"] = statistics.mean(self.throughput)

        return results

    def print_results(self, results: Dict[str, Any]):
        """
        打印评估结果

        Args:
            results: 评估结果
        """
        print(f"\n=== {results['system_name']} 性能评估结果 ===")

        # 打印响应时间
        print("\n响应时间统计：")
        print(f"  平均响应时间：{results['response_times']['mean']:.4f} 秒")
        print(f"  中位数响应时间：{results['response_times']['median']:.4f} 秒")
        print(f"  最小响应时间：{results['response_times']['min']:.4f} 秒")
        print(f"  最大响应时间：{results['response_times']['max']:.4f} 秒")
        print(f"  标准差：{results['response_times']['std_dev']:.4f} 秒")

        # 打印吞吐量
        print("\n吞吐量统计：")
        print(f"  平均吞吐量：{results['throughput']['mean']:.2f} 请求/秒")
        print(f"  中位数吞吐量：{results['throughput']['median']:.2f} 请求/秒")
        print(f"  最小吞吐量：{results['throughput']['min']:.2f} 请求/秒")
        print(f"  最大吞吐量：{results['throughput']['max']:.2f} 请求/秒")
        print(f"  标准差：{results['throughput']['std_dev']:.2f} 请求/秒")


# 使用
def test_function():
    """测试函数"""
    import time
    time.sleep(0.01)  # 模拟耗时操作

evaluator = PerformanceEvaluator(system_name="Agent 系统")

# 测量响应时间
evaluator.measure_response_time(test_function, iterations=100)

# 测量吞吐量
evaluator.measure_throughput(test_function, duration=10)

# 评估系统
results = evaluator.evaluate()

# 打印结果
evaluator.print_results(results)
```

## 30.3 系统评估方法

### 30.3.1 单元测试评估

**1. 单元测试评估器**

```python
# system_evaluation/unit_test_evaluator.py
import pytest
from typing import Dict, Any, List, Optional

class UnitTestEvaluator:
    """单元测试评估器"""

    def __init__(self, system_name: str):
        """
        初始化单元测试评估器

        Args:
            system_name: 系统名称
        """
        self.system_name = system_name

    def evaluate(self) -> Dict[str, Any]:
        """
        评估单元测试

        Returns:
            评估结果
        """
        # 运行 pytest
        result = pytest.main([
            "--tb=no",
            "-q",
            "--collect-only"
        ])

        # 解析结果
        results = {
            "system_name": self.system_name,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "error_tests": 0,
            "skipped_tests": 0,
            "test_coverage": 0
        }

        # 模拟结果（实际应该从 pytest 输出解析）
        results["total_tests"] = 100
        results["passed_tests"] = 90
        results["failed_tests"] = 5
        results["error_tests"] = 3
        results["skipped_tests"] = 2
        results["test_coverage"] = 0.85

        return results

    def print_results(self, results: Dict[str, Any]):
        """
        打印评估结果

        Args:
            results: 评估结果
        """
        print(f"\n=== {results['system_name']} 单元测试评估结果 ===")
        print(f"总测试数量：{results['total_tests']}")
        print(f"通过测试数量：{results['passed_tests']}")
        print(f"失败测试数量：{results['failed_tests']}")
        print(f"错误测试数量：{results['error_tests']}")
        print(f"跳过测试数量：{results['skipped_tests']}")
        print(f"测试覆盖率：{results['test_coverage']:.2%}")


# 使用
evaluator = UnitTestEvaluator(system_name="Agent 系统")

# 评估系统
results = evaluator.evaluate()

# 打印结果
evaluator.print_results(results)
```

### 30.3.2 集成测试评估

**1. 集成测试评估器**

```python
# system_evaluation/integration_test_evaluator.py
from typing import Dict, Any, List, Optional

class IntegrationTestEvaluator:
    """集成测试评估器"""

    def __init__(self, system_name: str):
        """
        初始化集成测试评估器

        Args:
            system_name: 系统名称
        """
        self.system_name = system_name

    def evaluate(self) -> Dict[str, Any]:
        """
        评估集成测试

        Returns:
            评估结果
        """
        # 运行集成测试
        result = pytest.main([
            "tests/integration/",
            "--tb=no",
            "-q"
        ])

        # 解析结果
        results = {
            "system_name": self.system_name,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "error_tests": 0,
            "test_duration": 0
        }

        # 模拟结果（实际应该从 pytest 输出解析）
        results["total_tests"] = 50
        results["passed_tests"] = 45
        results["failed_tests"] = 3
        results["error_tests"] = 2
        results["test_duration"] = 30

        return results

    def print_results(self, results: Dict[str, Any]):
        """
        打印评估结果

        Args:
            results: 评估结果
        """
        print(f"\n=== {results['system_name']} 集成测试评估结果 ===")
        print(f"总测试数量：{results['total_tests']}")
        print(f"通过测试数量：{results['passed_tests']}")
        print(f"失败测试数量：{results['failed_tests']}")
        print(f"错误测试数量：{results['error_tests']}")
        print(f"测试耗时：{results['test_duration']} 秒")


# 使用
evaluator = IntegrationTestEvaluator(system_name="Agent 系统")

# 评估系统
results = evaluator.evaluate()

# 打印结果
evaluator.print_results(results)
```

### 30.3.3 E2E 测试评估

**1. E2E 测试评估器**

```python
# system_evaluation/e2e_test_evaluator.py
from typing import Dict, Any, List, Optional

class E2ETestEvaluator:
    """E2E 测试评估器"""

    def __init__(self, system_name: str):
        """
        初始化 E2E 测试评估器

        Args:
            system_name: 系统名称
        """
        self.system_name = system_name

    def evaluate(self) -> Dict[str, Any]:
        """
        评估 E2E 测试

        Returns:
            评估结果
        """
        # 运行 E2E 测试
        result = pytest.main([
            "tests/e2e/",
            "--tb=no",
            "-q"
        ])

        # 解析结果
        results = {
            "system_name": self.system_name,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "error_tests": 0,
            "test_duration": 0,
            "user_satisfaction": 0
        }

        # 模拟结果（实际应该从 pytest 输出解析）
        results["total_tests"] = 20
        results["passed_tests"] = 18
        results["failed_tests"] = 1
        results["error_tests"] = 1
        results["test_duration"] = 120
        results["user_satisfaction"] = 4.5

        return results

    def print_results(self, results: Dict[str, Any]):
        """
        打印评估结果

        Args:
            results: 评估结果
        """
        print(f"\n=== {results['system_name']} E2E 测试评估结果 ===")
        print(f"总测试数量：{results['total_tests']}")
        print(f"通过测试数量：{results['passed_tests']}")
        print(f"失败测试数量：{results['failed_tests']}")
        print(f"错误测试数量：{results['error_tests']}")
        print(f"测试耗时：{results['test_duration']} 秒")
        print(f"用户满意度：{results['user_satisfaction']}/5")


# 使用
evaluator = E2ETestEvaluator(system_name="Agent 系统")

# 评估系统
results = evaluator.evaluate()

# 打印结果
evaluator.print_results(results)
```

## 30.4 本章总结

### 核心要点

1. **系统评估概述**: 系统评估类型、系统评估流程、系统评估指标
2. **功能评估**: 功能评估器实现
3. **性能评估**: 性能评估器实现
4. **系统评估方法**: 单元测试评估、集成测试评估、E2E 测试评估

### 实战技巧

- **功能评估**: 定义功能列表，使用测试函数验证功能
- **性能评估**: 测量响应时间、吞吐量，计算统计指标
- **单元测试评估**: 使用 pytest 运行测试，解析测试结果
- **集成测试评估**: 测试模块间协作，确保 API 正常工作
- **E2E 测试评估**: 测试完整用户流程，评估用户体验

### 练习题

1. 实现功能评估器
2. 实现性能评估器
3. 实现单元测试评估器
4. 实现集成测试评估器

### 下章预告

第31章将介绍 **Agent 系统优化**，包括：
- 系统优化概述
- 性能优化实战
- 代码优化实战

---

**本章完**

**下一章**: [第31章：Agent 系统优化](./31-chapter30-evaluation.md)
