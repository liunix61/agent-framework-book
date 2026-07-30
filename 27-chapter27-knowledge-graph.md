# 第27章：Agent 记忆系统实现

## 本章目标

通过实战项目，掌握 Agent 记忆系统的实现方法。

## 前置知识

- **基础 记忆**: 短期记忆、长期记忆
- **基础 数据库**: PostgreSQL、Redis
- **基础 项目**: 项目结构、代码组织

## 27.1 记忆架构设计

### 27.1.1 记忆系统概述

**1. 记忆系统架构**

```
┌─────────────────────────────────────────────────────────┐
│                    Agent 记忆系统                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  记忆管理层                        │  │
│  │  - 短期记忆管理器                                  │  │
│  │  - 长期记忆管理器                                  │  │
│  │  - 记忆压缩器                                      │  │
│  │  - 记忆检索器                                      │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  记忆存储层                        │  │
│  │  - 短期记忆存储（内存）                            │  │
│  │  - 长期记忆存储（PostgreSQL）                      │  │
│  │  - 向量存储（ChromaDB）                            │  │
│  │  - 知识图谱（Neo4j）                              │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**2. 记忆类型**

| 记忆类型 | 存储位置 | 生命周期 | 用途 |
|---------|---------|---------|------|
| **短期记忆** | 内存 | 短期（几分钟到几小时） | 当前任务上下文 |
| **长期记忆** | 数据库 | 长期（永久） | 知识积累 |
| **向量记忆** | 向量数据库 | 长期 | 语义检索 |
| **知识图谱** | 图数据库 | 长期 | 关系推理 |

### 27.1.2 记忆架构设计

**1. 记忆模型**

```python
# memory/models.py
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

class Memory:
    """记忆类"""

    def __init__(
        self,
        memory_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        memory_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        初始化记忆

        Args:
            memory_type: 记忆类型（short_term、long_term、vector、knowledge_graph）
            content: 记忆内容
            metadata: 元数据
            memory_id: 记忆 ID
            timestamp: 时间戳
        """
        self.memory_type = memory_type
        self.content = content
        self.metadata = metadata or {}
        self.memory_id = memory_id or str(uuid.uuid4())
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "memory_id": self.memory_id,
            "memory_type": self.memory_type,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Memory':
        """从字典创建"""
        return cls(
            memory_type=data["memory_type"],
            content=data["content"],
            metadata=data.get("metadata"),
            memory_id=data.get("memory_id"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None
        )


# 使用
memory = Memory(
    memory_type="short_term",
    content="用户正在写一首关于春天的诗",
    metadata={
        "user_id": "user_123",
        "task": "写诗"
    }
)

print(memory.to_dict())
```

**2. 记忆管理器接口**

```python
# memory/manager.py
from typing import Dict, Any, List, Optional

class MemoryManager:
    """记忆管理器接口"""

    def add_memory(self, memory: Memory) -> str:
        """
        添加记忆

        Args:
            memory: 记忆

        Returns:
            记忆 ID
        """
        raise NotImplementedError

    def get_memory(self, memory_id: str) -> Optional[Memory]:
        """
        获取记忆

        Args:
            memory_id: 记忆 ID

        Returns:
            记忆
        """
        raise NotImplementedError

    def search_memory(
        self,
        query: str,
        memory_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Memory]:
        """
        搜索记忆

        Args:
            query: 查询
            memory_type: 记忆类型
            limit: 限制数量

        Returns:
            记忆列表
        """
        raise NotImplementedError

    def delete_memory(self, memory_id: str):
        """
        删除记忆

        Args:
            memory_id: 记忆 ID
        """
        raise NotImplementedError

    def list_memories(
        self,
        memory_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Memory]:
        """
        列出记忆

        Args:
            memory_type: 记忆类型
            limit: 限制数量

        Returns:
            记忆列表
        """
        raise NotImplementedError
```

## 27.2 短期记忆实现

### 27.2.1 短期记忆管理器

**1. 短期记忆管理器实现**

```python
# memory/short_term_memory.py
import asyncio
from typing import Dict, Any, List, Optional
from collections import OrderedDict
from memory.models import Memory
from memory.manager import MemoryManager

class ShortTermMemoryManager(MemoryManager):
    """短期记忆管理器"""

    def __init__(self, max_size: int = 100):
        """
        初始化短期记忆管理器

        Args:
            max_size: 最大记忆数量
        """
        self.max_size = max_size
        self.memories: OrderedDict[str, Memory] = OrderedDict()

    def add_memory(self, memory: Memory) -> str:
        """
        添加记忆

        Args:
            memory: 记忆

        Returns:
            记忆 ID
        """
        # 添加到 OrderedDict
        self.memories[memory.memory_id] = memory

        # 移除最旧的记忆
        if len(self.memories) > self.max_size:
            self.memories.popitem(last=False)

        return memory.memory_id

    def get_memory(self, memory_id: str) -> Optional[Memory]:
        """
        获取记忆

        Args:
            memory_id: 记忆 ID

        Returns:
            记忆
        """
        return self.memories.get(memory_id)

    def search_memory(
        self,
        query: str,
        memory_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Memory]:
        """
        搜索记忆

        Args:
            query: 查询
            memory_type: 记忆类型
            limit: 限制数量

        Returns:
            记忆列表
        """
        results = []

        for memory_id, memory in self.memories.items():
            # 过滤记忆类型
            if memory_type and memory.memory_type != memory_type:
                continue

            # 检查查询是否匹配
            if query.lower() in memory.content.lower():
                results.append(memory)

                # 达到限制数量时停止
                if limit and len(results) >= limit:
                    break

        return results

    def delete_memory(self, memory_id: str):
        """
        删除记忆

        Args:
            memory_id: 记忆 ID
        """
        if memory_id in self.memories:
            del self.memories[memory_id]

    def list_memories(
        self,
        memory_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Memory]:
        """
        列出记忆

        Args:
            memory_type: 记忆类型
            limit: 限制数量

        Returns:
            记忆列表
        """
        results = []

        for memory_id, memory in self.memories.items():
            # 过滤记忆类型
            if memory_type and memory.memory_type != memory_type:
                continue

            results.append(memory)

            # 达到限制数量时停止
            if limit and len(results) >= limit:
                break

        return results

    def clear(self):
        """清空所有记忆"""
        self.memories.clear()

    def get_size(self) -> int:
        """获取记忆数量"""
        return len(self.memories)


# 使用
short_term_memory = ShortTermMemoryManager(max_size=10)

# 添加记忆
memory1 = Memory(
    memory_type="short_term",
    content="用户正在写一首关于春天的诗"
)
short_term_memory.add_memory(memory1)

memory2 = Memory(
    memory_type="short_term",
    content="用户喜欢诗歌"
)
short_term_memory.add_memory(memory2)

# 搜索记忆
results = short_term_memory.search_memory("诗歌", limit=10)

for result in results:
    print(f"记忆 ID：{result.memory_id}")
    print(f"记忆内容：{result.content}")
    print()

# 列出记忆
knowledge_list = short_term_memory.list_memories(limit=10)

for knowledge in knowledge_list:
    print(f"记忆 ID：{knowledge.memory_id}")
    print(f"记忆内容：{knowledge.content}")
    print()
```

**2. 短期记忆使用示例**

```python
# 使用短期记忆
short_term_memory = ShortTermMemoryManager(max_size=10)

# 添加短期记忆
short_term_memory.add_memory(
    Memory(
        memory_type="short_term",
        content="用户正在写一首关于春天的诗"
    )
)

# 搜索短期记忆
results = short_term_memory.search_memory("诗歌")

for result in results:
    print(result.content)
```

## 27.3 长期记忆实现

### 27.3.1 长期记忆管理器

**1. 长期记忆管理器实现**

```python
# memory/long_term_memory.py
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime
from memory.models import Memory
from memory.manager import MemoryManager

class LongTermMemoryManager(MemoryManager):
    """长期记忆管理器"""

    def __init__(self, database_path: str = "memory.db"):
        """
        初始化长期记忆管理器

        Args:
            database_path: 数据库路径
        """
        self.database_path = database_path
        self._init_database()

    def _init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            # 创建记忆表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    memory_id TEXT PRIMARY KEY,
                    memory_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    timestamp TEXT NOT NULL
                )
            """)

            conn.commit()

    def add_memory(self, memory: Memory) -> str:
        """
        添加记忆

        Args:
            memory: 记忆

        Returns:
            记忆 ID
        """
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            # 插入记忆
            cursor.execute("""
                INSERT INTO memories (
                    memory_id, memory_type, content, metadata, timestamp
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                memory.memory_id,
                memory.memory_type,
                memory.content,
                str(memory.metadata),
                memory.timestamp.isoformat()
            ))

            conn.commit()

        return memory.memory_id

    def get_memory(self, memory_id: str) -> Optional[Memory]:
        """
        获取记忆

        Args:
            memory_id: 记忆 ID

        Returns:
            记忆
        """
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            # 查询记忆
            cursor.execute("""
                SELECT memory_id, memory_type, content, metadata, timestamp
                FROM memories
                WHERE memory_id = ?
            """, (memory_id,))

            row = cursor.fetchone()

            if row is None:
                return None

            return Memory(
                memory_id=row[0],
                memory_type=row[1],
                content=row[2],
                metadata=eval(row[3]) if row[3] else None,
                timestamp=datetime.fromisoformat(row[4])
            )

    def search_memory(
        self,
        query: str,
        memory_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Memory]:
        """
        搜索记忆

        Args:
            query: 查询
            memory_type: 记忆类型
            limit: 限制数量

        Returns:
            记忆列表
        """
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            # 构建查询
            sql = "SELECT memory_id, memory_type, content, metadata, timestamp FROM memories WHERE 1=1"
            params = []

            # 过滤记忆类型
            if memory_type:
                sql += " AND memory_type = ?"
                params.append(memory_type)

            # 搜索内容
            sql += " AND content LIKE ?"
            params.append(f"%{query}%")

            # 限制数量
            if limit:
                sql += " LIMIT ?"
                params.append(limit)

            # 执行查询
            cursor.execute(sql, params)

            rows = cursor.fetchall()

            # 转换为记忆对象
            memories = []
            for row in rows:
                memories.append(Memory(
                    memory_id=row[0],
                    memory_type=row[1],
                    content=row[2],
                    metadata=eval(row[3]) if row[3] else None,
                    timestamp=datetime.fromisoformat(row[4])
                ))

            return memories

    def delete_memory(self, memory_id: str):
        """
        删除记忆

        Args:
            memory_id: 记忆 ID
        """
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            # 删除记忆
            cursor.execute("""
                DELETE FROM memories
                WHERE memory_id = ?
            """, (memory_id,))

            conn.commit()

    def list_memories(
        self,
        memory_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Memory]:
        """
        列出记忆

        Args:
            memory_type: 记忆类型
            limit: 限制数量

        Returns:
            记忆列表
        """
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            # 构建查询
            sql = "SELECT memory_id, memory_type, content, metadata, timestamp FROM memories WHERE 1=1"
            params = []

            # 过滤记忆类型
            if memory_type:
                sql += " AND memory_type = ?"
                params.append(memory_type)

            # 限制数量
            if limit:
                sql += " LIMIT ?"
                params.append(limit)

            # 执行查询
            cursor.execute(sql, params)

            rows = cursor.fetchall()

            # 转换为记忆对象
            memories = []
            for row in rows:
                memories.append(Memory(
                    memory_id=row[0],
                    memory_type=row[1],
                    content=row[2],
                    metadata=eval(row[3]) if row[3] else None,
                    timestamp=datetime.fromisoformat(row[4])
                ))

            return memories


# 使用
long_term_memory = LongTermMemoryManager(database_path="memory.db")

# 添加记忆
long_term_memory.add_memory(
    Memory(
        memory_type="long_term",
        content="用户喜欢诗歌",
        metadata={
            "user_id": "user_123",
            "category": "偏好"
        }
    )
)

# 搜索记忆
results = long_term_memory.search_memory("诗歌", limit=10)

for result in results:
    print(f"记忆 ID：{result.memory_id}")
    print(f"记忆内容：{result.content}")
    print()

# 列出记忆
knowledge_list = long_term_memory.list_memories(limit=10)

for knowledge in knowledge_list:
    print(f"记忆 ID：{knowledge.memory_id}")
    print(f"记忆内容：{knowledge.content}")
    print()
```

## 27.4 记忆压缩与检索

### 27.4.1 记忆压缩

**1. 记忆压缩器**

```python
# memory/compressor.py
from typing import Dict, Any

class MemoryCompressor:
    """记忆压缩器"""

    def compress(self, memory: Memory) -> Memory:
        """
        压缩记忆

        Args:
            memory: 记忆

        Returns:
            压缩后的记忆
        """
        compressed_content = self._compress_content(memory.content)

        return Memory(
            memory_type=memory.memory_type,
            content=compressed_content,
            metadata=memory.metadata,
            memory_id=memory.memory_id,
            timestamp=memory.timestamp
        )

    def _compress_content(self, content: str) -> str:
        """
        压缩内容

        Args:
            content: 内容

        Returns:
            压缩后的内容
        """
        # 简单的压缩：移除多余空格
        compressed = " ".join(content.split())

        return compressed


# 使用
compressor = MemoryCompressor()

# 压缩记忆
memory = Memory(
    memory_type="long_term",
    content="用户喜欢诗歌"
)

compressed_memory = compressor.compress(memory)

print(f"原始内容：{memory.content}")
print(f"压缩内容：{compressed_memory.content}")
```

### 27.4.2 记忆检索

**1. 记忆检索器**

```python
# memory/retriever.py
from typing import Dict, Any, List, Optional
from memory.models import Memory

class MemoryRetriever:
    """记忆检索器"""

    def __init__(self, memory_managers: Dict[str, MemoryManager]):
        """
        初始化记忆检索器

        Args:
            memory_managers: 记忆管理器字典
        """
        self.memory_managers = memory_managers

    def retrieve(
        self,
        query: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Memory]:
        """
        检索记忆

        Args:
            query: 查询
            memory_types: 记忆类型列表
            limit: 限制数量

        Returns:
            记忆列表
        """
        results = []

        # 检索所有记忆类型
        for memory_type, manager in self.memory_managers.items():
            # 过滤记忆类型
            if memory_types and memory_type not in memory_types:
                continue

            # 搜索记忆
            memories = manager.search_memory(query, limit=limit)

            results.extend(memories)

        # 按时间戳排序
        results.sort(key=lambda x: x.timestamp, reverse=True)

        # 返回前 N 个结果
        return results[:limit]

    def retrieve_by_type(
        self,
        query: str,
        memory_type: str,
        limit: int = 10
    ) -> List[Memory]:
        """
        按类型检索记忆

        Args:
            query: 查询
            memory_type: 记忆类型
            limit: 限制数量

        Returns:
            记忆列表
        """
        # 检索指定类型的记忆
        memories = self.memory_managers.get(memory_type).search_memory(
            query,
            limit=limit
        )

        # 按时间戳排序
        memories.sort(key=lambda x: x.timestamp, reverse=True)

        return memories


# 使用
short_term_memory = ShortTermMemoryManager(max_size=10)
long_term_memory = LongTermMemoryManager(database_path="memory.db")

memory_managers = {
    "short_term": short_term_memory,
    "long_term": long_term_memory
}

retriever = MemoryRetriever(memory_managers)

# 检索记忆
results = retriever.retrieve("诗歌", limit=10)

for result in results:
    print(f"记忆类型：{result.memory_type}")
    print(f"记忆内容：{result.content}")
    print()
```

## 27.5 本章总结

### 核心要点

1. **记忆架构设计**: 记忆系统架构、记忆类型
2. **短期记忆实现**: 短期记忆管理器实现
3. **长期记忆实现**: 长期记忆管理器实现
4. **记忆压缩与检索**: 记忆压缩器、记忆检索器

### 实战技巧

- **短期记忆**: 使用 OrderedDict 实现最近最少使用（LRU）缓存
- **长期记忆**: 使用 SQLite 存储记忆，支持复杂查询
- **记忆压缩**: 简单的压缩算法，移除多余空格
- **记忆检索**: 多类型记忆检索，按时间戳排序

### 练习题

1. 实现短期记忆管理器
2. 实现长期记忆管理器
3. 实现记忆压缩器
4. 实现记忆检索器

### 下章预告

第28章将介绍 **Agent 知识图谱实现**，包括：
- 知识图谱设计
- 知识图谱存储
- 知识图谱检索

---

**本章完**

**下一章**: [第28章：Agent 知识图谱实现](./28-chapter27-knowledge-graph.md)
