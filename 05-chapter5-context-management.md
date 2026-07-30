# 第5章：Context 管理

## 本章目标

掌握 Agent 的记忆系统，包括短期记忆、长期记忆、向量数据库、检索增强生成（RAG）等。

## 前置知识

- **基础 Python/C++**: 函数、类、异常处理
- **基础数据库**: PostgreSQL、Redis
- **基础 AI**: LLM API、向量概念

## 5.1 短期记忆 vs 长期记忆

### 5.1.1 记忆系统架构

**Agent 记忆系统**:

```
┌─────────────────────────────────────────────────────────┐
│                    Agent 记忆系统                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 短期记忆      │  │ 长期记忆      │  │ 知识库        │  │
│  │ (短期上下文)  │  │ (长期上下文)  │  │ (RAG)        │  │
│  │              │  │              │  │              │  │
│  │ - 当前对话    │  │ - 对话历史    │  │ - 文档        │  │
│  │ - 当前任务    │  │ - 用户偏好    │  │ - 知识图谱    │  │
│  │ - 当前状态    │  │ - 用户信息    │  │ - 实体知识    │  │
│  │              │  │ - 常见问题    │  │ - 业务规则    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │            记忆检索与更新模块                      │  │
│  │  - 相似度检索                                      │  │
│  │  - 向量搜索                                        │  │
│  │  - 记忆压缩                                        │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 5.1.2 短期记忆（Short-term Memory）

**特点**:
- **生命周期短**: 对话结束即销毁
- **容量小**: 限制 token 数量（通常 4K-16K）
- **速度快**: 直接在内存中访问
- **上下文相关**: 仅包含当前对话的上下文

**实现方式**:

```python
class ShortTermMemory:
    def __init__(self, max_tokens=4096):
        self.max_tokens = max_tokens
        self.messages = []

    def add_message(self, role, content):
        """添加消息到短期记忆"""
        self.messages.append({"role": role, "content": content})

    def get_context(self):
        """获取上下文（限制 token 数量）"""
        # 计算当前 token 数量
        current_tokens = sum(len(m["content"]) for m in self.messages)

        # 如果超过限制，移除最早的消息
        while current_tokens > self.max_tokens and len(self.messages) > 0:
            removed = self.messages.pop(0)
            current_tokens -= len(removed["content"])

        return self.messages

    def clear(self):
        """清除短期记忆"""
        self.messages = []

# 使用
short_term = ShortTermMemory(max_tokens=4096)

# 添加消息
short_term.add_message("system", "你是一个写作助手")
short_term.add_message("user", "请写一篇文章")
short_term.add_message("assistant", "好的，这是一篇文章：\n\n文章内容...")

# 获取上下文
context = short_term.get_context()
print(f"当前上下文包含 {len(context)} 条消息")
```

### 5.1.3 长期记忆（Long-term Memory）

**特点**:
- **生命周期长**: 对话结束后仍然保留
- **容量大**: 可以存储大量数据
- **速度慢**: 需要从数据库中检索
- **持久化**: 存储在数据库中

**实现方式**:

```python
import sqlite3

class LongTermMemory:
    def __init__(self, db_path="memory.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        # 创建记忆表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                relevance_score REAL
            )
        """)

        self.conn.commit()

    def save_memory(self, role, content, relevance_score=0.0):
        """保存记忆"""
        self.cursor.execute(
            "INSERT INTO memories (role, content, relevance_score) VALUES (?, ?, ?)",
            (role, content, relevance_score)
        )
        self.conn.commit()

    def retrieve_memories(self, query, limit=10):
        """检索记忆"""
        # 简单的关键词匹配（实际应用中应该使用向量搜索）
        self.cursor.execute(
            "SELECT * FROM memories WHERE content LIKE ? LIMIT ?",
            (f"%{query}%", limit)
        )

        memories = self.cursor.fetchall()
        return memories

    def clear_old_memories(self, days=30):
        """清除旧记忆"""
        self.cursor.execute(
            "DELETE FROM memories WHERE created_at < datetime('now', '-' || ? || ' days')",
            (days,)
        )
        self.conn.commit()

# 使用
long_term = LongTermMemory()

# 保存记忆
long_term.save_memory("user", "我喜欢写技术文章", relevance_score=0.9)
long_term.save_memory("assistant", "好的，我会为你写技术文章", relevance_score=0.8)

# 检索记忆
memories = long_term.retrieve_memories("技术文章")
for memory in memories:
    print(f"[{memory[1]}] {memory[2]}")
```

### 5.1.4 记忆系统对比

| 维度 | 短期记忆 | 长期记忆 |
|------|---------|---------|
| **生命周期** | 短（对话结束即销毁） | 长（永久保留） |
| **容量** | 小（4K-16K tokens） | 大（GB级别） |
| **速度** | 快（内存访问） | 慢（数据库检索） |
| **持久化** | 不持久 | 持久化 |
| **用途** | 当前对话上下文 | 历史对话、用户偏好 |
| **实现方式** | 列表/队列 | 数据库 |

## 5.2 向量数据库

### 5.2.1 什么是向量数据库

**向量数据库** 是一种专门存储向量并支持向量相似度检索的数据库。

**核心功能**:
- **向量存储**: 存储文本、图像、音频等数据的向量表示
- **向量搜索**: 基于余弦相似度、欧氏距离等计算相似度
- **向量索引**: 加速向量搜索（HNSW、IVF等）

**常用向量数据库**:
- **Chroma**: 轻量级、易用
- **Milvus**: 高性能、可扩展
- **PGVector**: PostgreSQL 扩展
- **Weaviate**: GraphQL API、内置向量索引

### 5.2.2 Chroma 使用

**安装**:

```bash
pip install chromadb
```

**基本用法**:

```python
import chromadb
from chromadb.config import Settings

# 初始化客户端
client = chromadb.Client(Settings())

# 创建集合
collection = client.create_collection(name="documents")

# 添加文档
documents = [
    "AI Agent 是一个能够自主感知、决策、行动的智能体",
    "Prompt Engineering 是让 LLM 生成更好输出的技术",
    "ReAct 是一种让 Agent 推理并调用工具的框架",
    "Chain-of-Thought 是让模型逐步推理的 Prompt 技术"
]

collection.add(
    documents=documents,
    ids=[f"doc_{i}" for i in range(len(documents))]
)

# 搜索
results = collection.query(
    query_texts=["Agent 的定义"],
    n_results=2
)

for i, result in enumerate(results['documents'][0]):
    print(f"结果 {i+1}: {result}")
```

**带元数据**:

```python
# 添加文档（带元数据）
collection.add(
    documents=[
        "AI Agent 是一个能够自主感知、决策、行动的智能体",
        "Prompt Engineering 是让 LLM 生成更好输出的技术"
    ],
    metadatas=[
        {"category": "概念", "source": "book"},
        {"category": "技术", "source": "book"}
    ],
    ids=["doc_0", "doc_1"]
)

# 带元数据搜索
results = collection.query(
    query_texts=["Agent 定义"],
    n_results=2,
    where={"category": "概念"}
)
```

### 5.2.3 Milvus 使用

**安装**:

```bash
pip install pymilvus
```

**基本用法**:

```python
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType

# 连接 Milvus
connections.connect(host="localhost", port="19530")

# 创建集合
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=500)
]
schema = CollectionSchema(fields, description="Agent 相关文档")
collection = Collection(name="agent_documents", schema=schema)

# 插入数据
import numpy as np

embeddings = np.random.randn(10, 768).tolist()
texts = [
    "AI Agent 是一个能够自主感知、决策、行动的智能体",
    "Prompt Engineering 是让 LLM 生成更好输出的技术"
]

collection.insert(
    data=[
        embeddings,
        texts
    ]
)

# 创建索引
collection.create_index(field_name="embedding", index_params={"metric_type": "L2", "index_type": "IVF_FLAT", "params": {"nlist": 128}})

# 搜索
query_vectors = np.random.randn(1, 768).tolist()

search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

results = collection.search(
    data=query_vectors,
    anns_field="embedding",
    param=search_params,
    limit=2,
    expr=None,
    output_fields=["text"]
)

for hit in results[0]:
    print(f"ID: {hit.id}, Distance: {hit.distance}, Text: {hit.entity.get('text')}")
```

### 5.2.4 PGVector 使用

**安装**:

```bash
pip install pgvector
```

**初始化数据库**:

```bash
# 创建数据库
createdb -U postgres agent_memory

# 连接数据库
psql -U postgres -d agent_memory

# 创建扩展
CREATE EXTENSION vector;

# 创建表
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(768),
    metadata JSONB
);
```

**Python 使用**:

```python
import psycopg2
from pgvector.psycopg2 import register_vector
import numpy as np

# 连接数据库
conn = psycopg2.connect(
    host="localhost",
    database="agent_memory",
    user="postgres",
    password="your_password"
)
cursor = conn.cursor()

# 注册向量类型
register_vector(cursor)

# 插入文档
embedding = np.random.randn(768).tolist()

cursor.execute(
    "INSERT INTO documents (content, embedding, metadata) VALUES (%s, %s, %s)",
    ("AI Agent 是一个能够自主感知、决策、行动的智能体", embedding, {"category": "概念"})
)

conn.commit()

# 搜索
query_embedding = np.random.randn(768).tolist()

cursor.execute(
    """
    SELECT content, 1 - (embedding <=> %s) as similarity
    FROM documents
    ORDER BY embedding <=> %s
    LIMIT 2
    """,
    (query_embedding, query_embedding)
)

results = cursor.fetchall()
for content, similarity in results:
    print(f"内容: {content}")
    print(f"相似度: {similarity}")
```

## 5.3 检索增强生成（RAG）

### 5.3.1 什么是 RAG

**检索增强生成（RAG）** 是一种将外部知识库与 LLM 结合的技术。

**核心思想**:
```
用户问题 → 检索相关文档 → 拼接到 Prompt → LLM 生成答案
```

**RAG 工作流程**:

```
┌─────────────────────────────────────────────────────────┐
│                    RAG 工作流程                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 用户问题                                             │
│     "Agent 的定义是什么？"                              │
│         ↓                                               │
│  2. 向量检索（从知识库检索相关文档）                      │
│     - 文档1: "AI Agent 是一个能够自主感知、决策、行动的智能体"  │
│     - 文档2: "Agent 是一个智能体，能够自主完成任务"        │
│         ↓                                               │
│  3. 构造 Prompt（检索结果 + 用户问题）                    │
│     "请根据以下信息回答用户问题：                        │
│      - 文档1: AI Agent 是一个能够自主感知、决策、行动的智能体
│      - 文档2: Agent 是一个智能体，能够自主完成任务
│      - 用户问题: Agent 的定义是什么？"                   │
│         ↓                                               │
│  4. LLM 生成答案                                         │
│     "Agent 是一个能够自主感知、决策、行动的智能体"        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 5.3.2 RAG 实现代码

```python
from openai import OpenAI
from chromadb import Client
import chromadb

# 初始化 ChromaDB
client = Client()
collection = client.create_collection(name="knowledge_base")

# 添加知识库文档
knowledge = [
    {
        "id": "doc_1",
        "content": "AI Agent 是一个能够自主感知、决策、行动的智能体",
        "metadata": {"category": "概念"}
    },
    {
        "id": "doc_2",
        "content": "Prompt Engineering 是让 LLM 生成更好输出的技术",
        "metadata": {"category": "技术"}
    },
    {
        "id": "doc_3",
        "content": "ReAct 是一种让 Agent 推理并调用工具的框架",
        "metadata": {"category": "框架"}
    },
    {
        "id": "doc_4",
        "content": "Chain-of-Thought 是让模型逐步推理的 Prompt 技术",
        "metadata": {"category": "技术"}
    }
]

# 添加到 ChromaDB
for doc in knowledge:
    collection.add(
        documents=[doc["content"]],
        metadatas=[doc["metadata"]],
        ids=[doc["id"]]
    )

# 初始化 OpenAI
llm_client = OpenAI(api_key="your-api-key")

# RAG 实现
class RAGAgent:
    def __init__(self, knowledge_collection, llm_client):
        self.knowledge_collection = knowledge_collection
        self.llm_client = llm_client

    def retrieve(self, query, top_k=2):
        """检索相关文档"""
        results = self.knowledge_collection.query(
            query_texts=[query],
            n_results=top_k
        )

        documents = []
        for i in range(len(results['documents'][0])):
            document = {
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i]
            }
            documents.append(document)

        return documents

    def generate_answer(self, query, documents):
        """生成答案"""
        # 构造 Prompt
        context = "\n".join([f"- {doc['content']}" for doc in documents])

        prompt = f"""
        请根据以下信息回答用户问题：

        知识库：
        {context}

        用户问题：{query}

        请直接回答，不要提及"根据信息"等字样。
        """

        # 调用 LLM
        response = self.llm_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "你是一个知识问答助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1024
        )

        return response.choices[0].message.content

    def ask(self, query):
        """RAG 查询"""
        # 1. 检索相关文档
        documents = self.retrieve(query, top_k=2)

        # 2. 生成答案
        answer = self.generate_answer(query, documents)

        return {
            "query": query,
            "documents": documents,
            "answer": answer
        }

# 使用
rag_agent = RAGAgent(collection, llm_client)

result = rag_agent.ask("Agent 的定义是什么？")

print(f"用户问题：{result['query']}")
print("\n检索到的文档：")
for doc in result['documents']:
    print(f"- {doc['content']}")

print("\n答案：")
print(result['answer'])
```

### 5.3.3 RAG 优化

**优化1: 分块检索**:

```python
def retrieve(self, query, top_k=2, chunk_size=500):
    """分块检索"""
    # 将长文档分割成小块
    chunks = self.split_document(query, chunk_size)

    # 对每个块进行检索
    all_results = []
    for chunk in chunks:
        results = self.knowledge_collection.query(
            query_texts=[chunk],
            n_results=top_k
        )

        for i in range(len(results['documents'][0])):
            all_results.append({
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i]
            })

    # 去重并返回最相关的结果
    return self.deduplicate_results(all_results, top_k)
```

**优化2: 混合检索**:

```python
def retrieve(self, query, top_k=2):
    """混合检索（关键词 + 向量）"""
    # 1. 向量检索
    vector_results = self.knowledge_collection.query(
        query_texts=[query],
        n_results=top_k
    )

    # 2. 关键词检索（使用全文搜索引擎）
    keyword_results = self.fulltext_search(query)

    # 3. 合并结果
    all_results = self.merge_results(vector_results, keyword_results)

    return all_results
```

## 5.4 记忆系统架构设计

### 5.4.1 记忆系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    记忆系统架构                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  记忆管理层                        │  │
│  │  - 记忆创建                                          │  │
│  │  - 记忆更新                                          │  │
│  │  - 记忆删除                                          │  │
│  │  - 记忆检索                                          │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 短期记忆      │  │ 长期记忆      │  │ 知识库        │  │
│  │ (短期上下文)  │  │ (长期上下文)  │  │ (RAG)        │  │
│  │              │  │              │  │              │  │
│  │ - 当前对话    │  │ - 对话历史    │  │ - 文档        │  │
│  │ - 当前任务    │  │ - 用户偏好    │  │ - 知识图谱    │  │
│  │ - 当前状态    │  │ - 用户信息    │  │ - 实体知识    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                        ↓                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  存储层                            │  │
│  │  - 内存（短期记忆）                                  │  │
│  │  - PostgreSQL（长期记忆）                           │  │
│  │  - ChromaDB（知识库）                                │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 5.4.2 记忆系统实现

```python
class MemorySystem:
    def __init__(self):
        # 初始化短期记忆
        self.short_term = ShortTermMemory(max_tokens=4096)

        # 初始化长期记忆
        self.long_term = LongTermMemory(db_path="memory.db")

        # 初始化知识库（RAG）
        self.knowledge_base = ChromaKnowledgeBase()

    def add_message(self, role, content):
        """添加消息"""
        # 添加到短期记忆
        self.short_term.add_message(role, content)

        # 如果是用户消息，保存到长期记忆
        if role == "user":
            self.long_term.save_memory(role, content)

    def get_context(self):
        """获取上下文"""
        # 合并短期记忆和长期记忆
        short_term_context = self.short_term.get_context()
        long_term_memories = self.long_term.retrieve_memories("")

        # 合并上下文
        context = short_term_context + long_term_memories

        return context

    def retrieve_knowledge(self, query, top_k=2):
        """检索知识"""
        return self.knowledge_base.search(query, top_k)

    def save_knowledge(self, documents):
        """保存知识"""
        self.knowledge_base.add_documents(documents)

# 使用
memory_system = MemorySystem()

# 添加消息
memory_system.add_message("system", "你是一个写作助手")
memory_system.add_message("user", "请写一篇文章")

# 获取上下文
context = memory_system.get_context()
print(f"上下文包含 {len(context)} 条消息")

# 检索知识
knowledge = memory_system.retrieve_knowledge("Agent 的定义", top_k=2)
print(f"检索到 {len(knowledge)} 条知识")
```

## 5.5 本章总结

### 核心要点

1. **短期记忆**: 对话结束即销毁，限制 token 数量
2. **长期记忆**: 对话结束后仍然保留，存储在数据库中
3. **向量数据库**: ChromaDB、Milvus、PGVector
4. **RAG**: 检索增强生成，将外部知识库与 LLM 结合
5. **记忆系统架构**: 记忆管理层 + 存储层

### 实战技巧

- **短期记忆**: 使用队列管理，限制 token 数量
- **长期记忆**: 使用 PostgreSQL 存储结构化数据
- **向量数据库**: ChromaDB 轻量级，适合小规模应用
- **RAG**: 分块检索、混合检索优化效果
- **记忆系统**: 短期 + 长期 + 知识库三层架构

### 练习题

1. 实现一个简单的短期记忆系统
2. 使用 ChromaDB 实现一个知识库
3. 使用 PGVector 实现一个向量搜索引擎
4. 使用 RAG 实现一个问答系统

### 下章预告

第6章将介绍 **Harness 工具框架**，包括：
- 工具的定义与注册
- 工具的调用机制
- 工具的参数验证
- 工具的错误处理

---

**本章完**

**下一章**: [第6章：Harness 工具框架](./06-chapter6-harness.md)
