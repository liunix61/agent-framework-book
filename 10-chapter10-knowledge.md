# 第10章：记忆与知识管理

## 本章目标

掌握 Agent 的记忆与知识管理机制，包括知识管理架构、知识图谱、记忆压缩与检索。

## 前置知识

- **基础 Python/C++**: 类、继承、装饰器
- **基础数据库**: PostgreSQL、Redis
- **基础图论**: 图、节点、边

## 10.1 知识管理架构

### 10.1.1 知识管理概念

**知识管理（Knowledge Management）** 是指收集、组织、存储和检索 Agent 的知识的过程。

**核心功能**:
- **知识收集**: 收集新的知识
- **知识组织**: 组织和分类知识
- **知识存储**: 存储知识
- **知识检索**: 检索知识

### 10.1.2 知识管理架构

```
┌─────────────────────────────────────────────────────────┐
│                    知识管理架构                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  知识管理层                        │  │
│  │  - 知识创建                                          │  │
│  │  - 知识更新                                          │  │
│  │  - 知识删除                                          │  │
│  │  - 知识检索                                          │  │
│  │  - 知识分类                                          │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 短期知识      │  │ 长期知识      │  │ 知识图谱      │  │
│  │ (临时知识)    │  │ (持久知识)    │  │ (知识关系)    │  │
│  │              │  │              │  │              │  │
│  │ - 当前对话    │  │ - 对话历史    │  │ - 实体关系    │  │
│  │ - 当前任务    │  │ - 用户偏好    │  │ - 知识图谱    │  │
│  │ - 当前状态    │  │ - 常见问题    │  │ - 概念关联    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                        ↓                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  存储层                            │  │
│  │  - PostgreSQL（长期知识）                           │  │
│  │  - Redis（短期知识）                                 │  │
│  │  - Neo4j（知识图谱）                                │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 10.1.3 知识类型

| 知识类型 | 特点 | 存储方式 | 生命周期 |
|---------|------|---------|---------|
| **事实知识** | 静态、明确 | PostgreSQL | 永久 |
| **过程知识** | 动态、可变 | Redis | 短期 |
| **关系知识** | 依赖关系 | Neo4j | 永久 |
| **经验知识** | 基于经验 | PostgreSQL | 长期 |

## 10.2 知识图谱

### 10.2.1 什么是知识图谱

**知识图谱（Knowledge Graph）** 是一种以图结构表示知识的框架。

**核心组件**:
- **实体（Entity）**: 图的节点
- **关系（Relation）**: 图的边
- **属性（Property）**: 节点的属性

### 10.2.2 Neo4j 基础

**安装 Neo4j**:

```bash
# Ubuntu/Debian
wget -O - https://debian.neo4j.com/neorgpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt update
sudo apt install neo4j

# 启动 Neo4j
sudo systemctl start neo4j
sudo systemctl enable neo4j

# 访问 Neo4j
# http://localhost:7474
# 用户名：neo4j
# 密码：neo4j
```

**Python 使用 Neo4j**:

```python
from neo4j import GraphDatabase

class KnowledgeGraph:
    """知识图谱"""

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_entity(self, name: str, properties: dict):
        """创建实体"""
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_and_return_entity, name, properties
            )
            return result

    @staticmethod
    def _create_and_return_entity(tx, name, properties):
        query = """
        CREATE (e:Entity {name: $name, properties: $properties})
        RETURN e
        """
        result = tx.run(query, name=name, properties=properties)
        return result.single()[0]

    def create_relationship(self, from_entity: str, to_entity: str, rel_type: str):
        """创建关系"""
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_and_return_relationship, from_entity, to_entity, rel_type
            )
            return result

    @staticmethod
    def _create_and_return_relationship(tx, from_entity, to_entity, rel_type):
        query = f"""
        MATCH (a:Entity {{name: $from_entity}})
        MATCH (b:Entity {{name: $to_entity}})
        CREATE (a)-[r:{rel_type}]->(b)
        RETURN r
        """
        result = tx.run(query, from_entity=from_entity, to_entity=to_entity)
        return result.single()[0]

    def find_entity(self, name: str):
        """查找实体"""
        with self.driver.session() as session:
            result = session.read_transaction(
                self._find_entity, name
            )
            return result

    @staticmethod
    def _find_entity(tx, name):
        query = """
        MATCH (e:Entity {name: $name})
        RETURN e
        """
        result = tx.run(query, name=name)
        return result.single()[0]

    def find_related(self, name: str, rel_type: str):
        """查找相关实体"""
        with self.driver.session() as session:
            result = session.read_transaction(
                self._find_related, name, rel_type
            )
            return result

    @staticmethod
    def _find_related(tx, name, rel_type):
        query = f"""
        MATCH (e:Entity {{name: $name}})-[r:{rel_type}]->(related)
        RETURN related
        """
        result = tx.run(query, name=name)
        return [record["related"] for record in result]


# 使用
kg = KnowledgeGraph("bolt://localhost:7687", "neo4j", "neo4j")

# 创建实体
agent_entity = kg.create_entity("Agent", {"type": "AI Agent", "version": "1.0"})
tool_entity = kg.create_entity("Tool", {"type": "Function", "language": "Python"})

print(f"创建实体：{agent_entity}")

# 创建关系
relation = kg.create_relationship("Agent", "Tool", "uses")
print(f"创建关系：{relation}")

# 查找实体
found_entity = kg.find_entity("Agent")
print(f"查找实体：{found_entity}")

# 查找相关实体
related = kg.find_related("Agent", "uses")
print(f"相关实体：{related}")

# 关闭连接
kg.close()
```

### 10.2.3 知识图谱示例

```python
def build_knowledge_graph():
    """构建知识图谱"""
    kg = KnowledgeGraph("bolt://localhost:7687", "neo4j", "neo4j")

    # 创建实体
    agent = kg.create_entity("Agent", {"type": "AI Agent", "version": "1.0"})
    prompt = kg.create_entity("Prompt", {"type": "Prompt Engineering"})
    harness = kg.create_entity("Harness", {"type": "Tool Framework"})
    loop = kg.create_entity("Loop", {"type": "Loop Control"})
    graph = kg.create_entity("Graph", {"type": "Graph Structure"})
    rag = kg.create_entity("RAG", {"type": "Retrieval Augmented Generation"})

    # 创建关系
    kg.create_relationship("Agent", "Prompt", "uses")
    kg.create_relationship("Agent", "Harness", "uses")
    kg.create_relationship("Agent", "Loop", "uses")
    kg.create_relationship("Agent", "Graph", "uses")
    kg.create_relationship("Agent", "RAG", "uses")

    kg.create_relationship("Prompt", "Harness", "requires")
    kg.create_relationship("Prompt", "RAG", "requires")

    kg.create_relationship("Harness", "Loop", "composes")
    kg.create_relationship("Harness", "Graph", "composes")

    print("知识图谱构建完成！")

    # 查询：Agent 使用的所有组件
    print("\nAgent 使用的所有组件：")
    related = kg.find_related("Agent", "uses")
    for entity in related:
        print(f"- {entity['name']} ({entity.get('properties', {}).get('type', '')})")

    # 查询：Prompt 依赖的所有组件
    print("\nPrompt 依赖的所有组件：")
    related = kg.find_related("Prompt", "requires")
    for entity in related:
        print(f"- {entity['name']} ({entity.get('properties', {}).get('type', '')})")

    kg.close()


# 使用
build_knowledge_graph()
```

## 10.3 记忆压缩与检索

### 10.3.1 记忆压缩

**记忆压缩（Memory Compression）** 是指减少记忆占用的空间。

**压缩方法**:
- **摘要（Summarization）**: 生成摘要
- **关键词提取（Keyword Extraction）**: 提取关键词
- **向量压缩（Vector Compression）**: 向量量化

```python
import numpy as np

class MemoryCompressor:
    """记忆压缩器"""

    @staticmethod
    def summarize(text: str, max_length: int = 100) -> str:
        """生成摘要"""
        # 简单的摘要方法：取前 max_length 个字符
        if len(text) <= max_length:
            return text

        return text[:max_length] + "..."

    @staticmethod
    def extract_keywords(text: str, top_k: int = 5) -> list:
        """提取关键词"""
        # 简单的关键词提取方法：统计词频
        words = text.lower().split()
        word_count = {}

        for word in words:
            if word not in ["the", "a", "an", "and", "or", "but"]:
                word_count[word] = word_count.get(word, 0) + 1

        # 返回出现次数最多的前 top_k 个词
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_words[:top_k]]

    @staticmethod
    def vector_compress(embedding: np.ndarray, compression_ratio: float = 0.5) -> np.ndarray:
        """向量压缩"""
        # 简单的向量压缩方法：取前 compression_ratio 比例的维度
        dim = int(embedding.shape[0] * compression_ratio)
        return embedding[:dim]


# 使用
compressor = MemoryCompressor()

# 摘要
text = "AI Agent 是一个能够自主感知、决策、行动的智能体。Agent 能够使用工具、记忆上下文、与人类交互。"
summary = compressor.summarize(text, max_length=50)
print(f"摘要：{summary}")

# 关键词
keywords = compressor.extract_keywords(text, top_k=5)
print(f"关键词：{keywords}")

# 向量压缩
embedding = np.random.randn(768)
compressed_embedding = compressor.vector_compress(embedding, compression_ratio=0.5)
print(f"原始维度：{embedding.shape[0]}")
print(f"压缩后维度：{compressed_embedding.shape[0]}")
```

### 10.3.2 记忆检索

**记忆检索（Memory Retrieval）** 是指从记忆中检索相关信息。

```python
import sqlite3
from typing import List, Dict, Any

class MemoryStorage:
    """记忆存储"""

    def __init__(self, db_path: str = "memory.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        # 创建记忆表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                relevance_score REAL DEFAULT 0.0
            )
        """)

        self.conn.commit()

    def add_memory(self, type: str, content: str, embedding: list = None, metadata: dict = None):
        """添加记忆"""
        embedding_str = str(embedding) if embedding else None
        metadata_str = str(metadata) if metadata else None

        self.cursor.execute(
            "INSERT INTO memories (type, content, embedding, metadata) VALUES (?, ?, ?, ?)",
            (type, content, embedding_str, metadata_str)
        )

        self.conn.commit()

    def search_by_keyword(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """按关键词搜索"""
        self.cursor.execute(
            "SELECT * FROM memories WHERE content LIKE ? LIMIT ?",
            (f"%{keyword}%", limit)
        )

        memories = self.cursor.fetchall()
        return self._format_results(memories)

    def search_by_embedding(self, query_embedding: list, top_k: int = 10) -> List[Dict[str, Any]]:
        """按向量相似度搜索"""
        # 简单的向量相似度计算（余弦相似度）
        results = []

        self.cursor.execute("SELECT * FROM memories")
        all_memories = self.cursor.fetchall()

        for memory in all_memories:
            memory_embedding = eval(memory[3]) if memory[3] else None

            if memory_embedding:
                similarity = self._cosine_similarity(query_embedding, memory_embedding)
                results.append({
                    "id": memory[0],
                    "type": memory[1],
                    "content": memory[2],
                    "embedding": memory_embedding,
                    "metadata": eval(memory[4]) if memory[4] else None,
                    "relevance_score": similarity
                })

        # 按相似度排序
        results.sort(key=lambda x: x["relevance_score"], reverse=True)

        return results[:top_k]

    @staticmethod
    def _cosine_similarity(vec1: list, vec2: list) -> float:
        """余弦相似度"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    @staticmethod
    def _format_results(results) -> List[Dict[str, Any]]:
        """格式化结果"""
        formatted = []

        for result in results:
            formatted.append({
                "id": result[0],
                "type": result[1],
                "content": result[2],
                "embedding": eval(result[3]) if result[3] else None,
                "metadata": eval(result[4]) if result[4] else None,
                "relevance_score": result[5]
            })

        return formatted

    def clear_old_memories(self, days: int = 30):
        """清除旧记忆"""
        self.cursor.execute(
            "DELETE FROM memories WHERE created_at < datetime('now', '-' || ? || ' days')",
            (days,)
        )

        self.conn.commit()

    def close(self):
        """关闭连接"""
        self.conn.close()


# 使用
storage = MemoryStorage()

# 添加记忆
storage.add_memory(
    type="concept",
    content="AI Agent 是一个能够自主感知、决策、行动的智能体",
    embedding=np.random.randn(768).tolist(),
    metadata={"category": "概念"}
)

storage.add_memory(
    type="tool",
    content="Prompt Engineering 是让 LLM 生成更好输出的技术",
    embedding=np.random.randn(768).tolist(),
    metadata={"category": "技术"}
)

storage.add_memory(
    type="framework",
    content="ReAct 是一种让 Agent 推理并调用工具的框架",
    embedding=np.random.randn(768).tolist(),
    metadata={"category": "框架"}
)

# 按关键词搜索
print("\n按关键词搜索：")
results = storage.search_by_keyword("Agent", limit=2)
for result in results:
    print(f"- {result['content']} (相似度：{result['relevance_score']:.2f})")

# 按向量相似度搜索
print("\n按向量相似度搜索：")
query_embedding = np.random.randn(768).tolist()
results = storage.search_by_embedding(query_embedding, top_k=2)
for result in results:
    print(f"- {result['content']} (相似度：{result['relevance_score']:.2f})")

# 关闭连接
storage.close()
```

## 10.4 知识库集成

### 10.4.1 RAG 知识库

```python
from openai import OpenAI
import chromadb

class RAGKnowledgeBase:
    """RAG 知识库"""

    def __init__(self, collection_name: str = "knowledge_base"):
        # 初始化 ChromaDB
        self.client = chromadb.Client()
        self.collection = self.client.create_collection(name=collection_name)

        # 初始化 LLM
        self.llm_client = OpenAI(api_key="your-api-key")

    def add_document(self, document_id: str, content: str, metadata: dict = None):
        """添加文档"""
        self.collection.add(
            documents=[content],
            metadatas=[metadata or {}],
            ids=[document_id]
        )
        print(f"已添加文档：{document_id}")

    def search(self, query: str, top_k: int = 2) -> List[dict]:
        """搜索文档"""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )

        documents = []
        for i in range(len(results['documents'][0])):
            document = {
                "id": results['ids'][0][i],
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i]
            }
            documents.append(document)

        return documents

    def generate_answer(self, query: str, top_k: int = 2) -> str:
        """生成答案（RAG）"""
        # 搜索相关文档
        documents = self.search(query, top_k)

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


# 使用
rag_kb = RAGKnowledgeBase()

# 添加文档
rag_kb.add_document(
    document_id="doc_1",
    content="AI Agent 是一个能够自主感知、决策、行动的智能体",
    metadata={"category": "概念"}
)

rag_kb.add_document(
    document_id="doc_2",
    content="Prompt Engineering 是让 LLM 生成更好输出的技术",
    metadata={"category": "技术"}
)

rag_kb.add_document(
    document_id="doc_3",
    content="ReAct 是一种让 Agent 推理并调用工具的框架",
    metadata={"category": "框架"}
)

# 生成答案
answer = rag_kb.generate_answer("Agent 的定义是什么？")
print(f"\n答案：{answer}")
```

### 10.4.2 知识库管理器

```python
class KnowledgeBaseManager:
    """知识库管理器"""

    def __init__(self, rag_kb: RAGKnowledgeBase, memory_storage: MemoryStorage):
        self.rag_kb = rag_kb
        self.memory_storage = memory_storage

    def add_knowledge(self, type: str, content: str, metadata: dict = None):
        """添加知识"""
        # 添加到 RAG 知识库
        document_id = f"{type}_{len(self.rag_kb.collection.get()['ids'])}"
        self.rag_kb.add_document(document_id, content, metadata)

        # 添加到记忆存储
        self.memory_storage.add_memory(type, content)

    def search_knowledge(self, query: str, top_k: int = 2) -> List[dict]:
        """搜索知识"""
        # 在 RAG 知识库中搜索
        rag_results = self.rag_kb.search(query, top_k)

        # 在记忆存储中搜索
        memory_results = self.memory_storage.search_by_keyword(query, limit=top_k)

        # 合并结果
        all_results = []

        for result in rag_results:
            all_results.append({
                "source": "RAG",
                "content": result["content"],
                "metadata": result["metadata"]
            })

        for result in memory_results:
            all_results.append({
                "source": "Memory",
                "content": result["content"],
                "metadata": result["metadata"]
            })

        return all_results

    def generate_answer(self, query: str, top_k: int = 2) -> str:
        """生成答案"""
        return self.rag_kb.generate_answer(query, top_k)


# 使用
rag_kb = RAGKnowledgeBase()
memory_storage = MemoryStorage()
manager = KnowledgeBaseManager(rag_kb, memory_storage)

# 添加知识
manager.add_knowledge(
    type="concept",
    content="AI Agent 是一个能够自主感知、决策、行动的智能体",
    metadata={"category": "概念"}
)

manager.add_knowledge(
    type="tool",
    content="Prompt Engineering 是让 LLM 生成更好输出的技术",
    metadata={"category": "技术"}
)

# 搜索知识
print("\n搜索知识：")
results = manager.search_knowledge("Agent", top_k=2)
for result in results:
    print(f"- [{result['source']}] {result['content']}")

# 生成答案
answer = manager.generate_answer("Agent 的定义是什么？")
print(f"\n答案：{answer}")
```

## 10.5 本章总结

### 核心要点

1. **知识管理架构**: 知识管理层、短期知识、长期知识、知识图谱
2. **知识图谱**: Neo4j 基础、实体、关系
3. **记忆压缩**: 摘要、关键词提取、向量压缩
4. **记忆检索**: 关键词搜索、向量相似度搜索
5. **知识库集成**: RAG 知识库、知识库管理器

### 实战技巧

- **知识管理**: 定义知识类型、存储方式
- **知识图谱**: 使用 Neo4j 建立实体关系
- **记忆压缩**: 减少记忆占用的空间
- **记忆检索**: 使用关键词和向量相似度
- **知识库集成**: 结合 RAG 和记忆存储

### 练习题

1. 实现一个简单的知识图谱
2. 实现一个记忆压缩器
3. 实现一个记忆检索系统
4. 实现一个 RAG 知识库

### 下章预告

第11章将介绍 **协议栈设计**，包括：
- 协议栈概念
- A2A 协议设计
- MCP 协议设计
- OKF 协议设计

---

**本章完**

**下一章**: [第11章：协议栈设计](./11-chapter11-protocols.md)
