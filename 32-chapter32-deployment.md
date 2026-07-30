# 第32章：Agent 系统部署实战

## 本章目标

通过实战项目，掌握 Agent 系统部署的最佳实践。

## 前置知识

- **基础 部署**: Docker、K8s
- **基础 Agent**: Harness、Loop、Graph
- **基础 项目**: 项目结构、代码组织

## 32.1 部署概述

### 32.1.1 部署概述

**1. 部署类型**

| 部署类型 | 说明 | 用途 |
|---------|------|------|
| **本地部署** | 本地服务器部署 | 开发、测试 |
| **云部署** | 云服务器部署 | 生产环境 |
| **容器部署** | Docker 容器部署 | 跨平台部署 |
| **容器编排部署** | K8s 容器编排部署 | 大规模部署 |

**2. 部署流程**

```
┌─────────────────────────────────────────────────────────┐
│                    部署流程                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  部署准备                          │  │
│  │  - 环境准备                                        │  │
│  │  - 配置准备                                        │  │
│  │  - 依赖准备                                        │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  部署实施                          │  │
│  │  - 构建镜像                                        │  │
│  │  - 部署应用                                        │  │
│  │  - 配置服务                                        │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  部署验证                          │  │
│  │  - 功能验证                                        │  │
│  │  - 性能验证                                        │  │
│  │  - 监控验证                                        │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  部署维护                          │  │
│  │  - 日志监控                                        │  │
│  │  - 性能监控                                        │  │
│  │  - 故障恢复                                        │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 32.1.2 部署环境

**1. 环境类型**

| 环境类型 | 说明 | 用途 |
|---------|------|------|
| **开发环境** | 开发者本地环境 | 开发、调试 |
| **测试环境** | 测试服务器环境 | 测试、验证 |
| **预发布环境** | 预发布服务器环境 | 预发布、验收 |
| **生产环境** | 生产服务器环境 | 生产、运营 |

**2. 环境配置**

| 环境变量 | 开发环境 | 测试环境 | 预发布环境 | 生产环境 |
|---------|---------|---------|-----------|---------|
| **数据库** | 本地数据库 | 测试数据库 | 预发布数据库 | 生产数据库 |
| **Redis** | 本地Redis | 测试Redis | 预发布Redis | 生产Redis |
| **日志级别** | DEBUG | INFO | INFO | WARN |
| **监控** | 无 | Prometheus | Prometheus | Prometheus |

## 32.2 Docker 部署实战

### 32.2.1 Dockerfile 编写

**1. 后端 Dockerfile**

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

**2. 前端 Dockerfile**

```dockerfile
# 使用 Node.js 基础镜像
FROM node:18-alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 使用 Nginx 作为生产服务器
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动命令
CMD ["nginx", "-g", "daemon off;"]
```

**3. Nginx 配置**

```nginx
# nginx.conf
server {
    listen 80;
    server_name localhost;

    # 前端
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 32.2.2 Docker Compose 编写

**1. docker-compose.yml**

```yaml
version: '3.8'

services:
  # PostgreSQL 数据库
  postgres:
    image: postgres:16-alpine
    container_name: agent_framework_postgres
    environment:
      POSTGRES_DB: agent_framework
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - agent_framework_network

  # Redis 缓存
  redis:
    image: redis:7-alpine
    container_name: agent_framework_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - agent_framework_network

  # 后端服务
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: agent_framework_backend
    environment:
      DATABASE_URL: postgresql://user:***@postgres:5432/agent_framework
      REDIS_URL: redis://redis:***@redis:6379
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    networks:
      - agent_framework_network

  # 前端服务
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: agent_framework_frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - agent_framework_network

networks:
  agent_framework_network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

**2. 启动项目**

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止所有服务
docker-compose down

# 停止所有服务并删除数据
docker-compose down -v
```

**3. 运行测试**

```bash
# 运行测试
docker-compose exec backend pytest tests/

# 生成覆盖率报告
docker-compose exec backend pytest --cov=app tests/

# 查看覆盖率报告
docker-compose exec backend open htmlcov/index.html
```

### 32.2.3 Docker 部署实战

**1. 构建镜像**

```bash
# 构建后端镜像
docker-compose build backend

# 构建前端镜像
docker-compose build frontend

# 构建所有镜像
docker-compose build
```

**2. 推送镜像**

```bash
# 标记镜像
docker tag agent_framework_backend:latest username/agent_framework_backend:latest
docker tag agent_framework_frontend:latest username/agent_framework_frontend:latest

# 推送镜像
docker push username/agent_framework_backend:latest
docker push username/agent_framework_frontend:latest
```

**3. 生产部署**

```bash
# 拉取镜像
docker pull username/agent_framework_backend:latest
docker pull username/agent_framework_frontend:latest

# 启动服务
docker-compose up -d
```

## 32.3 K8s 部署实战

### 32.3.1 Kubernetes 配置

**1. Secret 配置**

```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: agent-framework-secrets
type: Opaque
stringData:
  database-url: "postgresql://user:***@postgres:5432/agent_framework"
  redis-url: "redis://redis:***@redis:6379"
  jwt-secret-key: "your-secret-key"
  openai-api-key: "your-openai-api-key"
```

**2. ConfigMap 配置**

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: agent-framework-config
data:
  jwt-algorithm: "HS256"
  jwt-expires-hours: "24"
  log-level: "INFO"
```

**3. Deployment 配置**

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-framework-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agent-framework-backend
  template:
    metadata:
      labels:
        app: agent-framework-backend
    spec:
      containers:
      - name: backend
        image: username/agent-framework-backend:latest
        ports:
        - containerPort: 8000
        envFrom:
        - secretRef:
            name: agent-framework-secrets
        - configMapRef:
            name: agent-framework-config
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

**4. Service 配置**

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: agent-framework-backend
spec:
  selector:
    app: agent-framework-backend
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: ClusterIP
```

**5. Ingress 配置**

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: agent-framework-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: agent-framework.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: agent-framework-frontend
            port:
              number: 80
```

### 32.3.2 K8s 部署实战

**1. 创建命名空间**

```bash
# 创建命名空间
kubectl create namespace agent-framework
```

**2. 应用配置**

```bash
# 应用 Secret
kubectl apply -f secrets.yaml -n agent-framework

# 应用 ConfigMap
kubectl apply -f configmap.yaml -n agent-framework

# 应用 Deployment
kubectl apply -f deployment.yaml -n agent-framework

# 应用 Service
kubectl apply -f service.yaml -n agent-framework

# 应用 Ingress
kubectl apply -f ingress.yaml -n agent-framework
```

**3. 查看部署状态**

```bash
# 查看 Pod 状态
kubectl get pods -n agent-framework

# 查看日志
kubectl logs -f deployment/agent-framework-backend -n agent-framework

# 查看服务
kubectl get svc -n agent-framework

# 查看 Ingress
kubectl get ingress -n agent-framework
```

**4. 扩容和缩容**

```bash
# 扩容副本数
kubectl scale deployment agent-framework-backend --replicas=5 -n agent-framework

# 缩容副本数
kubectl scale deployment agent-framework-backend --replicas=2 -n agent-framework
```

**5. 滚动更新**

```bash
# 更新镜像
kubectl set image deployment/agent-framework-backend backend=username/agent-framework-backend:v1.1.0 -n agent-framework

# 查看滚动更新状态
kubectl rollout status deployment/agent-framework-backend -n agent-framework

# 回滚到上一个版本
kubectl rollout undo deployment/agent-framework-backend -n agent-framework
```

### 32.3.3 K8s 监控

**1. Prometheus 配置**

```yaml
# prometheus-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s

    scrape_configs:
    - job_name: 'agent-framework-backend'
      kubernetes_sd_configs:
      - role: pod
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: agent-framework-backend
      - source_labels: [__meta_kubernetes_pod_ip]
        target_label: __address__
        replacement: $1:8000
```

**2. Grafana 配置**

```yaml
# grafana-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:latest
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          value: "admin"
        volumeMounts:
        - name: grafana-storage
          mountPath: /var/lib/grafana
      volumes:
      - name: grafana-storage
        emptyDir: {}
```

## 32.4 CI/CD 实战

### 32.4.1 GitHub Actions

**1. .github/workflows/deploy.yml**

```yaml
name: Deploy

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install docker-compose

    - name: Build Docker images
      run: |
        docker-compose build

    - name: Push Docker images
      env:
        DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
        DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
      run: |
        docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD
        docker-compose push

    - name: Deploy to K8s
      run: |
        kubectl set image deployment/agent-framework-backend backend=username/agent-framework-backend:latest -n agent-framework
        kubectl rollout status deployment/agent-framework-backend -n agent-framework
```

### 32.4.2 GitLab CI

**1. .gitlab-ci.yml**

```yaml
deploy:
  stage: deploy
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker-compose build
    - docker-compose push
    - kubectl set image deployment/agent-framework-backend backend=$CI_REGISTRY_IMAGE/backend:latest -n agent-framework
    - kubectl rollout status deployment/agent-framework-backend -n agent-framework
  only:
    - main
```

## 32.5 本章总结

### 核心要点

1. **部署概述**: 部署类型、部署流程、部署环境
2. **Docker 部署实战**: Dockerfile 编写、Docker Compose 编写、Docker 部署实战
3. **K8s 部署实战**: Kubernetes 配置、K8s 部署实战、K8s 监控
4. **CI/CD 实战**: GitHub Actions、GitLab CI

### 实战技巧

- **Docker 部署**: 使用多阶段构建优化镜像大小、使用健康检查、使用资源限制
- **K8s 部署**: 使用 Secret 和 ConfigMap 管理敏感配置、使用健康检查、使用资源限制
- **监控**: 使用 Prometheus 收集指标、使用 Grafana 可视化、使用日志聚合
- **CI/CD**: 使用 GitHub Actions 或 GitLab CI 实现自动化部署

### 练习题

1. 编写 Dockerfile
2. 编写 Docker Compose 配置
3. 编写 Kubernetes 配置
4. 配置 CI/CD 流程

---

**本章完**

**全书完**

---

## 📚 附录

### 附录 A：完整代码示例

**A.1 Agent 基础类**

```python
# agent_framework/agent.py
from typing import Dict, Any, Optional

class Agent:
    """Agent 基础类"""

    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str
    ):
        """
        初始化 Agent

        Args:
            agent_id: Agent ID
            name: Agent 名称
            description: Agent 描述
        """
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.is_stopped = False

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        执行任务

        Args:
            task: 任务
            context: 上下文

        Returns:
            结果
        """
        if self.is_stopped:
            raise RuntimeError("Agent 已停止")

        return f"{self.name} 执行任务：{task}"

    def stop(self):
        """停止 Agent"""
        self.is_stopped = True

    def is_stopped(self) -> bool:
        """
        检查 Agent 是否停止

        Returns:
            是否停止
        """
        return self.is_stopped
```

**A.2 Harness 工具类**

```python
# agent_framework/harness.py
from typing import Dict, Any

class ToolRegistry:
    """工具注册器"""

    def __init__(self):
        """初始化工具注册器"""
        self.tools = {}

    def register_tool(self, tool):
        """注册工具"""
        self.tools[tool.name] = tool

    def get_tool(self, tool_name: str):
        """获取工具"""
        return self.tools.get(tool_name)

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """
        执行工具

        Args:
            tool_name: 工具名称
            kwargs: 工具参数

        Returns:
            工具执行结果
        """
        tool = self.get_tool(tool_name)

        if tool is None:
            raise ValueError(f"工具 {tool_name} 不存在")

        return tool.execute(**kwargs)


class Tool:
    """工具基类"""

    def __init__(self, name: str, description: str):
        """
        初始化工具

        Args:
            name: 工具名称
            description: 工具描述
        """
        self.name = name
        self.description = description

    def execute(self, **kwargs) -> Any:
        """
        执行工具

        Args:
            kwargs: 工具参数

        Returns:
            工具执行结果
        """
        raise NotImplementedError


class GetWeatherTool(Tool):
    """获取天气工具"""

    def __init__(self):
        """初始化工具"""
        super().__init__(
            name="get_weather",
            description="获取指定城市的天气"
        )

    def execute(self, city: str) -> str:
        """
        执行工具

        Args:
            city: 城市

        Returns:
            天气信息
        """
        return f"{city} 的天气是晴天，温度 25°C"
```

**A.3 Graph 图结构类**

```python
# agent_framework/graph.py
from typing import Dict, Any, List, Optional

class Node:
    """节点"""

    def __init__(
        self,
        node_id: str,
        agent,
        position: Optional[tuple] = None
    ):
        """
        初始化节点

        Args:
            node_id: 节点 ID
            agent: Agent 实例
            position: 位置
        """
        self.node_id = node_id
        self.agent = agent
        self.position = position

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "node_id": self.node_id,
            "agent_id": self.agent.agent_id,
            "position": self.position
        }


class Edge:
    """边"""

    def __init__(
        self,
        from_node: str,
        to_node: str,
        weight: float = 1.0
    ):
        """
        初始化边

        Args:
            from_node: 源节点
            to_node: 目标节点
            weight: 权重
        """
        self.from_node = from_node
        self.to_node = to_node
        self.weight = weight

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "from_node": self.from_node,
            "to_node": self.to_node,
            "weight": self.weight
        }


class Graph:
    """图"""

    def __init__(self):
        """初始化图"""
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []

    def add_node(self, node: Node):
        """添加节点"""
        self.nodes[node.node_id] = node

    def add_edge(self, edge: Edge):
        """添加边"""
        self.edges.append(edge)

    def execute(self) -> str:
        """执行图"""
        results = []

        for node in self.nodes.values():
            result = node.agent.execute("执行任务")
            results.append(result)

        return "\n".join(results)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges]
        }
```

### 附录 B：最佳实践清单

**B.1 Agent 开发最佳实践**

- [ ] 使用统一的 Agent 接口
- [ ] 使用 Harness 管理工具
- [ ] 使用 Graph 组织 Agent
- [ ] 使用 Loop 控制执行流程
- [ ] 使用 Memory 管理记忆
- [ ] 使用 KnowledgeGraph 管理知识
- [ ] 编写单元测试
- [ ] 编写文档

**B.2 Agent 部署最佳实践**

- [ ] 使用 Docker 容器化
- [ ] 使用 K8s 编排
- [ ] 配置健康检查
- [ ] 配置资源限制
- [ ] 配置监控
- [ ] 配置日志
- [ ] 配置备份
- [ ] 配置容灾

**B.3 Agent 安全最佳实践**

- [ ] 使用 JWT 认证
- [ ] 使用 RBAC 授权
- [ ] 使用加密存储敏感数据
- [ ] 使用输入验证
- [ ] 使用输出过滤
- [ ] 使用审计日志
- [ ] 使用 HTTPS
- [ ] 使用限流

### 附录 C：常见问题

**C.1 开发问题**

**Q: 如何选择 Agent 架构？**

A: 根据 Agent 的复杂度和需求选择：
- 简单 Agent：使用 Agent 类
- 需要工具调用：使用 Harness
- 需要编排：使用 Graph
- 需要循环控制：使用 Loop

**Q: 如何优化 Agent 性能？**

A: 优化方法：
- 使用缓存
- 使用异步编程
- 使用对象池
- 优化算法
- 优化数据库查询

**C.2 部署问题**

**Q: 如何处理配置管理？**

A: 使用 ConfigMap 和 Secret 管理 K8s 配置，使用环境变量管理 Docker 配置。

**Q: 如何处理数据库迁移？**

A: 使用数据库迁移工具（如 Alembic），在部署前进行迁移。

**C.3 安全问题**

**Q: 如何防止 SQL 注入？**

A: 使用 ORM 或参数化查询，避免直接拼接 SQL。

**Q: 如何防止 XSS 攻击？**

A: 使用输出编码，使用 CSP 策略。

### 附录 D：资源链接

**D.1 学习资源**

- [Agent 框架文档](https://agent-framework.nousresearch.com/docs)
- [Docker 文档](https://docs.docker.com/)
- [Kubernetes 文档](https://kubernetes.io/docs/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)

**D.2 工具资源**

- [Pydantic](https://docs.pydantic.dev/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Docker](https://www.docker.com/)
- [Kubernetes](https://kubernetes.io/)

**D.3 社区资源**

- [GitHub](https://github.com/)
- [Stack Overflow](https://stackoverflow.com/)
- [Reddit](https://www.reddit.com/)

---

**感谢阅读！**

**祝您开发顺利！**
