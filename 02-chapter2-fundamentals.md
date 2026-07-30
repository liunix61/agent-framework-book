# 第2章：Python/C++ Agent 开发基础

## 本章目标

掌握 Python 和 C++ Agent 开发的基础知识，包括 LLM API 使用、Prompt Engineering 实战、简单 Agent 的实现。

## 前置知识

- **基础编程知识**: Python/C++（至少一种）
- **基础 AI 知识**: LLM、Prompt Engineering 基本概念
- **基础网络知识**: HTTP、REST API

## 2.1 LLM API 基础

### 2.1.1 OpenAI API

**官方文档**: https://platform.openai.com/docs

**基本用法**:

```python
from openai import OpenAI

# 初始化客户端
client = OpenAI(api_key="your-api-key")

# 简单对话
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "你是一个写作助手"},
        {"role": "user", "content": "请写一篇关于AI的文章"}
    ]
)

print(response.choices[0].message.content)
```

**流式输出**:

```python
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "写一首诗"}
    ],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

**Function Calling**:

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
                    "city": {"type": "string", "description": "城市名称"}
                },
                "required": ["city"]
            }
        }
    }
]

# 调用API
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "北京今天天气怎么样？"}
    ],
    tools=tools,
    tool_choice="auto"
)

# 检查是否需要调用工具
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        # 调用工具
        if function_name == "get_weather":
            result = get_weather(arguments["city"])
            print(result)
```

### 2.1.2 Claude API

**官方文档**: https://docs.anthropic.com

**基本用法**:

```python
import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

message = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "请写一篇关于AI的文章"}
    ]
)

print(message.content[0].text)
```

**系统提示词**:

```python
message = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=1024,
    system="你是一个专业的写作助手，擅长写文章、博客、报告。",
    messages=[
        {"role": "user", "content": "请写一篇关于AI的文章"}
    ]
)
```

### 2.1.3 本地模型（Llama3）

**官方文档**: https://llama.meta.com

**使用 Ollama**:

```bash
# 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 下载模型
ollama pull llama3

# 运行模型
ollama run llama3
```

**Python 调用**:

```python
import ollama

# 简单对话
response = ollama.chat(model='llama3', messages=[
  {'role': 'user', 'content': '写一首诗'},
])

print(response['message']['content'])
```

**批量推理**:

```python
import ollama

prompts = [
    "写一篇关于AI的文章",
    "写一首关于春天的诗",
    "解释量子计算"
]

for prompt in prompts:
    response = ollama.chat(model='llama3', messages=[
        {'role': 'user', 'content': prompt}
    ])
    print(f"Prompt: {prompt}")
    print(f"Response: {response['message']['content']}\n")
```

### 2.1.4 其他 LLM API

| 模型 | API | 价格 | 特点 |
|------|-----|------|------|
| GPT-4 | OpenAI API | $0.03/1K tokens | 最强推理能力 |
| Claude 3.5 Sonnet | Anthropic API | $3/1M tokens | 上下文窗口大 |
| Llama3 | Ollama（本地） | 免费 | 开源、可定制 |
| Qwen2 | Alibaba API | $0.2/1M tokens | 中文能力强 |

## 2.2 Prompt Engineering 实战

### 2.2.1 Few-Shot Prompting

**问题**: 让模型生成代码时，模型经常写错

**Few-Shot Prompting**:

```
你是一个Python编程助手。请根据以下示例生成代码：

示例1：
用户: 写一个快速排序
助手:
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

示例2：
用户: 写一个斐波那契数列生成器
助手:
def fibonacci(n):
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib[:n]

用户: 写一个二分查找算法
助手:
```

### 2.2.2 Chain-of-Thought（CoT）

**问题**: 让模型进行推理时，模型经常直接给出答案，缺少推理过程

**CoT Prompting**:

```
用户: 一列火车以每小时60公里的速度行驶，行驶了2小时。然后以每小时80公里的速度行驶了3小时。总行驶距离是多少？

思考过程：
1. 第一段距离 = 速度1 × 时间1 = 60 × 2 = 120公里
2. 第二段距离 = 速度2 × 时间2 = 80 × 3 = 240公里
3. 总距离 = 第一段距离 + 第二段距离 = 120 + 240 = 360公里

答案：360公里
```

### 2.2.3 ReAct（Reasoning + Acting）

**问题**: 模型需要调用工具时，不知道如何使用工具

**ReAct Prompting**:

```
你是一个智能助手，可以使用工具完成任务。

可用工具：
- search_web(query): 搜索网页
- get_weather(city): 获取天气信息

任务：北京今天天气怎么样？

思考：
用户想了解北京的天气，我需要使用get_weather工具。

行动：
search_web("北京天气")

观察：
搜索结果：北京今天天气晴，气温15-25摄氏度

思考：
我已经获得了天气信息，可以回答用户的问题。

答案：
北京今天天气晴，气温15-25摄氏度。
```

### 2.2.4 Structured Output

**问题**: 模型生成的JSON格式不规范

**Structured Output**:

```python
from openai import OpenAI

client = OpenAI(api_key="your-api-key")

response = client.chat.completions.create(
    model="gpt-4",
    response_format={"type": "json_object"},
    messages=[
        {
            "role": "system",
            "content": "你是一个数据分析师，请分析以下文本并返回JSON格式的结果。JSON格式：{\"sentiment\": \"positive/negative/neutral\", \"summary\": \"摘要\", \"keywords\": [\"关键词1\", \"关键词2\"]}"
        },
        {
            "role": "user",
            "content": "今天的AI技术发展非常迅速，新的模型不断涌现，让人感到兴奋。"
        }
    ]
)

result = json.loads(response.choices[0].message.content)
print(result)
```

### 2.2.5 Prompt 优化技巧

**技巧1**: 明确角色和职责

```
❌ 错误：
请写一篇文章。

✅ 正确：
你是一个专业的技术写作助手，擅长写技术文章、博客、报告。请写一篇关于Agent的文章。
```

**技巧2**: 提供详细的示例

```
❌ 错误：
写一个排序函数。

✅ 正确：
你是一个Python编程助手。请根据以下示例生成代码：

示例1：
def quicksort(arr):
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
```

**技巧3**: 设置输出格式约束

```
❌ 错误：
请分析这段文本。

✅ 正确：
你是一个数据分析师。请分析以下文本，并以JSON格式返回结果。

JSON格式：
{
  "sentiment": "positive/negative/neutral",
  "summary": "摘要",
  "keywords": ["关键词1", "关键词2"]
}

文本：今天的AI技术发展非常迅速，新的模型不断涌现，让人感到兴奋。
```

**技巧4**: 逐步引导

```
❌ 错误：
请写一篇关于Agent的文章。

✅ 正确：
你是一个写作助手。请按照以下步骤写一篇关于Agent的文章：

步骤1: 写一个Agent的定义
步骤2: 写一个Agent的例子
步骤3: 写一个Agent的应用场景
步骤4: 总结Agent的重要性

请按照步骤逐个完成。
```

## 2.3 简单 Agent 的实现

### 2.3.1 Python Agent 基础实现

**项目结构**:

```
simple-agent/
├── agent.py
├── tools.py
├── main.py
└── requirements.txt
```

**agent.py**:

```python
from openai import OpenAI
import json

class SimpleAgent:
    def __init__(self, api_key, model="gpt-4"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.messages = [
            {"role": "system", "content": "你是一个智能助手"}
        ]

    def add_message(self, role, content):
        """添加消息到对话历史"""
        self.messages.append({"role": role, "content": content})

    def chat(self, user_message):
        """与Agent对话"""
        self.add_message("user", user_message)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )

        assistant_message = response.choices[0].message.content
        self.add_message("assistant", assistant_message)

        return assistant_message

    def clear_history(self):
        """清除对话历史"""
        self.messages = [
            {"role": "system", "content": "你是一个智能助手"}
        ]
```

**tools.py**:

```python
import requests

def get_weather(city):
    """获取天气信息"""
    # 这里可以调用真实的天气API
    # 例如：https://api.openweathermap.org/data/2.5/weather
    return f"{city}今天天气晴，气温15-25摄氏度"

def search_web(query):
    """搜索网页"""
    # 这里可以调用真实的搜索API
    # 例如：Google Custom Search API
    return f"搜索结果：关于{query}的相关信息"

def calculate(expression):
    """计算表达式"""
    try:
        result = eval(expression)
        return f"计算结果：{result}"
    except:
        return "计算错误，请检查表达式"
```

**main.py**:

```python
from agent import SimpleAgent
from tools import get_weather, search_web, calculate

def main():
    # 初始化Agent
    agent = SimpleAgent(api_key="your-api-key", model="gpt-4")

    # 设置系统提示词
    agent.add_message("system", """
        你是一个智能助手，可以使用以下工具：
        - get_weather(city): 获取天气信息
        - search_web(query): 搜索网页
        - calculate(expression): 计算表达式

        请根据用户的问题，决定是否需要调用工具。
    """)

    # 对话
    while True:
        user_message = input("用户: ")
        if user_message.lower() in ["exit", "quit", "退出"]:
            break

        # 检查是否需要调用工具
        if "天气" in user_message:
            # 提取城市名称
            city = user_message.replace("天气", "").replace("北京", "").strip()
            result = get_weather(city)
            print(f"助手: {result}")
            agent.add_message("user", user_message)
            agent.add_message("assistant", result)
        elif "搜索" in user_message or "查找" in user_message:
            query = user_message.replace("搜索", "").replace("查找", "").strip()
            result = search_web(query)
            print(f"助手: {result}")
            agent.add_message("user", user_message)
            agent.add_message("assistant", result)
        elif "计算" in user_message or "等于" in user_message:
            expression = user_message.replace("计算", "").replace("等于", "").strip()
            result = calculate(expression)
            print(f"助手: {result}")
            agent.add_message("user", user_message)
            agent.add_message("assistant", result)
        else:
            # 调用LLM
            response = agent.chat(user_message)
            print(f"助手: {response}")

if __name__ == "__main__":
    main()
```

**requirements.txt**:

```
openai>=1.0.0
```

**运行**:

```bash
pip install -r requirements.txt
python main.py
```

### 2.3.2 C++ Agent 基础实现

**项目结构**:

```
simple-agent-cpp/
├── CMakeLists.txt
├── agent.cpp
├── tools.cpp
├── tools.h
└── main.cpp
```

**tools.h**:

```cpp
#pragma once

#include <string>

std::string get_weather(const std::string& city);
std::string search_web(const std::string& query);
std::string calculate(const std::string& expression);
```

**tools.cpp**:

```cpp
#include "tools.h"
#include <iostream>
#include <sstream>
#include <cmath>

std::string get_weather(const std::string& city) {
    return city + "今天天气晴，气温15-25摄氏度";
}

std::string search_web(const std::string& query) {
    return "搜索结果：关于" + query + "的相关信息";
}

std::string calculate(const std::string& expression) {
    std::istringstream iss(expression);
    double result;
    if (!(iss >> result)) {
        return "计算错误，请检查表达式";
    }
    return "计算结果：" + std::to_string(result);
}
```

**agent.h**:

```cpp
#pragma once

#include <string>
#include <vector>
#include <memory>

class Agent {
public:
    Agent(const std::string& api_key, const std::string& model = "gpt-4");
    ~Agent();

    void add_message(const std::string& role, const std::string& content);
    std::string chat(const std::string& user_message);
    void clear_history();

private:
    std::string api_key_;
    std::string model_;
    std::vector<std::pair<std::string, std::string>> messages_;
};
```

**agent.cpp**:

```cpp
#include "agent.h"
#include <curl/curl.h>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

static size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp) {
    ((std::string*)userp)->append((char*)contents, size * nmemb);
    return size * nmemb;
}

Agent::Agent(const std::string& api_key, const std::string& model)
    : api_key_(api_key), model_(model) {
    messages_.push_back({"system", "你是一个智能助手"});
}

Agent::~Agent() {
    curl_global_cleanup();
}

void Agent::add_message(const std::string& role, const std::string& content) {
    messages_.push_back({role, content});
}

std::string Agent::chat(const std::string& user_message) {
    add_message("user", user_message);

    CURL* curl = curl_easy_init();
    std::string readBuffer;

    json requestBody = {
        {"model", model_},
        {"messages", json::array()}
    };

    for (const auto& msg : messages_) {
        requestBody["messages"].push_back({
            {"role", msg.first},
            {"content", msg.second}
        });
    }

    std::string requestBodyStr = requestBody.dump();

    struct curl_slist* headers = nullptr;
    headers = curl_slist_append(headers, "Content-Type: application/json");
    headers = curl_slist_append(headers, ("Authorization: Bearer " + api_key_).c_str());

    curl_easy_setopt(curl, CURLOPT_URL, "https://api.openai.com/v1/chat/completions");
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, requestBodyStr.c_str());
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);

    CURLcode res = curl_easy_perform(curl);
    curl_easy_cleanup(curl);

    if (res != CURLE_OK) {
        return "错误：无法连接到OpenAI API";
    }

    json response = json::parse(readBuffer);
    std::string assistantMessage = response["choices"][0]["message"]["content"];

    add_message("assistant", assistantMessage);

    return assistantMessage;
}

void Agent::clear_history() {
    messages_.clear();
    messages_.push_back({"system", "你是一个智能助手"});
}
```

**main.cpp**:

```cpp
#include "agent.h"
#include "tools.h"
#include <iostream>
#include <string>

void print_menu() {
    std::cout << "\n===== 智能助手菜单 =====\n";
    std::cout << "1. 查询天气\n";
    std::cout << "2. 搜索网页\n";
    std::cout << "3. 计算表达式\n";
    std::cout << "4. 对话\n";
    std::cout << "0. 退出\n";
    std::cout << "========================\n";
    std::cout << "请选择: ";
}

int main() {
    curl_global_init(CURL_GLOBAL_ALL);

    std::string api_key;
    std::cout << "请输入OpenAI API Key: ";
    std::cin >> api_key;

    Agent agent(api_key);

    int choice;
    while (true) {
        print_menu();
        std::cin >> choice;

        switch (choice) {
            case 1: {
                std::string city;
                std::cout << "请输入城市: ";
                std::cin >> city;
                std::cout << "助手: " << get_weather(city) << std::endl;
                break;
            }
            case 2: {
                std::string query;
                std::cout << "请输入搜索关键词: ";
                std::cin >> query;
                std::cout << "助手: " << search_web(query) << std::endl;
                break;
            }
            case 3: {
                std::string expression;
                std::cout << "请输入计算表达式: ";
                std::cin >> expression;
                std::cout << "助手: " << calculate(expression) << std::endl;
                break;
            }
            case 4: {
                std::string message;
                std::cout << "用户: ";
                std::cin.ignore();
                std::getline(std::cin, message);
                std::cout << "助手: " << agent.chat(message) << std::endl;
                break;
            }
            case 0: {
                std::cout << "退出程序\n";
                goto cleanup;
            }
            default: {
                std::cout << "无效选择，请重试\n";
                break;
            }
        }
    }

cleanup:
    curl_global_cleanup();
    return 0;
}
```

**CMakeLists.txt**:

```cmake
cmake_minimum_required(VERSION 3.10)
project(SimpleAgentCpp)

set(CMAKE_CXX_STANDARD 17)

# 查找依赖
find_package(CURL REQUIRED)
find_package(nlohmann_json REQUIRED)

# 添加可执行文件
add_executable(simple-agent agent.cpp tools.cpp main.cpp)

# 链接库
target_link_libraries(simple-agent CURL::libcurl nlohmann_json::nlohmann_json)
```

**编译运行**:

```bash
mkdir build && cd build
cmake ..
make
./simple-agent
```

## 2.4 本章总结

### 核心要点

1. **LLM API 基础**: OpenAI、Claude、本地模型（Llama3）
2. **Prompt Engineering**: Few-Shot、CoT、ReAct、Structured Output
3. **简单 Agent 实现**: Python 和 C++ 基础实现
4. **工具调用**: Function Calling、工具管理

### 代码示例

- Python 简单 Agent（agent.py、tools.py、main.py）
- C++ 简单 Agent（agent.cpp、tools.cpp、main.cpp）

### 练习题

1. 尝试使用不同的 LLM API（Claude、本地模型）实现简单 Agent
2. 实现一个支持多个工具的 Agent
3. 实现 Agent 的记忆功能（保存对话历史）

### 下章预告

第3章将介绍 **环境搭建与工具链**，包括：
- Python 环境搭建（venv、conda、pip）
- C++ 环境搭建（GCC、CMake、VSCode）
- Agent 开发工具（IDE、调试工具、性能分析工具）
- 数据库（PostgreSQL、Redis）配置
- 测试框架（pytest、Google Test）配置

---

**本章完**

**下一章**: [第3章：环境搭建与工具链](./03-chapter3-setup.md)
