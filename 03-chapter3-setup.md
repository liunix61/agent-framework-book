# 第3章：环境搭建与工具链

## 本章目标

搭建完整的 Agent 开发环境，包括 Python、C++、数据库、测试框架等工具链。

## 前置知识

- **基础编程知识**: Python/C++（至少一种）
- **基础 Linux 命令**: cd、ls、mkdir、chmod、pip、conda
- **基础 Git 知识**: clone、commit、push、pull

## 3.1 Python 环境搭建

### 3.1.1 使用 venv（推荐）

**创建虚拟环境**:

```bash
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 确认激活成功
which python  # 应该显示 .venv/bin/python
```

**安装依赖**:

```bash
# 升级 pip
pip install --upgrade pip

# 创建 requirements.txt
pip freeze > requirements.txt

# 安装依赖
pip install -r requirements.txt
```

**requirements.txt 示例**:

```
openai>=1.0.0
anthropic>=0.18.0
ollama>=0.1.0
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.0.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
redis>=5.0.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
httpx>=0.25.0
```

**退出虚拟环境**:

```bash
deactivate
```

### 3.1.2 使用 conda（推荐用于科学计算）

**安装 Miniconda**:

```bash
# 下载 Miniconda 安装脚本
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# 运行安装脚本
bash Miniconda3-latest-Linux-x86_64.sh

# 初始化 conda
conda init bash

# 重新加载 bash
source ~/.bashrc
```

**创建环境**:

```bash
# 创建环境（Python 3.11）
conda create -n agent-env python=3.11

# 激活环境
conda activate agent-env

# 安装依赖
conda install openai anthropic fastapi uvicorn sqlalchemy psycopg2 redis pytest pytest-asyncio httpx -y
```

### 3.1.3 pip 镜像源配置（国内加速）

**临时使用**:

```bash
pip install package -i https://mirrors.aliyun.com/pypi/simple/
```

**永久配置**:

```bash
# 创建 pip 配置文件
mkdir -p ~/.pip
touch ~/.pip/pip.conf

# 配置阿里云镜像
cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
EOF
```

## 3.2 C++ 环境搭建

### 3.2.1 安装 GCC

**Ubuntu/Debian**:

```bash
sudo apt update
sudo apt install build-essential cmake git
```

**CentOS/RHEL**:

```bash
sudo yum groupinstall "Development Tools"
sudo yum install cmake git
```

**验证安装**:

```bash
g++ --version
cmake --version
```

### 3.2.2 安装 CMake

**Ubuntu/Debian**:

```bash
sudo apt install cmake
```

**CentOS/RHEL**:

```bash
sudo yum install cmake
```

**使用 Conda 安装**:

```bash
conda install cmake -y
```

### 3.2.3 安装依赖库

**curl**:

```bash
sudo apt install libcurl4-openssl-dev
```

**nlohmann/json**:

```bash
sudo apt install nlohmann-json3-dev
```

**或使用 venv**:

```bash
python3 -m venv .venv-cpp
source .venv-cpp/bin/activate
pip install nlohmann_json
```

### 3.2.4 VSCode 配置

**安装 C++ 扩展**:

- C/C++ (Microsoft)
- C/C++ Extension Pack

**创建 .vscode/settings.json**:

```json
{
    "C_Cpp.default.compilerPath": "/usr/bin/g++",
    "C_Cpp.default.configurationProvider": "ms-vscode.cmake-tools",
    "cmake.configureOnOpen": true,
    "editor.formatOnSave": true,
    "C_Cpp.clang_format_style": "Google"
}
```

**创建 .vscode/c_cpp_properties.json**:

```json
{
    "configurations": [
        {
            "name": "Linux",
            "includePath": [
                "${workspaceFolder}/**",
                "/usr/include"
            ],
            "defines": ["_GNU_SOURCE"],
            "compilerPath": "/usr/bin/g++",
            "cStandard": "c17",
            "cppStandard": "c++20",
            "intelliSenseMode": "linux-gcc-x64"
        }
    ],
    "version": 4
}
```

## 3.3 数据库配置

### 3.3.1 PostgreSQL 安装

**Ubuntu/Debian**:

```bash
# 安装 PostgreSQL
sudo apt install postgresql postgresql-contrib

# 启动 PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建数据库
sudo -u postgres psql
CREATE DATABASE agent_admin;
CREATE USER agent_admin WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE agent_admin TO agent_admin;
\q
```

**CentOS/RHEL**:

```bash
sudo yum install postgresql-server postgresql-contrib
sudo /usr/bin/postgresql-setup --initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql

sudo -u postgres psql
CREATE DATABASE agent_admin;
CREATE USER agent_admin WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE agent_admin TO agent_admin;
\q
```

### 3.3.2 Redis 安装

**Ubuntu/Debian**:

```bash
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**CentOS/RHEL**:

```bash
sudo yum install redis
sudo systemctl start redis
sudo systemctl enable redis
```

**验证安装**:

```bash
redis-cli ping
# 应该返回：PONG
```

### 3.3.3 连接测试

**Python 测试**:

```python
import psycopg2

# 连接数据库
conn = psycopg2.connect(
    host="localhost",
    database="agent_admin",
    user="agent_admin",
    password="your_password"
)

cursor = conn.cursor()
cursor.execute("SELECT version();")
print(cursor.fetchone())

cursor.close()
conn.close()
```

**C++ 测试**:

```cpp
#include <libpq-fe.h>
#include <iostream>

int main() {
    PGconn* conn = PQconnectdb("host=localhost dbname=agent_admin user=agent_admin password=your_password");

    if (PQstatus(conn) != CONNECTION_OK) {
        std::cout << "连接失败: " << PQerrorMessage(conn) << std::endl;
        PQfinish(conn);
        return 1;
    }

    PGresult* res = PQexec(conn, "SELECT version();");
    if (PQresultStatus(res) == PGRES_TUPLES_OK) {
        std::cout << "PostgreSQL版本: " << PQgetvalue(res, 0, 0) << std::endl;
    }

    PQclear(res);
    PQfinish(conn);
    return 0;
}
```

## 3.4 测试框架配置

### 3.4.1 pytest 配置

**安装 pytest**:

```bash
pip install pytest pytest-asyncio pytest-cov
```

**创建 pytest.ini**:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --tb=short
    --cov=.
    --cov-report=html
    --cov-report=term-missing
```

**创建 .pytest.ini**:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts =
    -v
    --tb=short
    --cov=src
    --cov-report=html
    --cov-report=term-missing
```

### 3.4.2 C++ 测试（Google Test）

**安装 Google Test**:

```bash
sudo apt install libgtest-dev
cd /usr/src/gtest
sudo cmake CMakeLists.txt
sudo make
sudo cp *.a /usr/lib/
sudo cp -r include/* /usr/include/
```

**创建 CMakeLists.txt**:

```cmake
cmake_minimum_required(VERSION 3.10)
project(MyTests)

set(CMAKE_CXX_STANDARD 17)

# 查找 Google Test
find_package(GTest REQUIRED)

# 添加可执行文件
add_executable(test_agent agent_test.cpp)
target_link_libraries(test_agent GTest::gtest_main)
```

**创建 agent_test.cpp**:

```cpp
#include <gtest/gtest.h>
#include "agent.h"

TEST(AgentTest, Constructor) {
    Agent agent("test-api-key", "gpt-4");
    EXPECT_TRUE(true);
}

TEST(AgentTest, AddMessage) {
    Agent agent("test-api-key", "gpt-4");
    agent.add_message("user", "Hello");
    EXPECT_EQ(agent.messages.size(), 2);
}

TEST(AgentTest, ClearHistory) {
    Agent agent("test-api-key", "gpt-4");
    agent.add_message("user", "Hello");
    agent.clear_history();
    EXPECT_EQ(agent.messages.size(), 1);
}
```

**编译运行**:

```bash
mkdir build && cd build
cmake ..
make
./test_agent
```

## 3.5 Agent 开发工具

### 3.5.1 IDE 配置

**VSCode**:

- **Python**: Python、Pylance、Jupyter
- **C++**: C/C++、CMake Tools、C/C++ Extension Pack
- **调试**: Python Debugger、C++ Debugger

**PyCharm**:

- **Python**: Python、Django、Flask
- **调试**: Python Debugger、Remote Debug

**CLion**:

- **C++**: CMake、CLion 内置调试器
- **性能分析**: Profiler

### 3.5.2 调试工具

**Python 调试**:

```python
import pdb

# 断点调试
pdb.set_trace()

# 或使用 ipdb
import ipdb; ipdb.set_trace()
```

**C++ 调试**:

```bash
g++ -g -O0 -std=c++20 main.cpp -o main
gdb ./main
```

### 3.5.3 性能分析工具

**Python 性能分析**:

```bash
python -m cProfile -s time main.py
```

**C++ 性能分析**:

```bash
valgrind --tool=callgrind ./main
kcachegrind callgrind.out.*
```

**火焰图**:

```bash
pip install py-spy
py-spy top --pid $(pgrep main)
```

## 3.6 项目结构

### 3.6.1 Python 项目结构

```
my-agent-project/
├── .venv/                      # 虚拟环境
├── src/                        # 源代码
│   ├── agent.py
│   ├── tools.py
│   └── main.py
├── tests/                      # 测试代码
│   ├── test_agent.py
│   └── test_tools.py
├── requirements.txt            # Python 依赖
├── pytest.ini                  # Pytest 配置
├── .gitignore
├── README.md
└── .env                        # 环境变量
```

### 3.6.2 C++ 项目结构

```
my-agent-project/
├── build/                      # 编译输出
├── src/                        # 源代码
│   ├── agent.h
│   ├── agent.cpp
│   ├── tools.h
│   ├── tools.cpp
│   └── main.cpp
├── tests/                      # 测试代码
│   ├── test_agent.cpp
│   └── CMakeLists.txt
├── CMakeLists.txt              # CMake 配置
├── .gitignore
├── README.md
└── .env                        # 环境变量
```

### 3.6.3 环境变量配置

**.env 文件**:

```
# OpenAI API
OPENAI_API_KEY=your-api-key

# Claude API
ANTHROPIC_API_KEY=your-api-key

# 数据库
DB_HOST=localhost
DB_PORT=5432
DB_NAME=agent_admin
DB_USER=agent_admin
DB_PASSWORD=your_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# 其他配置
DEBUG=True
LOG_LEVEL=INFO
```

**Python 读取环境变量**:

```python
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
```

**C++ 读取环境变量**:

```cpp
#include <cstdlib>
#include <string>

std::string get_env_var(const std::string& key) {
    const char* value = std::getenv(key.c_str());
    return value ? value : "";
}

std::string api_key = get_env_var("OPENAI_API_KEY");
```

## 3.7 本章总结

### 核心要点

1. **Python 环境搭建**: venv、conda、pip 镜像源
2. **C++ 环境搭建**: GCC、CMake、依赖库、VSCode
3. **数据库配置**: PostgreSQL、Redis
4. **测试框架**: pytest、Google Test
5. **开发工具**: IDE、调试工具、性能分析工具
6. **项目结构**: Python 和 C++ 项目结构
7. **环境变量**: .env 文件配置

### 检查清单

- [ ] Python 虚拟环境已创建
- [ ] pip 依赖已安装
- [ ] C++ 编译器已安装
- [ ] CMake 已安装
- [ ] PostgreSQL 已安装并运行
- [ ] Redis 已安装并运行
- [ ] pytest 已安装并配置
- [ ] Google Test 已安装
- [ ] VSCode C++ 扩展已安装
- [ ] 项目结构已创建
- [ ] .env 文件已创建

### 练习题

1. 使用 conda 创建一个 Python 环境，安装 OpenAI 和 Anthropic 库
2. 使用 CMake 编译一个简单的 C++ 项目
3. 配置 pytest 并运行一个简单的测试
4. 使用环境变量管理 API Key

### 下章预告

第4章将介绍 **Prompt Engineering 进阶**，包括：
- Chain-of-Thought（CoT）深入解析
- ReAct 框架详解
- Self-Consistency
- Tool Use 与 Function Calling
- Prompt 优化实战案例

---

**本章完**

**下一章**: [第4章：Prompt Engineering 进阶](./04-chapter4-prompt-engineering.md)
