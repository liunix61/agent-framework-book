# 第12章：Agent 系统部署

## 本章目标

掌握 Agent 系统部署方法，包括部署架构、Docker 部署、K8s 部署、监控与日志。

## 前置知识

- **基础 Docker**: Dockerfile、docker-compose
- **基础 K8s**: Deployment、Service、Ingress
- **基础 监控**: Prometheus、Grafana

## 12.1 部署架构

### 12.1.1 Agent 系统架构

**Agent 系统部署架构**:

```
┌─────────────────────────────────────────────────────────┐
│                    Agent 系统架构                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  客户端层                          │  │
│  │  - Web 前端（Vue3/Nuxt4）                          │  │
│  │  - 移动端（uni-app）                               │  │
│  │  - CLI 工具                                        │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↓ HTTP/WebSocket                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  网关层                            │  │
│  │  - API 网关（Nginx）                               │  │
│  │  - 负载均衡                                        │  │
│  │  - 认证授权                                        │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  应用层                            │  │
│  │  - Agent 服务                                      │  │
│  │  - 工具服务                                        │  │
│  │  - 知识库服务                                      │  │
│  │  - 协议栈服务                                      │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  数据层                            │  │
│  │  - PostgreSQL（数据库）                            │  │
│  │  - Redis（缓存）                                    │  │
│  │  - Neo4j（知识图谱）                                │  │
│  │  - ChromaDB（向量数据库）                          │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 12.1.2 部署方式对比

| 部署方式 | 特点 | 适用场景 | 优点 | 缺点 |
|---------|------|---------|------|------|
| **单机部署** | 所有服务在同一台机器 | 开发、测试、小规模应用 | 简单、成本低 | 可扩展性差 |
| **Docker 部署** | 容器化部署 | 中小规模应用 | 隔离、易移植 | 资源占用高 |
| **K8s 部署** | 容器编排部署 | 大规模生产环境 | 高可用、可扩展 | 复杂、成本高 |

## 12.2 Docker 部署

### 12.2.1 Dockerfile

**Agent 系统后端 Dockerfile**:

```dockerfile
# 使用 Python 3.11 基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非 root 用户
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**前端 Dockerfile**:

```dockerfile
FROM node:18-alpine as builder

WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制源代码
COPY . .

# 构建
RUN npm run build

# 生产环境镜像
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 12.2.2 docker-compose.yml

**完整的 docker-compose.yml**:

```yaml
version: '3.8'

services:
  # PostgreSQL 数据库
  postgres:
    image: postgres:16-alpine
    container_name: agent_postgres
    environment:
      POSTGRES_DB: agent_db
      POSTGRES_USER: agent_user
      POSTGRES_PASSWORD: agent_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U agent_user -d agent_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis 缓存
  redis:
    image: redis:7-alpine
    container_name: agent_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Neo4j 知识图谱
  neo4j:
    image: neo4j:5.16.0
    container_name: agent_neo4j
    environment:
      NEO4J_AUTH: neo4j/neo4j_password
      NEO4J_dbms_memory_pagecache_size: 1G
      NEO4J_dbms_memory_heap_initial__size: 512M
      NEO4J_dbms_memory_heap_max__size: 1G
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    volumes:
      - neo4j_data:/data
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:7474 || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ChromaDB 向量数据库
  chromadb:
    image: chromadb/chroma:latest
    container_name: agent_chromadb
    ports:
      - "8000:8000"
    volumes:
      - chromadb_data:/chroma/chroma

  # Agent 后端
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: agent_backend
    environment:
      DATABASE_URL: postgresql://agent_user:agent_password@postgres:5432/agent_db
      REDIS_URL: redis://redis:6379/0
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_USER: neo4j
      NEO4J_PASSWORD: neo4j_password
      CHROMA_HOST: chromadb:8000
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      neo4j:
        condition: service_healthy
      chromadb:
        condition: service_started
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # Agent 前端
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: agent_frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
  neo4j_data:
  chromadb_data:
```

### 12.2.3 启动部署

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend

# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v

# 重新构建并启动
docker-compose up -d --build
```

## 12.3 K8s 部署

### 12.3.1 K8s 配置

**Agent 后端 Deployment**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-backend
  labels:
    app: agent-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agent-backend
  template:
    metadata:
      labels:
        app: agent-backend
    spec:
      containers:
      - name: backend
        image: agent-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: agent-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: agent-secrets
              key: redis-url
        - name: NEO4J_URI
          valueFrom:
            secretKeyRef:
              name: agent-secrets
              key: neo4j-uri
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: agent-backend
spec:
  selector:
    app: agent-backend
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: ClusterIP
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: agent-config
data:
  ENV: "production"
  LOG_LEVEL: "info"
---
apiVersion: v1
kind: Secret
metadata:
  name: agent-secrets
type: Opaque
stringData:
  database-url: postgresql://agent_user:agent_password@postgres:5432/agent_db
  redis-url: redis://redis-service:6379/0
  neo4j-uri: bolt://neo4j-service:7687
```

**Agent 前端 Deployment**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-frontend
  labels:
    app: agent-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: agent-frontend
  template:
    metadata:
      labels:
        app: agent-frontend
    spec:
      containers:
      - name: frontend
        image: agent-frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "128Mi"
            cpu: "200m"
          limits:
            memory: "256Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: agent-frontend
spec:
  selector:
    app: agent-frontend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: ClusterIP
```

**Ingress 配置**:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: agent-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - agent.example.com
    secretName: agent-tls
  rules:
  - host: agent.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: agent-frontend
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: agent-backend
            port:
              number: 8000
```

### 12.3.2 部署命令

```bash
# 应用 K8s 配置
kubectl apply -f agent-deployment.yaml

# 查看 Deployment
kubectl get deployments

# 查看 Pods
kubectl get pods

# 查看 Services
kubectl get services

# 查看日志
kubectl logs -f deployment/agent-backend

# 扩容
kubectl scale deployment agent-backend --replicas=5

# 滚动更新
kubectl set image deployment/agent-backend backend=agent-backend:v2.0

# 回滚
kubectl rollout undo deployment/agent-backend

# 删除
kubectl delete -f agent-deployment.yaml
```

## 12.4 监控与日志

### 12.4.1 Prometheus 配置

**prometheus.yml**:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  # Agent 后端监控
  - job_name: 'agent-backend'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: agent-backend
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod
      - source_labels: [__meta_kubernetes_namespace]
        target_label: namespace

  # Node Exporter 监控
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']

  # Redis 监控
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### 12.4.2 Grafana 仪表盘

**关键监控指标**:

| 指标 | 说明 | 告警阈值 |
|------|------|---------|
| **QPS** | 每秒请求数 | > 1000 |
| **响应时间 (P95)** | 95% 请求的响应时间 | > 1s |
| **错误率** | 错误请求占比 | > 1% |
| **CPU 使用率** | CPU 使用率 | > 80% |
| **内存使用率** | 内存使用率 | > 85% |
| **Pod 重启次数** | Pod 重启次数 | > 3次/小时 |

**Grafana 仪表盘 JSON**:

```json
{
  "dashboard": {
    "title": "Agent System Dashboard",
    "panels": [
      {
        "title": "QPS",
        "targets": [
          {
            "expr": "rate(http_requests_total[1m])"
          }
        ]
      },
      {
        "title": "Response Time (P95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[1m]) / rate(http_requests_total[1m])"
          }
        ]
      }
    ]
  }
}
```

### 12.4.3 日志管理

**Fluentd 配置**:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/agent/*.log
      pos_file /var/log/agent/fluentd.log.pos
      tag agent.*
      <parse>
        @type json
      </parse>
    </source>

    <match agent.**>
      @type elasticsearch
      host elasticsearch
      port 9200
      logstash_format true
      logstash_prefix agent
    </match>
```

**日志查询示例**:

```bash
# 查询错误日志
kubectl logs deployment/agent-backend --tail=100 | grep ERROR

# 实时查看日志
kubectl logs -f deployment/agent-backend

# 查询特定 Pod 的日志
kubectl logs <pod-name> --tail=50

# 查询特定时间段的日志
kubectl logs <pod-name> --since=1h
```

## 12.5 本章总结

### 核心要点

1. **部署架构**: 客户端层、网关层、应用层、数据层
2. **Docker 部署**: Dockerfile、docker-compose、启动命令
3. **K8s 部署**: Deployment、Service、Ingress、ConfigMap、Secret
4. **监控**: Prometheus、Grafana、关键指标
5. **日志**: Fluentd、日志查询

### 实战技巧

- **Docker 部署**: 使用 docker-compose 简化部署
- **K8s 部署**: 使用 ConfigMap 和 Secret 管理配置
- **监控**: 关注 QPS、响应时间、错误率
- **日志**: 使用 ELK Stack 管理日志

### 练习题

1. 编写 Dockerfile 部署 Agent 系统后端
2. 编写 docker-compose.yml 文件
3. 编写 K8s Deployment 配置
4. 配置 Prometheus 监控 Agent 系统

### 下章预告

第13章将介绍 **Agent 安全**，包括：
- Agent 安全威胁
- 认证与授权
- 数据加密
- 安全最佳实践

---

**本章完**

**下一章**: [第13章：Agent 安全](./13-chapter13-security.md)
