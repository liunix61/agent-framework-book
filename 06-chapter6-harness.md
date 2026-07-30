# 第6章：Harness 工具框架

## 本章目标

掌握 Agent 的工具框架，包括工具的定义、注册、调用、参数验证、错误处理等。

## 前置知识

- **基础 Python/C++**: 函数、类、装饰器
- **基础 LLM API**: Function Calling
- **基础异常处理**: try-except

## 6.1 工具的定义与注册

### 6.1.1 什么是工具（Tool）

**工具（Tool）** 是 Agent 能够调用的外部功能或服务。

**工具类型**:
- **API 调用**: HTTP 请求、REST API、GraphQL
- **数据库操作**: CRUD、查询、更新
- **文件操作**: 读写文件、压缩、解压
- **系统操作**: 执行命令、系统调用
- **第三方服务**: 天气、地图、翻译等

### 6.1.2 工具的定义

**Python 工具定义**:

```python
from typing import Dict, Any, List
import inspect

class Tool:
    """工具基类"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.parameters = self._get_parameters()

    def _get_parameters(self) -> List[Dict[str, Any]]:
        """获取工具参数"""
        signature = inspect.signature(self.execute)
        parameters = []

        for param_name, param in signature.parameters.items():
            if param_name == "self":
                continue

            param_info = {
                "name": param_name,
                "type": str(param.annotation).replace("typing.", ""),
                "description": f"{param.annotation} - {param.name}",
                "required": param.default == inspect.Parameter.empty
            }

            if param.default != inspect.Parameter.empty:
                param_info["default"] = param.default

            parameters.append(param_info)

        return parameters

    def execute(self, **kwargs) -> Any:
        """执行工具"""
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"Tool(name={self.name}, description={self.description})"


# 示例工具
class GetWeatherTool(Tool):
    """获取天气工具"""

    def __init__(self):
        super().__init__(
            name="get_weather",
            description="获取指定城市的天气信息"
        )

    def execute(self, city: str) -> str:
        """执行工具"""
        # 这里可以调用真实的天气 API
        return f"{city}今天天气晴，气温15-25摄氏度"


class SearchWebTool(Tool):
    """搜索网页工具"""

    def __init__(self):
        super().__init__(
            name="search_web",
            description="搜索网页内容"
        )

    def execute(self, query: str) -> str:
        """执行工具"""
        # 这里可以调用真实的搜索 API
        return f"搜索结果：关于{query}的相关信息"


class CalculateTool(Tool):
    """计算工具"""

    def __init__(self):
        super().__init__(
            name="calculate",
            description="计算数学表达式"
        )

    def execute(self, expression: str) -> str:
        """执行工具"""
        try:
            result = eval(expression)
            return f"计算结果：{result}"
        except Exception as e:
            return f"计算错误：{str(e)}"
```

### 6.1.3 工具注册

**工具注册器**:

```python
class ToolRegistry:
    """工具注册器"""

    def __init__(self):
        self.tools = {}

    def register(self, tool: Tool):
        """注册工具"""
        self.tools[tool.name] = tool
        print(f"已注册工具：{tool.name}")

    def get_tool(self, name: str) -> Tool:
        """获取工具"""
        if name not in self.tools:
            raise ValueError(f"工具 {name} 不存在")
        return self.tools[name]

    def list_tools(self) -> List[str]:
        """列出所有工具"""
        return list(self.tools.keys())

    def get_tool_schema(self) -> List[Dict[str, Any]]:
        """获取工具模式（用于 LLM）"""
        schemas = []

        for tool in self.tools.values():
            schema = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            param["name"]: {
                                "type": param["type"],
                                "description": param["description"]
                            }
                            for param in tool.parameters
                        },
                        "required": [
                            param["name"]
                            for param in tool.parameters
                            if param["required"]
                        ]
                    }
                }
            }
            schemas.append(schema)

        return schemas


# 使用
registry = ToolRegistry()

# 注册工具
registry.register(GetWeatherTool())
registry.register(SearchWebTool())
registry.register(CalculateTool())

# 列出所有工具
print("\n所有工具：")
for tool_name in registry.list_tools():
    print(f"- {tool_name}")

# 获取工具模式
schemas = registry.get_tool_schema()
print("\n工具模式：")
import json
print(json.dumps(schemas, indent=2, ensure_ascii=False))
```

### 6.1.4 LLM 工具调用

**结合 LLM 的工具调用**:

```python
from openai import OpenAI
import json

client = OpenAI(api_key="your-api-key")

# 获取工具模式
schemas = registry.get_tool_schema()

# 调用 LLM
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "system",
            "content": "你是一个智能助手，可以使用以下工具："
        },
        {
            "role": "system",
            "content": json.dumps(schemas, ensure_ascii=False)
        },
        {
            "role": "user",
            "content": "北京的天气怎么样？"
        }
    ],
    tools=schemas,
    tool_choice="auto"
)

# 检查是否需要调用工具
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        print(f"\n工具调用：{function_name}")
        print(f"参数：{arguments}")

        # 执行工具
        tool = registry.get_tool(function_name)
        result = tool.execute(**arguments)

        print(f"结果：{result}")
```

## 6.2 工具的调用机制

### 6.2.1 工具调用流程

```
┌─────────────────────────────────────────────────────────┐
│                    工具调用流程                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 用户输入                                             │
│     "北京的天气怎么样？"                                 │
│         ↓                                               │
│  2. LLM 决定是否需要调用工具                            │
│     - 需要调用 get_weather 工具                         │
│     - 参数：city="北京"                                  │
│         ↓                                               │
│  3. 执行工具                                            │
│     get_weather(city="北京")                            │
│         ↓                                               │
│  4. 返回工具结果                                         │
│     "北京今天天气晴，气温15-25摄氏度"                    │
│         ↓                                               │
│  5. LLM 生成最终答案                                     │
│     "北京今天天气晴，气温15-25摄氏度"                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 6.2.2 工具调用器

```python
class ToolCaller:
    """工具调用器"""

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def call_tool(self, tool_name: str, **kwargs) -> Any:
        """调用工具"""
        # 获取工具
        tool = self.registry.get_tool(tool_name)

        # 执行工具
        try:
            result = tool.execute(**kwargs)
            return result
        except Exception as e:
            return f"工具调用错误：{str(e)}"

    def call_tool_with_llm(self, user_message: str) -> str:
        """使用 LLM 决定是否调用工具"""
        # 获取工具模式
        schemas = self.registry.get_tool_schema()

        # 调用 LLM
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个智能助手，可以使用以下工具："
                },
                {
                    "role": "system",
                    "content": json.dumps(schemas, ensure_ascii=False)
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            tools=schemas,
            tool_choice="auto"
        )

        # 检查是否需要调用工具
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                # 执行工具
                result = self.call_tool(function_name, **arguments)

                # 返回工具结果
                return result

        # 如果不需要调用工具，返回 LLM 的答案
        return response.choices[0].message.content


# 使用
caller = ToolCaller(registry)

# 调用工具
result = caller.call_tool("get_weather", city="北京")
print(result)

# 使用 LLM 决定是否调用工具
answer = caller.call_tool_with_llm("北京的天气怎么样？")
print(answer)
```

### 6.2.3 工具调用链

```python
class ToolCaller:
    """工具调用器（支持工具调用链）"""

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def call_tool(self, tool_name: str, **kwargs) -> Any:
        """调用工具"""
        tool = self.registry.get_tool(tool_name)

        try:
            result = tool.execute(**kwargs)
            return result
        except Exception as e:
            return f"工具调用错误：{str(e)}"

    def call_tool_with_llm(self, user_message: str) -> str:
        """使用 LLM 决定是否调用工具"""
        # 获取工具模式
        schemas = self.registry.get_tool_schema()

        # 调用 LLM
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个智能助手，可以使用以下工具："
                },
                {
                    "role": "system",
                    "content": json.dumps(schemas, ensure_ascii=False)
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            tools=schemas,
            tool_choice="auto"
        )

        # 检查是否需要调用工具
        if response.choices[0].message.tool_calls:
            # 处理多个工具调用
            for tool_call in response.choices[0].message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                # 执行工具
                result = self.call_tool(function_name, **arguments)

                # 将工具结果添加到消息历史
                response.choices[0].message.tool_calls = []  # 清空工具调用
                response.choices[0].message.content = result

            # 返回工具结果
            return response.choices[0].message.content

        # 如果不需要调用工具，返回 LLM 的答案
        return response.choices[0].message.content


# 使用
caller = ToolCaller(registry)
answer = caller.call_tool_with_llm("搜索北京的天气")
print(answer)
```

## 6.3 工具的参数验证

### 6.3.1 参数验证器

```python
from typing import Dict, Any, List
import jsonschema

class ParameterValidator:
    """参数验证器"""

    @staticmethod
    def validate_parameters(tool: Tool, **kwargs) -> tuple[bool, str]:
        """验证工具参数"""
        # 获取工具参数模式
        parameters = tool.parameters

        # 检查必需参数
        required_params = [p["name"] for p in parameters if p["required"]]

        for param_name in required_params:
            if param_name not in kwargs:
                return False, f"缺少必需参数：{param_name}"

        # 检查参数类型
        for param_name, param_value in kwargs.items():
            for param in parameters:
                if param["name"] == param_name:
                    param_type = param["type"]

                    # 简单类型检查
                    if param_type == "str":
                        if not isinstance(param_value, str):
                            return False, f"参数 {param_name} 必须是字符串"

                    elif param_type == "int":
                        if not isinstance(param_value, int):
                            return False, f"参数 {param_name} 必须是整数"

                    elif param_type == "float":
                        if not isinstance(param_value, (int, float)):
                            return False, f"参数 {param_name} 必须是数字"

                    break

        return True, "参数验证通过"


# 使用
validator = ParameterValidator()

# 验证工具参数
tool = GetWeatherTool()
is_valid, message = validator.validate_parameters(tool, city="北京")

if is_valid:
    print("参数验证通过")
else:
    print(f"参数验证失败：{message}")
```

### 6.3.2 参数类型转换

```python
class ParameterConverter:
    """参数类型转换器"""

    @staticmethod
    def convert_parameters(tool: Tool, **kwargs) -> Dict[str, Any]:
        """转换工具参数类型"""
        converted = {}

        for param_name, param_value in kwargs.items():
            for param in tool.parameters:
                if param["name"] == param_name:
                    param_type = param["type"]

                    # 类型转换
                    if param_type == "int":
                        converted[param_name] = int(param_value)
                    elif param_type == "float":
                        converted[param_name] = float(param_value)
                    elif param_type == "str":
                        converted[param_name] = str(param_value)
                    else:
                        converted[param_name] = param_value

                    break

        return converted


# 使用
converter = ParameterConverter()

# 转换参数类型
tool = GetWeatherTool()
converted_params = converter.convert_parameters(
    tool,
    city=123  # 整数
)

print(f"转换后的参数：{converted_params}")
print(f"city 类型：{type(converted_params['city'])}")
```

## 6.4 工具的错误处理

### 6.4.1 工具异常处理

```python
class ToolException(Exception):
    """工具异常基类"""
    pass


class ToolNotFoundError(ToolException):
    """工具未找到异常"""
    pass


class InvalidParameterError(ToolException):
    """无效参数异常"""
    pass


class ToolExecutionError(ToolException):
    """工具执行异常"""
    pass


class ToolErrorHandler:
    """工具错误处理器"""

    @staticmethod
    def handle_error(error: ToolException) -> str:
        """处理工具错误"""
        error_messages = {
            ToolNotFoundError: "工具不存在，请检查工具名称",
            InvalidParameterError: "参数无效，请检查参数类型和值",
            ToolExecutionError: "工具执行失败，请稍后重试"
        }

        error_type = type(error)
        if error_type in error_messages:
            return error_messages[error_type]

        return f"未知错误：{str(error)}"


# 使用
class SafeTool(Tool):
    """安全的工具（带错误处理）"""

    def execute(self, **kwargs) -> Any:
        """执行工具"""
        try:
            # 参数验证
            validator = ParameterValidator()
            is_valid, message = validator.validate_parameters(self, **kwargs)

            if not is_valid:
                raise InvalidParameterError(message)

            # 类型转换
            converter = ParameterConverter()
            converted_params = converter.convert_parameters(self, **kwargs)

            # 执行工具
            result = self._execute_impl(**converted_params)
            return result

        except ToolException as e:
            error_handler = ToolErrorHandler()
            return error_handler.handle_error(e)
        except Exception as e:
            error_handler = ToolErrorHandler()
            return error_handler.handle_error(ToolExecutionError(str(e)))

    def _execute_impl(self, **kwargs) -> Any:
        """工具实现"""
        raise NotImplementedError


# 使用
safe_tool = SafeTool()
result = safe_tool.execute(city="北京")
print(result)
```

### 6.4.2 工具超时处理

```python
import signal
import time
from functools import wraps

def timeout(seconds):
    """工具超时装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            def timeout_handler(signum, frame):
                raise TimeoutError(f"工具执行超时：{seconds}秒")

            # 设置超时信号
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # 取消超时
                signal.alarm(0)

        return wrapper
    return decorator


# 使用
@timeout(5)  # 5秒超时
def slow_tool():
    """慢速工具"""
    time.sleep(10)
    return "执行完成"


try:
    result = slow_tool()
    print(result)
except TimeoutError as e:
    print(f"超时：{e}")
```

## 6.5 工具插件化

### 6.5.1 工具插件系统

```python
from abc import ABC, abstractmethod

class ToolPlugin(ABC):
    """工具插件基类"""

    @abstractmethod
    def get_tools(self) -> List[Tool]:
        """获取工具列表"""
        pass


class WeatherPlugin(ToolPlugin):
    """天气工具插件"""

    def get_tools(self) -> List[Tool]:
        return [GetWeatherTool()]


class SearchPlugin(ToolPlugin):
    """搜索工具插件"""

    def get_tools(self) -> List[Tool]:
        return [SearchWebTool()]


class CalculationPlugin(ToolPlugin):
    """计算工具插件"""

    def get_tools(self) -> List[Tool]:
        return [CalculateTool()]


class ToolPluginManager:
    """工具插件管理器"""

    def __init__(self):
        self.plugins = []

    def register_plugin(self, plugin: ToolPlugin):
        """注册插件"""
        self.plugins.append(plugin)
        print(f"已注册插件：{plugin.__class__.__name__}")

    def get_all_tools(self) -> List[Tool]:
        """获取所有工具"""
        all_tools = []

        for plugin in self.plugins:
            all_tools.extend(plugin.get_tools())

        return all_tools

    def get_tool_schema(self) -> List[Dict[str, Any]]:
        """获取所有工具模式"""
        all_tools = self.get_all_tools()

        schemas = []
        for tool in all_tools:
            schema = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            param["name"]: {
                                "type": param["type"],
                                "description": param["description"]
                            }
                            for param in tool.parameters
                        },
                        "required": [
                            param["name"]
                            for param in tool.parameters
                            if param["required"]
                        ]
                    }
                }
            }
            schemas.append(schema)

        return schemas


# 使用
plugin_manager = ToolPluginManager()

# 注册插件
plugin_manager.register_plugin(WeatherPlugin())
plugin_manager.register_plugin(SearchPlugin())
plugin_manager.register_plugin(CalculationPlugin())

# 获取所有工具
all_tools = plugin_manager.get_all_tools()
print(f"\n所有工具：{[tool.name for tool in all_tools]}")

# 获取工具模式
schemas = plugin_manager.get_tool_schema()
print(f"\n工具模式数量：{len(schemas)}")
```

## 6.6 本章总结

### 核心要点

1. **工具定义**: 继承 Tool 基类，实现 execute 方法
2. **工具注册**: 使用 ToolRegistry 管理工具
3. **工具调用**: 使用 ToolCaller 调用工具
4. **参数验证**: 使用 ParameterValidator 验证参数
5. **错误处理**: 使用 ToolErrorHandler 处理错误
6. **工具插件化**: 使用 ToolPluginManager 管理插件

### 实战技巧

- **工具定义**: 使用类型注解和文档字符串
- **工具注册**: 使用注册器统一管理工具
- **参数验证**: 检查必需参数和参数类型
- **错误处理**: 使用异常处理和超时控制
- **工具插件化**: 使用插件系统扩展工具

### 练习题

1. 实现一个简单的工具注册器
2. 实现一个工具调用器（支持 LLM 决定调用）
3. 实现一个参数验证器
4. 实现一个工具错误处理器

### 下章预告

第7章将介绍 **Loop 循环控制**，包括：
- 循环控制的概念
- 循环控制器的实现
- 循环控制与 Agent 的结合

---

**本章完**

**下一章**: [第7章：Loop 循环控制](./07-chapter7-loop-control.md)
