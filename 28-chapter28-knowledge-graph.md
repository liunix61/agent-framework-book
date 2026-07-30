# 第28章：Agent 知识图谱实现

## 本章目标

通过实战项目，掌握 Agent 知识图谱的实现方法。

## 前置知识

- **基础 图数据库**: Neo4j
- **基础 图理论**: 节点、边、图结构
- **基础 项目**: 项目结构、代码组织

## 28.1 知识图谱设计

### 28.1.1 知识图谱概述

**1. 知识图谱架构**

```
┌─────────────────────────────────────────────────────────┐
│                    Agent 知识图谱                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  知识管理层                        │  │
│  │  - 知识节点管理器                                  │  │
│  │  - 知识关系管理器                                  │  │
│  │  - 知识检索器                                      │  │
│  │  - 知识推理器                                      │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  知识存储层                        │  │
│  │  - Neo4j 图数据库                                  │  │
│  │  - 节点（实体）                                    │  │
│  │  - 边（关系）                                      │  │
│  │  - 属性（数据）                                    │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**2. 知识图谱类型**

| 知识图谱类型 | 说明 | 用途 |
|-------------|------|------|
| **概念图谱** | 概念之间的关系 | 知识推理 |
| **实体图谱** | 实体之间的关系 | 关系推理 |
| **事件图谱** | 事件之间的关系 | 事件推理 |
| **知识图谱** | 综合知识图谱 | 综合推理 |

### 28.1.2 知识图谱设计

**1. 知识节点**

```python
# knowledge_graph/models.py
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

class KnowledgeNode:
    """知识节点"""

    def __init__(
        self,
        node_id: str,
        label: str,
        properties: Dict[str, Any],
        node_type: str = "entity",
        created_at: Optional[datetime] = None
    ):
        """
        初始化知识节点

        Args:
            node_id: 节点 ID
            label: 节点标签
            properties: 属性
            node_type: 节点类型（entity、concept、event）
            created_at: 创建时间
        """
        self.node_id = node_id
        self.label = label
        self.properties = properties
        self.node_type = node_type
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "node_id": self.node_id,
            "label": self.label,
            "properties": self.properties,
            "node_type": self.node_type,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeNode':
        """从字典创建"""
        return cls(
            node_id=data["node_id"],
            label=data["label"],
            properties=data["properties"],
            node_type=data.get("node_type", "entity"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
        )


# 使用
node = KnowledgeNode(
    node_id="node_1",
    label="AI Agent",
    properties={
        "description": "AI Agent 是一种能够自主执行任务的 AI 系统",
        "category": "AI",
        "keywords": ["AI", "Agent", "自主"]
    },
    node_type="concept"
)

print(node.to_dict())
```

**2. 知识边**

```python
# knowledge_graph/models.py
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

class KnowledgeEdge:
    """知识边"""

    def __init__(
        self,
        edge_id: str,
        source_node_id: str,
        target_node_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None
    ):
        """
        初始化知识边

        Args:
            edge_id: 边 ID
            source_node_id: 源节点 ID
            target_node_id: 目标节点 ID
            relationship_type: 关系类型
            properties: 属性
            edge_id: 边 ID
            created_at: 创建时间
        """
        self.edge_id = edge_id or str(uuid.uuid4())
        self.source_node_id = source_node_id
        self.target_node_id = target_node_id
        self.relationship_type = relationship_type
        self.properties = properties or {}
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "edge_id": self.edge_id,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "relationship_type": self.relationship_type,
            "properties": self.properties,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeEdge':
        """从字典创建"""
        return cls(
            edge_id=data["edge_id"],
            source_node_id=data["source_node_id"],
            target_node_id=data["target_node_id"],
            relationship_type=data["relationship_type"],
            properties=data.get("properties"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
        )


# 使用
edge = KnowledgeEdge(
    edge_id="edge_1",
    source_node_id="node_1",
    target_node_id="node_2",
    relationship_type="PART_OF",
    properties={
        "weight": 0.8,
        "confidence": 0.9
    }
)

print(edge.to_dict())
```

**3. 知识图谱**

```python
# knowledge_graph/models.py
from typing import Dict, Any, List, Optional
from memory.models import Memory

class KnowledgeGraph:
    """知识图谱"""

    def __init__(self):
        """初始化知识图谱"""
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: Dict[str, KnowledgeEdge] = {}

    def add_node(self, node: KnowledgeNode):
        """
        添加节点

        Args:
            node: 知识节点
        """
        self.nodes[node.node_id] = node

    def add_edge(self, edge: KnowledgeEdge):
        """
        添加边

        Args:
            edge: 知识边
        """
        self.edges[edge.edge_id] = edge

    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """
        获取节点

        Args:
            node_id: 节点 ID

        Returns:
            知识节点
        """
        return self.nodes.get(node_id)

    def get_edge(self, edge_id: str) -> Optional[KnowledgeEdge]:
        """
        获取边

        Args:
            edge_id: 边 ID

        Returns:
            知识边
        """
        return self.edges.get(edge_id)

    def get_neighbors(self, node_id: str) -> List[KnowledgeNode]:
        """
        获取邻居节点

        Args:
            node_id: 节点 ID

        Returns:
            邻居节点列表
        """
        neighbors = []

        for edge in self.edges.values():
            if edge.source_node_id == node_id:
                neighbors.append(self.get_node(edge.target_node_id))

            if edge.target_node_id == node_id:
                neighbors.append(self.get_node(edge.source_node_id))

        return neighbors

    def search_nodes(
        self,
        label: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> List[KnowledgeNode]:
        """
        搜索节点

        Args:
            label: 节点标签
            properties: 属性

        Returns:
            节点列表
        """
        results = []

        for node_id, node in self.nodes.items():
            # 过滤节点标签
            if label and node.label != label:
                continue

            # 过滤属性
            if properties:
                for key, value in properties.items():
                    if key not in node.properties or node.properties[key] != value:
                        break
                else:
                    results.append(node)
                    continue

            results.append(node)

        return results

    def search_edges(
        self,
        relationship_type: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> List[KnowledgeEdge]:
        """
        搜索边

        Args:
            relationship_type: 关系类型
            properties: 属性

        Returns:
            边列表
        """
        results = []

        for edge_id, edge in self.edges.items():
            # 过滤关系类型
            if relationship_type and edge.relationship_type != relationship_type:
                continue

            # 过滤属性
            if properties:
                for key, value in properties.items():
                    if key not in edge.properties or edge.properties[key] != value:
                        break
                else:
                    results.append(edge)
                    continue

            results.append(edge)

        return results

    def get_subgraph(
        self,
        node_id: str,
        max_depth: int = 2
    ) -> 'KnowledgeGraph':
        """
        获取子图

        Args:
            node_id: 节点 ID
            max_depth: 最大深度

        Returns:
            子图
        """
        subgraph = KnowledgeGraph()
        visited = set()
        queue = [(node_id, 0)]

        while queue:
            current_node_id, depth = queue.pop(0)

            if current_node_id in visited:
                continue

            visited.add(current_node_id)

            # 获取节点
            node = self.get_node(current_node_id)
            if node:
                subgraph.add_node(node)

            # 获取邻居节点
            if depth < max_depth:
                neighbors = self.get_neighbors(current_node_id)
                for neighbor in neighbors:
                    if neighbor.node_id not in visited:
                        queue.append((neighbor.node_id, depth + 1))

        # 获取相关边
        for edge in self.edges.values():
            if edge.source_node_id in visited and edge.target_node_id in visited:
                subgraph.add_edge(edge)

        return subgraph


# 使用
knowledge_graph = KnowledgeGraph()

# 添加节点
node1 = KnowledgeNode(
    node_id="node_1",
    label="AI Agent",
    properties={
        "description": "AI Agent 是一种能够自主执行任务的 AI 系统",
        "category": "AI"
    },
    node_type="concept"
)

node2 = KnowledgeNode(
    node_id="node_2",
    label="LLM",
    properties={
        "description": "LLM 是一种大语言模型",
        "category": "AI"
    },
    node_type="concept"
)

node3 = KnowledgeNode(
    node_id="node_3",
    label="Python",
    properties={
        "description": "Python 是一种编程语言",
        "category": "编程语言"
    },
    node_type="concept"
)

knowledge_graph.add_node(node1)
knowledge_graph.add_node(node2)
knowledge_graph.add_node(node3)

# 添加边
edge1 = KnowledgeEdge(
    edge_id="edge_1",
    source_node_id="node_1",
    target_node_id="node_2",
    relationship_type="PART_OF",
    properties={"weight": 0.8}
)

edge2 = KnowledgeEdge(
    edge_id="edge_2",
    source_node_id="node_1",
    target_node_id="node_3",
    relationship_type="IMPLEMENTED_IN",
    properties={"weight": 0.7}
)

knowledge_graph.add_edge(edge1)
knowledge_graph.add_edge(edge2)

# 获取邻居节点
neighbors = knowledge_graph.get_neighbors("node_1")

print(f"节点 {node1.label} 的邻居节点：")
for neighbor in neighbors:
    print(f"- {neighbor.label}")

# 搜索节点
nodes = knowledge_graph.search_nodes(label="AI")

print(f"\n所有 AI 相关节点：")
for node in nodes:
    print(f"- {node.label}: {node.properties['description']}")
```

## 28.2 知识图谱存储

### 28.2.1 Neo4j 配置

**1. 安装 Neo4j**

```bash
# 安装 Neo4j
brew install neo4j

# 启动 Neo4j
neo4j start

# 访问 Neo4j Browser
open http://localhost:7474
```

**2. Neo4j 连接**

```python
from neo4j import GraphDatabase

class Neo4jConnection:
    """Neo4j 连接"""

    def __init__(self, uri: str, user: str, password: str):
        """
        初始化 Neo4j 连接

        Args:
            uri: 连接 URI
            user: 用户名
            password: 密码
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """关闭连接"""
        self.driver.close()

    def query(self, query: str, parameters: dict = None):
        """
        查询

        Args:
            query: 查询
            parameters: 参数

        Returns:
            结果
        """
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]


# 使用
connection = Neo4jConnection(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password"
)

# 查询
results = connection.query("MATCH (n) RETURN n LIMIT 10")

for result in results:
    print(result)

# 关闭连接
connection.close()
```

### 28.2.2 知识图谱存储实现

**1. 知识图谱存储器**

```python
# knowledge_graph/storage.py
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from neo4j import GraphDatabase
from knowledge_graph.models import KnowledgeNode, KnowledgeEdge

class KnowledgeGraphStorage:
    """知识图谱存储器"""

    def __init__(self, uri: str, user: str, password: str):
        """
        初始化知识图谱存储器

        Args:
            uri: 连接 URI
            user: 用户名
            password: 密码
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """关闭连接"""
        self.driver.close()

    def add_node(self, node: KnowledgeNode):
        """
        添加节点

        Args:
            node: 知识节点
        """
        with self.driver.session() as session:
            session.run("""
                CREATE (n:KnowledgeNode {
                    node_id: $node_id,
                    label: $label,
                    properties: $properties,
                    node_type: $node_type,
                    created_at: $created_at
                })
            """, {
                "node_id": node.node_id,
                "label": node.label,
                "properties": node.properties,
                "node_type": node.node_type,
                "created_at": node.created_at.isoformat()
            })

    def add_edge(self, edge: KnowledgeEdge):
        """
        添加边

        Args:
            edge: 知识边
        """
        with self.driver.session() as session:
            session.run("""
                MATCH (source:KnowledgeNode {node_id: $source_node_id})
                MATCH (target:KnowledgeNode {node_id: $target_node_id})
                CREATE (source)-[r:RELATIONSHIP {
                    edge_id: $edge_id,
                    relationship_type: $relationship_type,
                    properties: $properties,
                    created_at: $created_at
                }]->(target)
            """, {
                "source_node_id": edge.source_node_id,
                "target_node_id": edge.target_node_id,
                "edge_id": edge.edge_id,
                "relationship_type": edge.relationship_type,
                "properties": edge.properties,
                "created_at": edge.created_at.isoformat()
            })

    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """
        获取节点

        Args:
            node_id: 节点 ID

        Returns:
            知识节点
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:KnowledgeNode {node_id: $node_id})
                RETURN n
            """, {"node_id": node_id})

            record = result.single()

            if record is None:
                return None

            node_data = record["n"]

            return KnowledgeNode(
                node_id=node_data["node_id"],
                label=node_data["label"],
                properties=node_data["properties"],
                node_type=node_data.get("node_type", "entity"),
                created_at=datetime.fromisoformat(node_data["created_at"])
            )

    def get_edge(self, edge_id: str) -> Optional[KnowledgeEdge]:
        """
        获取边

        Args:
            edge_id: 边 ID

        Returns:
            知识边
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH ()-[r:RELATIONSHIP {edge_id: $edge_id}]->()
                RETURN r
            """, {"edge_id": edge_id})

            record = result.single()

            if record is None:
                return None

            edge_data = record["r"]

            return KnowledgeEdge(
                edge_id=edge_data["edge_id"],
                source_node_id=edge_data.start_node()["node_id"],
                target_node_id=edge_data.end_node()["node_id"],
                relationship_type=edge_data["relationship_type"],
                properties=edge_data["properties"]
            )

    def search_nodes(
        self,
        label: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> List[KnowledgeNode]:
        """
        搜索节点

        Args:
            label: 节点标签
            properties: 属性

        Returns:
            节点列表
        """
        with self.driver.session() as session:
            query = "MATCH (n:KnowledgeNode) WHERE 1=1"
            parameters = {}

            # 过滤节点标签
            if label:
                query += " AND n.label = $label"
                parameters["label"] = label

            # 过滤属性
            if properties:
                for key, value in properties.items():
                    query += f" AND n.properties.{key} = $properties_{key}"
                    parameters[f"properties_{key}"] = value

            query += " RETURN n"

            result = session.run(query, parameters)

            nodes = []
            for record in result:
                node_data = record["n"]

                nodes.append(KnowledgeNode(
                    node_id=node_data["node_id"],
                    label=node_data["label"],
                    properties=node_data["properties"],
                    node_type=node_data.get("node_type", "entity"),
                    created_at=datetime.fromisoformat(node_data["created_at"])
                ))

            return nodes

    def search_edges(
        self,
        relationship_type: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> List[KnowledgeEdge]:
        """
        搜索边

        Args:
            relationship_type: 关系类型
            properties: 属性

        Returns:
            边列表
        """
        with self.driver.session() as session:
            query = "MATCH ()-[r:RELATIONSHIP]->() WHERE 1=1"
            parameters = {}

            # 过滤关系类型
            if relationship_type:
                query += " AND r.relationship_type = $relationship_type"
                parameters["relationship_type"] = relationship_type

            # 过滤属性
            if properties:
                for key, value in properties.items():
                    query += f" AND r.properties.{key} = $properties_{key}"
                    parameters[f"properties_{key}"] = value

            query += " RETURN r"

            result = session.run(query, parameters)

            edges = []
            for record in result:
                edge_data = record["r"]

                edges.append(KnowledgeEdge(
                    edge_id=edge_data["edge_id"],
                    source_node_id=edge_data.start_node()["node_id"],
                    target_node_id=edge_data.end_node()["node_id"],
                    relationship_type=edge_data["relationship_type"],
                    properties=edge_data["properties"]
                ))

            return edges

    def get_neighbors(self, node_id: str) -> List[KnowledgeNode]:
        """
        获取邻居节点

        Args:
            node_id: 节点 ID

        Returns:
            邻居节点列表
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (source:KnowledgeNode {node_id: $node_id})-[:RELATIONSHIP]->(target:KnowledgeNode)
                RETURN target
            """, {"node_id": node_id})

            neighbors = []
            for record in result:
                node_data = record["target"]

                neighbors.append(KnowledgeNode(
                    node_id=node_data["node_id"],
                    label=node_data["label"],
                    properties=node_data["properties"],
                    node_type=node_data.get("node_type", "entity"),
                    created_at=datetime.fromisoformat(node_data["created_at"])
                ))

            return neighbors

    def delete_node(self, node_id: str):
        """
        删除节点

        Args:
            node_id: 节点 ID
        """
        with self.driver.session() as session:
            session.run("""
                MATCH (n:KnowledgeNode {node_id: $node_id})
                DETACH DELETE n
            """, {"node_id": node_id})

    def delete_edge(self, edge_id: str):
        """
        删除边

        Args:
            edge_id: 边 ID
        """
        with self.driver.session() as session:
            session.run("""
                MATCH ()-[r:RELATIONSHIP {edge_id: $edge_id}]->()
                DELETE r
            """, {"edge_id": edge_id})


# 使用
storage = KnowledgeGraphStorage(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password"
)

# 添加节点
node = KnowledgeNode(
    node_id=str(uuid.uuid4()),
    label="AI Agent",
    properties={
        "description": "AI Agent 是一种能够自主执行任务的 AI 系统",
        "category": "AI"
    },
    node_type="concept"
)

storage.add_node(node)

# 搜索节点
nodes = storage.search_nodes(label="AI")

for node in nodes:
    print(f"节点：{node.label}")
    print(f"描述：{node.properties['description']}")
    print()

# 关闭连接
storage.close()
```

## 28.3 知识图谱检索

### 28.3.1 知识图谱检索器

**1. 知识图谱检索器**

```python
# knowledge_graph/retriever.py
from typing import Dict, Any, List, Optional
from knowledge_graph.storage import KnowledgeGraphStorage
from knowledge_graph.models import KnowledgeNode, KnowledgeEdge

class KnowledgeGraphRetriever:
    """知识图谱检索器"""

    def __init__(self, storage: KnowledgeGraphStorage):
        """
        初始化知识图谱检索器

        Args:
            storage: 知识图谱存储器
        """
        self.storage = storage

    def retrieve(
        self,
        query: str,
        max_depth: int = 2
    ) -> List[KnowledgeNode]:
        """
        检索知识

        Args:
            query: 查询
            max_depth: 最大深度

        Returns:
            知识节点列表
        """
        # 搜索节点
        nodes = self.storage.search_nodes(properties={"label": query})

        # 获取子图
        results = []
        for node in nodes:
            subgraph = self.storage.get_subgraph(node.node_id, max_depth)

            # 获取所有节点
            for subgraph_node in subgraph.nodes.values():
                if subgraph_node.node_id not in [n.node_id for n in results]:
                    results.append(subgraph_node)

        return results

    def retrieve_by_type(
        self,
        node_type: str,
        max_depth: int = 2
    ) -> List[KnowledgeNode]:
        """
        按类型检索知识

        Args:
            node_type: 节点类型
            max_depth: 最大深度

        Returns:
            知识节点列表
        """
        # 搜索节点
        nodes = self.storage.search_nodes(node_type=node_type)

        # 获取子图
        results = []
        for node in nodes:
            subgraph = self.storage.get_subgraph(node.node_id, max_depth)

            # 获取所有节点
            for subgraph_node in subgraph.nodes.values():
                if subgraph_node.node_id not in [n.node_id for n in results]:
                    results.append(subgraph_node)

        return results

    def get_path(
        self,
        source_node_id: str,
        target_node_id: str,
        max_depth: int = 5
    ) -> List[KnowledgeNode]:
        """
        获取路径

        Args:
            source_node_id: 源节点 ID
            target_node_id: 目标节点 ID
            max_depth: 最大深度

        Returns:
            路径列表
        """
        with self.storage.driver.session() as session:
            result = session.run("""
                MATCH path = shortestPath(
                    (source:KnowledgeNode {node_id: $source_node_id})-[*1..$max_depth]-(target:KnowledgeNode {node_id: $target_node_id})
                )
                RETURN [node IN nodes(path) | node]
            """, {
                "source_node_id": source_node_id,
                "target_node_id": target_node_id,
                "max_depth": max_depth
            })

            records = result.single()

            if records is None:
                return []

            # 转换为节点列表
            path = []
            for node_data in records[0]:
                path.append(KnowledgeNode(
                    node_id=node_data["node_id"],
                    label=node_data["label"],
                    properties=node_data["properties"],
                    node_type=node_data.get("node_type", "entity"),
                    created_at=datetime.fromisoformat(node_data["created_at"])
                ))

            return path


# 使用
storage = KnowledgeGraphStorage(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password"
)

retriever = KnowledgeGraphRetriever(storage)

# 检索知识
results = retriever.retrieve("AI", max_depth=2)

print(f"AI 相关知识：")
for node in results:
    print(f"- {node.label}: {node.properties.get('description', '')}")

# 关闭连接
storage.close()
```

## 28.4 本章总结

### 核心要点

1. **知识图谱设计**: 知识图谱架构、知识节点、知识边
2. **知识图谱存储**: Neo4j 配置、知识图谱存储器
3. **知识图谱检索**: 知识图谱检索器、路径查询

### 实战技巧

- **知识图谱设计**: 使用节点表示实体，使用边表示关系，使用属性存储数据
- **知识图谱存储**: 使用 Neo4j 存储知识图谱，支持复杂查询
- **知识图谱检索**: 使用图遍历算法检索知识，使用最短路径算法查询路径

### 练习题

1. 实现知识图谱节点
2. 实现知识图谱边
3. 实现知识图谱存储器
4. 实现知识图谱检索器

### 下章预告

第29章将介绍 **Agent 知识推理**，包括：
- 知识推理概述
- 知识推理算法
- 知识推理应用

---

**本章完**

**下一章**: [第29章：Agent 知识推理](./29-chapter28-knowledge-reasoning.md)
