# 第24章：Agent 部署实战

## 本章目标

通过实战项目，掌握 Agent 部署的最佳实践。

## 前置知识

- **基础 部署**: Docker、K8s
- **基础 Agent**: Harness、Loop、Graph
- **基础 项目**: 项目结构、代码组织

## 24.1 Docker 部署实战

### 24.1.1 Dockerfile 编写

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

### 24.1.2 Docker Compose 编写

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

### 24.1.3 Docker 部署实战

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

## 24.2 K8s 部署实战

### 24.2.1 Kubernetes 配置

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

### 24.2.2 K8s 部署实战

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

### 24.2.3 K8s 监控

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

## 24.3 监控与日志实战

### 24.3.1 Prometheus 监控

**1. 安装 Prometheus**

```bash
# 创建命名空间
kubectl create namespace monitoring

# 应用 Prometheus 配置
kubectl apply -f prometheus-config.yaml -n monitoring

# 应用 Prometheus Deployment
kubectl apply -f prometheus-deployment.yaml -n monitoring
```

**2. Grafana 仪表板**

```yaml
# grafana-dashboard.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboard
  namespace: monitoring
data:
  agent-framework-dashboard.json: |
    {
      "dashboard": {
        "title": "Agent Framework Dashboard",
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
            "title": "Response Time",
            "targets": [
              {
                "expr": "rate(http_request_duration_seconds_sum[1m]) / rate(http_request_duration_seconds_count[1m])"
              }
            ]
          },
          {
            "title": "Error Rate",
            "targets": [
              {
                "expr": "rate(http_requests_total{status=~\"5..\"}[1m])"
              }
            ]
          }
        ]
      }
    }
```

### 24.3.2 日志管理

**1. Fluentd 配置**

```yaml
# fluentd-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/agent_framework.log
      <parse>
        @type json
      </parse>
      tag agent_framework
    </source>

    <match agent_framework>
      @type elasticsearch
      host elasticsearch
      port 9200
      logstash_format true
      logstash_prefix agent_framework
    </match>
```

**2. Elasticsearch 配置**

```yaml
# elasticsearch.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: elasticsearch
spec:
  serviceName: elasticsearch
  replicas: 3
  selector:
    matchLabels:
      app: elasticsearch
  template:
    metadata:
      labels:
        app: elasticsearch
    spec:
      containers:
      - name: elasticsearch
        image: elasticsearch:8.11.0
        ports:
        - containerPort: 9200
        env:
        - name: discovery.type
          value: single-node
```

## 24.4 本章总结

### 核心要点

1. **Docker 部署实战**: Dockerfile 编写、Docker Compose 编写、Docker 部署实战
2. **K8s 部署实战**: Kubernetes 配置、K8s 部署实战、K8s 监控
3. **监控与日志实战**: Prometheus 监控、Grafana 仪表板、日志管理

### 实战技巧

- **Docker 部署**: 使用多阶段构建优化镜像大小、使用健康检查、使用资源限制
- **K8s 部署**: 使用 Secret 和 ConfigMap 管理敏感配置、使用健康检查、使用资源限制
- **监控**: 使用 Prometheus 收集指标、使用 Grafana 可视化、使用日志聚合

### 练习题

1. 编写 Dockerfile
2. 编写 Docker Compose 配置
3. 编写 Kubernetes 配置
4. 配置 Prometheus 监控

### 下章预告

第25章将介绍 **Agent 应用拓展**，包括：
- Agent 在金融领域的应用
- Agent 在医疗领域的应用
- Agent 在教育领域的应用

---

**本章完**

**下一章**: [第25章：Agent 应用拓展](./25-chapter24-deployment-practice.md)
