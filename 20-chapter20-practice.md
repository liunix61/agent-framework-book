# 第20章：Agent 开发实战

## 本章目标

通过实战项目，掌握 Agent 开发的完整流程。

## 前置知识

- **基础 Agent**: Harness、Loop、Graph
- **基础 开发**: Python、FastAPI、数据库
- **基础 项目**: 项目结构、代码组织

## 20.1 实战项目1：智能写作助手

### 20.1.1 项目需求

**需求描述**:
开发一个智能写作助手 Agent，能够帮助用户完成以下任务：
1. 规划文章结构
2. 撰写文章内容
3. 审阅文章
4. 编辑文章
5. 生成最终文章

**技术要求**:
- 使用 Python 开发
- 使用 FastAPI 框架
- 使用 PostgreSQL 存储数据
- 使用 Redis 缓存
- 使用 LLM API（OpenAI）

### 20.1.2 项目架构

**项目架构**:

```
┌─────────────────────────────────────────────────────────┐
│                    智能写作助手项目                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  前端层                            │  │
│  │  - Web 前端（Vue3）                               │  │
│  │  - API 网关（Nginx）                              │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  后端层                            │  │
│  │  - FastAPI 应用                                    │  │
│  │  - Agent 服务                                      │  │
│  │  - 工具服务                                        │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  数据层                            │  │
│  │  - PostgreSQL（数据库）                            │  │
│  │  - Redis（缓存）                                    │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 20.1.3 项目结构

**项目结构**:

```
writing-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 应用入口
│   │   ├── config.py            # 配置文件
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── planner.py       # 规划 Agent
│   │   │   ├── writer.py        # 写作 Agent
│   │   │   ├── reviewer.py      # 审阅 Agent
│   │   │   └── editor.py        # 编辑 Agent
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── llm_tool.py      # LLM 工具
│   │   │   └── database_tool.py # 数据库工具
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py       # Pydantic 模型
│   │   └── database.py          # 数据库连接
│   ├── tests/
│   │   ├── test_agents/
│   │   ├── test_tools/
│   │   └── test_api.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api/
│   │   └── main.js
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

### 20.1.4 后端开发

**1. 配置文件**

```python
# backend/app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """配置类"""

    # LLM API
    openai_api_key: str
    openai_model: str = "gpt-4"

    # 数据库
    database_url: str = "postgresql://user:password@localhost:5432/writing_assistant"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # 应用
    app_name: str = "智能写作助手"
    app_version: str = "1.0.0"
    debug: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
```

**2. 数据库模型**

```python
# backend/app/models/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional

class ArticleStructure(BaseModel):
    """文章结构"""
    sections: List[str] = Field(..., description="文章章节")

class ArticleContent(BaseModel):
    """文章内容"""
    title: str
    content: str
    sections: List[str] = Field(..., description="文章章节")

class ArticleReview(BaseModel):
    """文章审阅"""
    review: str
    suggestions: List[str] = Field(default=[], description="修改建议")

class ArticleEdit(BaseModel):
    """文章编辑"""
    edited_content: str
    changes: List[str] = Field(default=[], description="修改内容")

class Article(BaseModel):
    """文章"""
    id: Optional[str] = None
    title: str
    content: str
    status: str = "draft"  # draft, reviewed, edited, completed
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# 创建数据库引擎
engine = create_engine(settings.database_url)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


# 创建数据库表
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

class ArticleDB(Base):
    """文章数据库模型"""
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    status = Column(String, default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# 创建表
Base.metadata.create_all(bind=engine)
```

**3. Agent 实现**

```python
# backend/app/agents/planner.py
from typing import Dict, Any
from app.models.schemas import ArticleStructure
import time

class PlannerAgent:
    """规划 Agent"""

    def __init__(self, llm_tool):
        """初始化规划 Agent"""
        self.llm_tool = llm_tool

    def plan(self, topic: str) -> ArticleStructure:
        """
        规划文章结构

        Args:
            topic: 主题

        Returns:
            文章结构
        """
        prompt = f"""
        请为以下主题规划文章结构：
        主题：{topic}

        文章结构应该包括：
        1. 引言
        2. 正文（3-5个章节）
        3. 结论

        请返回 JSON 格式：
        {{
            "sections": ["章节1", "章节2", "章节3", "章节4", "章节5", "结论"]
        }}
        """

        response = self.llm_tool.call(prompt)
        structure = self.llm_tool.parse_json(response)

        return ArticleStructure(**structure)


# backend/app/agents/writer.py
from typing import Dict, Any
from app.models.schemas import ArticleContent

class WriterAgent:
    """写作 Agent"""

    def __init__(self, llm_tool):
        """初始化写作 Agent"""
        self.llm_tool = llm_tool

    def write(self, topic: str, structure: ArticleStructure) -> ArticleContent:
        """
        撰写文章内容

        Args:
            topic: 主题
            structure: 文章结构

        Returns:
            文章内容
        """
        sections = "\n".join([
            f"{i+1}. {section}"
            for i, section in enumerate(structure.sections)
        ])

        prompt = f"""
        请为以下主题撰写文章：
        主题：{topic}

        文章结构：
        {sections}

        请撰写完整的文章，包括引言、正文和结论。
        """

        response = self.llm_tool.call(prompt)

        return ArticleContent(
            title=topic,
            content=response,
            sections=structure.sections
        )


# backend/app/agents/reviewer.py
from typing import Dict, Any
from app.models.schemas import ArticleReview

class ReviewerAgent:
    """审阅 Agent"""

    def __init__(self, llm_tool):
        """初始化审阅 Agent"""
        self.llm_tool = llm_tool

    def review(self, content: str) -> ArticleReview:
        """
        审阅文章

        Args:
            content: 文章内容

        Returns:
            文章审阅
        """
        prompt = f"""
        请审阅以下文章：

        {content}

        请提供：
        1. 整体评价
        2. 修改建议（3-5条）
        """

        response = self.llm_tool.call(prompt)

        return ArticleReview(
            review=response
        )


# backend/app/agents/editor.py
from typing import Dict, Any
from app.models.schemas import ArticleEdit

class EditorAgent:
    """编辑 Agent"""

    def __init__(self, llm_tool):
        """初始化编辑 Agent"""
        self.llm_tool = llm_tool

    def edit(self, content: str, review: ArticleReview) -> ArticleEdit:
        """
        编辑文章

        Args:
            content: 文章内容
            review: 文章审阅

        Returns:
            文章编辑
        """
        prompt = f"""
        请根据以下审阅意见编辑文章：

        审阅意见：
        {review.review}

        原文：
        {content}

        请根据审阅意见修改文章。
        """

        response = self.llm_tool.call(prompt)

        return ArticleEdit(
            edited_content=response
        )
```

**4. LLM 工具**

```python
# backend/app/tools/llm_tool.py
import openai
from typing import Dict, Any

class LLMTool:
    """LLM 工具"""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        """初始化 LLM 工具"""
        openai.api_key = api_key
        self.model = model

    def call(self, prompt: str) -> str:
        """
        调用 LLM

        Args:
            prompt: 提示词

        Returns:
            LLM 响应
        """
        response = openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个专业的写作助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4096
        )

        return response.choices[0].message.content

    def parse_json(self, response: str) -> Dict[str, Any]:
        """
        解析 JSON

        Args:
            response: LLM 响应

        Returns:
            JSON 数据
        """
        import json
        return json.loads(response)
```

**5. FastAPI 应用**

```python
# backend/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.schemas import Article, ArticleCreate
from app.agents.planner import PlannerAgent
from app.agents.writer import WriterAgent
from app.agents.reviewer import ReviewerAgent
from app.agents.editor import EditorAgent
from app.tools.llm_tool import LLMTool
from app.config import settings

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建 LLM 工具
llm_tool = LLMTool(
    api_key=settings.openai_api_key,
    model=settings.openai_model
)

# 创建 Agent
planner = PlannerAgent(llm_tool)
writer = WriterAgent(llm_tool)
reviewer = ReviewerAgent(llm_tool)
editor = EditorAgent(llm_tool)


# 依赖项：获取数据库会话
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# API 端点
@app.post("/articles/generate")
async def generate_article(
    topic: str,
    db: Session = Depends(get_db)
):
    """
    生成文章

    Args:
        topic: 主题
        db: 数据库会话

    Returns:
        文章
    """
    try:
        # 1. 规划
        structure = planner.plan(topic)

        # 2. 撰写
        content = writer.write(topic, structure)

        # 3. 审阅
        review = reviewer.review(content.content)

        # 4. 编辑
        edited = editor.edit(content.content, review)

        # 5. 保存到数据库
        article_db = ArticleDB(
            title=content.title,
            content=edited.edited_content,
            status="completed"
        )
        db.add(article_db)
        db.commit()
        db.refresh(article_db)

        # 返回文章
        return {
            "id": article_db.id,
            "title": article_db.title,
            "content": article_db.content,
            "status": article_db.status,
            "created_at": article_db.created_at,
            "updated_at": article_db.updated_at
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/articles/{article_id}")
async def get_article(article_id: int, db: Session = Depends(get_db)):
    """
    获取文章

    Args:
        article_id: 文章 ID
        db: 数据库会话

    Returns:
        文章
    """
    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).first()

    if article is None:
        raise HTTPException(status_code=404, detail="文章不存在")

    return {
        "id": article.id,
        "title": article.title,
        "content": article.content,
        "status": article.status,
        "created_at": article.created_at,
        "updated_at": article.updated_at
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**6. requirements.txt**

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
openai==1.3.7
python-dotenv==1.0.0
```

**7. Dockerfile**

```dockerfile
# 使用 Python 3.11 基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**8. docker-compose.yml**

```yaml
version: '3.8'

services:
  # PostgreSQL 数据库
  postgres:
    image: postgres:16-alpine
    container_name: writing_assistant_postgres
    environment:
      POSTGRES_DB: writing_assistant
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Redis 缓存
  redis:
    image: redis:7-alpine
    container_name: writing_assistant_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # 后端服务
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: writing_assistant_backend
    environment:
      DATABASE_URL: postgresql://user:password@postgres:5432/writing_assistant
      REDIS_URL: redis://redis:6379/0
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app

  # 前端服务
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: writing_assistant_frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
```

### 20.1.5 前端开发

**1. Vue3 前端**

```javascript
// frontend/src/api/article.js
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

export const generateArticle = async (topic) => {
  const response = await axios.post(`${API_BASE_URL}/articles/generate`, null, {
    params: { topic }
  })
  return response.data
}

export const getArticle = async (articleId) => {
  const response = await axios.get(`${API_BASE_URL}/articles/${articleId}`)
  return response.data
}
```

```javascript
// frontend/src/pages/GenerateArticle.vue
<template>
  <div class="generate-article">
    <h1>智能写作助手</h1>

    <div class="form">
      <input
        v-model="topic"
        placeholder="输入文章主题"
        @keyup.enter="generate"
      />
      <button @click="generate" :disabled="loading">
        {{ loading ? '生成中...' : '生成文章' }}
      </button>
    </div>

    <div v-if="article" class="article">
      <h2>{{ article.title }}</h2>
      <div class="content">{{ article.content }}</div>
      <div class="status">{{ article.status }}</div>
    </div>
  </div>
</template>

<script>
import { generateArticle } from '../api/article'

export default {
  data() {
    return {
      topic: '',
      article: null,
      loading: false
    }
  },
  methods: {
    async generate() {
      this.loading = true
      try {
        this.article = await generateArticle(this.topic)
      } catch (error) {
        console.error('生成文章失败:', error)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
```

### 20.1.6 部署与测试

**1. 启动项目**

```bash
# 启动 Docker Compose
docker-compose up -d

# 查看日志
docker-compose logs -f
```

**2. 测试 API**

```bash
# 生成文章
curl -X POST "http://localhost:8000/api/articles/generate?topic=AI Agent的未来" \
  -H "Content-Type: application/json"

# 获取文章
curl "http://localhost:8000/api/articles/1"
```

**3. 测试前端**

```bash
# 访问前端
http://localhost:3000
```

## 20.2 实战项目2：量化交易 Agent

### 20.2.1 项目需求

**需求描述**:
开发一个量化交易 Agent，能够：
1. 生成交易策略
2. 检查风险
3. 执行交易
4. 监控交易

**技术要求**:
- 使用 Python 开发
- 使用 FastAPI 框架
- 使用 PostgreSQL 存储数据
- 使用 Redis 缓存
- 使用 LLM API（OpenAI）
- 使用 pandas 处理数据

### 20.2.2 项目架构

**项目架构**:

```
┌─────────────────────────────────────────────────────────┐
│                    量化交易 Agent 项目                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  数据层                            │  │
│  │  - 市场数据（价格、成交量）                         │  │
│  │  - K线数据                                          │  │
│  │  - 财报数据                                        │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  Agent 层                            │  │
│  │  - 策略生成器（Strategy Agent）                     │  │
│  │  - 风控 Agent（Risk Control Agent）                 │  │
│  │  - 执行 Agent（Execution Agent）                    │  │
│  │  - 监控 Agent（Monitoring Agent）                   │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  工具层                            │  │
│  │  - 数据获取工具                                      │  │
│  │  - 策略回测工具                                      │  │
│  │  - 交易执行工具                                      │  │
│  │  - 风险管理工具                                      │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 20.2.3 Agent 实现

**1. 策略 Agent**

```python
# backend/app/agents/strategy_agent.py
import pandas as pd
import numpy as np
from typing import Dict, Any

class StrategyAgent:
    """策略 Agent"""

    def __init__(self, llm_tool):
        """初始化策略 Agent"""
        self.llm_tool = llm_tool

    def generate_strategy(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        生成交易策略

        Args:
            data: 市场数据

        Returns:
            策略结果
        """
        # 计算 RSI 指标
        rsi = self._calculate_rsi(data['close'], 14)

        # 生成交易信号
        signals = []
        for i in range(len(rsi)):
            if rsi[i] < 30:
                signals.append("buy")
            elif rsi[i] > 70:
                signals.append("sell")
            else:
                signals.append("hold")

        return {
            "signals": signals,
            "last_signal": signals[-1],
            "status": "completed"
        }

    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """计算 RSI 指标"""
        deltas = prices.diff()
        seed = deltas[:period + 1].mean()
        up = deltas[:period + 1].copy()
        down = deltas[:period + 1].copy()
        up[up < 0] = 0
        down[down > 0] = 0

        up_series = up.rolling(window=period).mean()
        down_series = down.rolling(window=period).mean()

        rs = up_series / down_series
        rsi = 100 - (100 / (1 + rs))

        return rsi
```

**2. 风控 Agent**

```python
# backend/app/agents/risk_agent.py
import pandas as pd
import numpy as np
from typing import Dict, Any

class RiskAgent:
    """风控 Agent"""

    def __init__(self, llm_tool):
        """初始化风控 Agent"""
        self.llm_tool = llm_tool

    def check_risk(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        检查风险

        Args:
            data: 市场数据

        Returns:
            风险结果
        """
        # 计算最大回撤
        max_drawdown = self._calculate_max_drawdown(data['close'])

        # 检查是否超过风险阈值
        if max_drawdown > 0.1:
            return {
                "risk_level": "high",
                "max_drawdown": max_drawdown,
                "status": "completed"
            }

        return {
            "risk_level": "low",
            "max_drawdown": max_drawdown,
            "status": "completed"
        }

    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """计算最大回撤"""
        cummax = prices.cummax()
        drawdown = (prices - cummax) / cummax
        max_drawdown = drawdown.min()

        return max_drawdown
```

**3. 执行 Agent**

```python
# backend/app/agents/execution_agent.py
from typing import Dict, Any

class ExecutionAgent:
    """执行 Agent"""

    def __init__(self, llm_tool):
        """初始化执行 Agent"""
        self.llm_tool = llm_tool

    def execute_trade(self, signal: str, price: float) -> Dict[str, Any]:
        """
        执行交易

        Args:
            signal: 交易信号（buy/sell/hold）
            price: 价格

        Returns:
            执行结果
        """
        if signal == "buy":
            return {
                "action": "buy",
                "price": price,
                "status": "completed"
            }
        elif signal == "sell":
            return {
                "action": "sell",
                "price": price,
                "status": "completed"
            }

        return {
            "action": "hold",
            "price": price,
            "status": "completed"
        }
```

**4. 监控 Agent**

```python
# backend/app/agents/monitoring_agent.py
import pandas as pd
from typing import Dict, Any

class MonitoringAgent:
    """监控 Agent"""

    def __init__(self, llm_tool):
        """初始化监控 Agent"""
        self.llm_tool = llm_tool

    def monitor_trades(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        监控交易

        Args:
            data: 市场数据

        Returns:
            监控结果
        """
        # 计算收益率
        if len(data) >= 2:
            return_rate = (data['close'].iloc[-1] - data['close'].iloc[-2]) / data['close'].iloc[-2]
        else:
            return_rate = 0.0

        return {
            "return_rate": return_rate,
            "status": "completed"
        }
```

**5. FastAPI 应用**

```python
# backend/app/main.py
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.agents.strategy_agent import StrategyAgent
from app.agents.risk_agent import RiskAgent
from app.agents.execution_agent import ExecutionAgent
from app.agants.monitoring_agent import MonitoringAgent
from app.tools.llm_tool import LLMTool
from app.config import settings

# 创建 FastAPI 应用
app = FastAPI(
    title="量化交易 Agent",
    version="1.0.0",
    debug=settings.debug
)

# 创建 LLM 工具
llm_tool = LLMTool(
    api_key=settings.openai_api_key,
    model=settings.openai_model
)

# 创建 Agent
strategy_agent = StrategyAgent(llm_tool)
risk_agent = RiskAgent(llm_tool)
execution_agent = ExecutionAgent(llm_tool)
monitoring_agent = MonitoringAgent(llm_tool)


# 依赖项：获取数据库会话
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# API 端点
@app.post("/trades/execute")
async def execute_trade(
    data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    执行交易

    Args:
        data: 市场数据
        db: 数据库会话

    Returns:
    """
    try:
        # 1. 生成策略
        strategy_result = strategy_agent.generate_strategy(data)

        # 2. 检查风险
        risk_result = risk_agent.check_risk(data)

        # 3. 执行交易
        execution_result = execution_agent.execute_trade(
            strategy_result["last_signal"],
            data["close"][-1]
        )

        # 4. 监控交易
        monitoring_result = monitoring_agent.monitor_trades(data)

        # 返回结果
        return {
            "strategy": strategy_result,
            "risk": risk_result,
            "execution": execution_result,
            "monitoring": monitoring_result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

## 20.3 本章总结

### 核心要点

1. **实战项目1：智能写作助手**
   - 项目架构、项目结构
   - 后端开发（配置、模型、Agent、API）
   - 前端开发（Vue3）
   - 部署与测试

2. **实战项目2：量化交易 Agent**
   - 项目架构、Agent 实现
   - 策略 Agent、风控 Agent、执行 Agent、监控 Agent
   - FastAPI 应用

### 实战技巧

- **项目架构**: 清晰的分层架构（前端层、后端层、数据层）
- **Agent 实现**: 每个 Agent 负责单一职责
- **API 设计**: RESTful API 设计
- **部署**: Docker Compose 部署
- **测试**: API 测试、前端测试

### 练习题

1. 完成智能写作助手项目的开发
2. 完成量化交易 Agent 项目的开发
3. 为项目添加单元测试
4. 为项目添加集成测试

### 下章预告

第21章将介绍 **Agent 性能优化实战**，包括：
- 性能分析实战
- 缓存优化实战
- 异步优化实战
- 并发优化实战

---

**本章完**

**下一章**: [第21章：Agent 性能优化实战](./21-chapter21-performance-practice.md)
