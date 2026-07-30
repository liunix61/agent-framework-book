# 第4章：Prompt Engineering 进阶

## 本章目标

深入掌握高级 Prompt Engineering 技巧，包括 Chain-of-Thought、ReAct、Self-Consistency、Tool Use 等。

## 前置知识

- **基础 Prompt Engineering**: Few-Shot、系统提示词
- **基础 LLM API**: OpenAI、Claude、本地模型
- **基础 Python/C++**: 函数调用、异常处理

## 4.1 Chain-of-Thought（CoT）深入解析

### 4.1.1 什么是 CoT

**Chain-of-Thought（思维链）** 是一种让模型逐步推理的 Prompt 技术，通过展示推理过程来提高推理准确性。

**论文**: "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" (2022)

**核心思想**:
```
传统Prompt: 直接给出答案
CoT Prompt: 思考过程 → 答案
```

### 4.1.2 CoT 示例对比

**传统 Prompt**:

```
用户: 一列火车以每小时60公里的速度行驶，行驶了2小时。然后以每小时80公里的速度行驶了3小时。总行驶距离是多少？

助手: 360公里
```

**CoT Prompt**:

```
用户: 一列火车以每小时60公里的速度行驶，行驶了2小时。然后以每小时80公里的速度行驶了3小时。总行驶距离是多少？

思考过程：
1. 第一段距离 = 速度1 × 时间1 = 60 × 2 = 120公里
2. 第二段距离 = 速度2 × 时间2 = 80 × 3 = 240公里
3. 总距离 = 第一段距离 + 第二段距离 = 120 + 240 = 360公里

答案：360公里
```

**效果对比**:
- 传统 Prompt：正确率 ~80%
- CoT Prompt：正确率 ~90%

### 4.1.3 CoT 自动化

**OpenAI 支持 CoT 自动化**:

```python
from openai import OpenAI

client = OpenAI(api_key="your-api-key")

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "system",
            "content": "请逐步思考，然后给出答案。"
        },
        {
            "role": "user",
            "content": "一列火车以每小时60公里的速度行驶，行驶了2小时。然后以每小时80公里的速度行驶了3小时。总行驶距离是多少？"
        }
    ],
    temperature=0,  # 降低温度，强制推理
    max_tokens=1024
)

print(response.choices[0].message.content)
```

**输出**:

```
思考过程：
1. 第一段距离 = 60公里/小时 × 2小时 = 120公里
2. 第二段距离 = 80公里/小时 × 3小时 = 240公里
3. 总距离 = 120公里 + 240公里 = 360公里

答案：360公里
```

### 4.1.4 CoT 的变体

**Zero-Shot CoT**:

```
用户: 请逐步思考，然后给出答案。一列火车以每小时60公里的速度行驶，行驶了2小时。然后以每小时80公里的速度行驶了3小时。总行驶距离是多少？
```

**Few-Shot CoT**:

```
用户: 请逐步思考，然后给出答案。

示例1：
问题: 12 + 15 × 3 = ?
思考过程：
1. 先计算乘法：15 × 3 = 45
2. 再计算加法：12 + 45 = 57
答案：57

示例2：
问题: 100 - 20 × 4 = ?
思考过程：
1. 先计算乘法：20 × 4 = 80
2. 再计算减法：100 - 80 = 20
答案：20

问题: 一列火车以每小时60公里的速度行驶，行驶了2小时。然后以每小时80公里的速度行驶了3小时。总行驶距离是多少？
```

### 4.1.5 CoT 在 Agent 中的应用

**Agent 推理流程**:

```
用户: 帮我查一下北京的天气

Agent CoT Prompt:
思考过程：
1. 用户想了解北京的天气
2. 我需要调用 get_weather 工具
3. 参数是 city="北京"

行动：
search_web("北京天气")

观察：
搜索结果：北京今天天气晴，气温15-25摄氏度

思考过程：
1. 我已经获得了天气信息
2. 可以回答用户的问题

答案：
北京今天天气晴，气温15-25摄氏度。
```

## 4.2 ReAct 框架详解

### 4.2.1 什么是 ReAct

**ReAct（Reasoning + Acting）** 是一种让 Agent 能够推理并调用工具的框架。

**论文**: "ReAct: Synergizing Reasoning and Acting in Language Models" (2022)

**核心思想**:
```
思考 → 行动 → 观察 → 思考 →  → 答案
```

### 4.2.2 ReAct 工作流程

```
步骤1: 思考
用户想了解北京的天气，我需要调用 get_weather 工具。

步骤2: 行动
search_web("北京天气")

步骤3: 观察
搜索结果：北京今天天气晴，气温15-25摄氏度

步骤4: 思考
我已经获得了天气信息，可以回答用户的问题。

步骤5: 答案
北京今天天气晴，气温15-25摄氏度。
```

### 4.2.3 ReAct Prompt 模板

```python
REACT_PROMPT_TEMPLATE = """
你是一个智能助手，可以使用以下工具：
{tools}

任务：{task}

请按照以下格式回答：

思考：
{thought}

行动：
{action}

观察：
{observation}

答案：
{answer}
"""

TOOLS = [
    {
        "name": "get_weather",
        "description": "获取天气信息",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称"
                }
            },
            "required": ["city"]
        }
    }
]
```

### 4.2.4 ReAct 实现代码

```python
from openai import OpenAI
import json

class ReActAgent:
    def __init__(self, api_key, model="gpt-4"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.tools = [
            {
                "name": "get_weather",
                "description": "获取天气信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "城市名称"
                        }
                    },
                    "required": ["city"]
                }
            }
        ]

    def _get_tool_call(self, thought, task):
        """让模型决定是否需要调用工具"""
        prompt = f"""
        你是一个智能助手，可以使用以下工具：
        {self.tools}

        任务：{task}

        思考：{thought}

        请决定是否需要调用工具。如果需要，请以JSON格式返回：
        {{
            "action": "tool_name",
            "action_input": "参数"
        }}

        如果不需要，请返回：
        {{
            "action": "final_answer",
            "action_input": "答案"
        }}
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result

    def _execute_tool(self, tool_name, action_input):
        """执行工具调用"""
        if tool_name == "get_weather":
            return f"天气信息：{action_input}今天天气晴，气温15-25摄氏度"
        else:
            return "工具不存在"

    def run(self, task):
        """运行 ReAct Agent"""
        messages = [
            {
                "role": "system",
                "content": "你是一个智能助手，可以使用工具完成任务。"
            },
            {
                "role": "user",
                "content": f"任务：{task}"
            }
        ]

        while True:
            # 让模型思考
            thought = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1024
            ).choices[0].message.content

            # 决定是否调用工具
            decision = self._get_tool_call(thought, task)

            if decision["action"] == "final_answer":
                return decision["action_input"]

            # 执行工具
            observation = self._execute_tool(
                decision["action"],
                decision["action_input"]
            )

            # 添加到消息历史
            messages.append({"role": "assistant", "content": thought})
            messages.append({
                "role": "tool",
                "content": f"观察：{observation}"
            })

# 使用
agent = ReActAgent(api_key="your-api-key")
result = agent.run("北京的天气怎么样？")
print(result)
```

### 4.2.5 ReAct vs CoT

| 维度 | ReAct | CoT |
|------|-------|-----|
| **核心** | 推理 + 行动 | 推理 |
| **工具调用** | ✅ 支持 | ❌ 不支持 |
| **多轮交互** | ✅ 支持 | ❌ 不支持 |
| **适用场景** | Agent、工具调用 | 数学推理、逻辑推理 |
| **复杂度** | 较高 | 较低 |

## 4.3 Self-Consistency

### 4.3.1 什么是 Self-Consistency

**Self-Consistency（自洽性）** 是一种通过多次采样，选择最一致的答案来提高准确率的 Prompt 技术。

**论文**: "Self-Consistency Improves Chain of Thought Reasoning in Large Language Models" (2022)

**核心思想**:
```
多次采样 → 多个答案 → 选择最一致的答案
```

### 4.3.2 Self-Consistency 示例

**问题**: 一列火车以每小时60公里的速度行驶，行驶了2小时。然后以每小时80公里的速度行驶了3小时。总行驶距离是多少？

**采样1**:
```
思考过程：
1. 第一段距离 = 60 × 2 = 120公里
2. 第二段距离 = 80 × 3 = 240公里
3. 总距离 = 120 + 240 = 360公里

答案：360公里
```

**采样2**:
```
思考过程：
1. 第一段距离 = 60 × 2 = 120公里
2. 第二段距离 = 80 × 3 = 240公里
3. 总距离 = 120 + 240 = 360公里

答案：360公里
```

**采样3**:
```
思考过程：
1. 第一段距离 = 60 × 2 = 120公里
2. 第二段距离 = 80 × 3 = 240公里
3. 总距离 = 120 + 240 = 360公里

答案：360公里
```

**结论**: 360公里（3次采样一致）

### 4.3.3 Self-Consistency 实现

```python
from openai import OpenAI
import json
from collections import Counter

class SelfConsistencyAgent:
    def __init__(self, api_key, model="gpt-4", num_samples=3):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.num_samples = num_samples

    def _generate_answer(self, task):
        """生成单个答案"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "请逐步思考，然后给出答案。"
                },
                {
                    "role": "user",
                    "content": task
                }
            ],
            temperature=0.7,
            max_tokens=1024
        )
        return response.choices[0].message.content

    def _extract_answer(self, response):
        """从响应中提取答案"""
        # 提取"答案："后面的内容
        if "答案：" in response:
            return response.split("答案：")[1].strip()
        else:
            return response

    def run(self, task):
        """运行 Self-Consistency Agent"""
        answers = []

        # 多次采样
        for i in range(self.num_samples):
            print(f"采样 {i+1}/{self.num_samples}")
            response = self._generate_answer(task)
            answer = self._extract_answer(response)
            answers.append(answer)
            print(f"答案：{answer}\n")

        # 统计最频繁的答案
        counter = Counter(answers)
        most_common = counter.most_common(1)[0]

        return {
            "answers": answers,
            "most_common": most_common[0],
            "frequency": most_common[1]
        }

# 使用
agent = SelfConsistencyAgent(api_key="your-api-key", num_samples=5)
result = agent.run("一列火车以每小时60公里的速度行驶，行驶了2小时。然后以每小时80公里的速度行驶了3小时。总行驶距离是多少？")

print(f"答案：{result['most_common']}")
print(f"频率：{result['frequency']}/{result['num_samples']}")
```

### 4.3.4 Self-Consistency 优化

**温度调整**:
```python
# 低温度（0.1-0.3）：推理更一致
response = client.chat.completions.create(
    model="gpt-4",
    temperature=0.2,  # 降低温度
    
)

# 高温度（0.7-1.0）：更多样化
response = client.chat.completions.create(
    model="gpt-4",
    temperature=0.7,  # 提高温度
    
)
```

**采样数量**:
```python
# 3-5次采样：平衡成本和效果
agent = SelfConsistencyAgent(api_key="your-api-key", num_samples=5)

# 10-20次采样：更高准确率，但成本更高
agent = SelfConsistencyAgent(api_key="your-api-key", num_samples=10)
```

## 4.4 Tool Use 与 Function Calling

### 4.4.1 Function Calling 基础

**Function Calling（函数调用）** 是 OpenAI 推出的一种让模型能够调用函数的工具。

**基本用法**:

```python
from openai import OpenAI

client = OpenAI(api_key="your-api-key")

# 定义工具
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

# 调用 API
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "北京的天气怎么样？"}
    ],
    tools=tools,
    tool_choice="auto"
)

# 检查是否需要调用工具
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        print(f"工具：{function_name}")
        print(f"参数：{arguments}")

        # 执行工具
        result = execute_tool(function_name, arguments)
        print(f"结果：{result}")
```

### 4.4.2 多工具调用

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "搜索网页",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "搜索北京的天气"}
    ],
    tools=tools,
    tool_choice="auto"
)

# 处理工具调用
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        result = execute_tool(function_name, arguments)
        print(f"{function_name}({arguments}) = {result}")
```

### 4.4.3 工具调用链

```python
def execute_tool_call(tool_call):
    """执行工具调用"""
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    # 工具函数映射
    tool_functions = {
        "get_weather": get_weather,
        "search_web": search_web,
        "calculate": calculate
    }

    if function_name in tool_functions:
        return tool_functions[function_name](**arguments)
    else:
        return "工具不存在"

# 工具函数
def get_weather(city):
    return f"{city}今天天气晴，气温15-25摄氏度"

def search_web(query):
    return f"搜索结果：关于{query}的相关信息"

def calculate(expression):
    try:
        result = eval(expression)
        return f"计算结果：{result}"
    except:
        return "计算错误"

# 主循环
while True:
    user_message = input("用户: ")
    if user_message.lower() in ["exit", "quit"]:
        break

    # 调用 API
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "你是一个智能助手，可以使用以下工具：get_weather、search_web、calculate"},
            {"role": "user", "content": user_message}
        ],
        tools=tools,
        tool_choice="auto"
    )

    # 处理工具调用
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            result = execute_tool_call(tool_call)
            print(f"助手: {result}")
    else:
        answer = response.choices[0].message.content
        print(f"助手: {answer}")
```

## 4.5 Prompt 优化实战案例

### 4.5.1 代码生成优化

**问题**: 模型生成的代码经常有错误

**优化前**:

```
用户: 写一个快速排序
助手: def quicksort(arr): 
```

**优化后**:

```
用户: 你是一个Python编程助手。请根据以下示例生成代码：

示例1：
用户: 写一个快速排序
助手: def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

用户: 写一个二分查找算法
助手: def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

用户: 写一个斐波那契数列生成器
助手: def fibonacci(n):
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib[:n]
```

### 4.5.2 数据分析优化

**问题**: 模型生成的分析结果不准确

**优化前**:

```
用户: 分析这段文本的情感
助手: 情感是正面的。
```

**优化后**:

```
用户: 你是一个数据分析师。请分析以下文本，并以JSON格式返回结果。

JSON格式：
{
  "sentiment": "positive/negative/neutral",
  "summary": "摘要",
  "keywords": ["关键词1", "关键词2"]
}

文本：今天的AI技术发展非常迅速，新的模型不断涌现，让人感到兴奋。

思考过程：
1. 文本提到了"发展迅速"、"不断涌现"、"兴奋"等词汇，说明情感是正面的
2. 摘要：AI技术快速发展，新模型不断涌现
3. 关键词：AI、技术、发展、模型、涌现

答案：{"sentiment": "positive", "summary": "AI技术快速发展，新模型不断涌现", "keywords": ["AI", "技术", "发展", "模型", "涌现"]}
```

### 4.5.3 多语言翻译优化

**问题**: 模型翻译结果不准确

**优化前**:

```
用户: 将"Hello, world"翻译成中文
助手: 你好，世界
```

**优化后**:

```
用户: 你是一个专业的翻译助手。请将以下文本翻译成中文，并保持专业术语的准确性。

原文：Hello, world

翻译要求：
1. 保持专业术语的准确性
2. 保持句子的通顺
3. 保持原文的语气

翻译：你好，世界
```

## 4.6 本章总结

### 核心要点

1. **Chain-of-Thought**: 逐步推理，提高准确性
2. **ReAct**: 推理 + 行动，支持工具调用
3. **Self-Consistency**: 多次采样，选择最一致的答案
4. **Function Calling**: 让模型调用函数
5. **Prompt 优化**: 明确角色、提供示例、设置格式

### 实战技巧

- **CoT**: 使用"思考过程："引导模型逐步推理
- **ReAct**: 使用"思考 → 行动 → 观察 → 答案"格式
- **Self-Consistency**: 多次采样（3-5次），选择最频繁的答案
- **Function Calling**: 定义工具，让模型决定是否调用
- **Prompt 优化**: 明确角色、提供示例、设置格式

### 练习题

1. 使用 CoT 实现一个数学推理 Agent
2. 使用 ReAct 实现一个支持工具调用的 Agent
3. 使用 Self-Consistency 实现一个高准确率的推理 Agent
4. 使用 Function Calling 实现一个代码生成 Agent

### 下章预告

第5章将介绍 **Context 管理**，包括：
- 短期记忆 vs 长期记忆
- 向量数据库
- 检索增强生成（RAG）
- 记忆系统架构设计

---

**本章完**

**下一章**: [第5章：Context 管理](./05-chapter5-context-management.md)
