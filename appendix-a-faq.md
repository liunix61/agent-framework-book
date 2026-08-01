#| 附录A：常见问题与解决方案

## A.1 Agent 框架开发常见问题

### Q1: 如何选择 Agent 框架？

**答**：根据项目需求选择：
- **企业级平台**：Agent Admin、OPCOS（多租户、权限控制）
- **多模态框架**：UniAgents（DAG编排、三层记忆）
- **写作平台**：MindFlow（10个Agent、14个Core模块）
- **量化交易**：QuantFlow（策略→风控→交易）

### Q2: Python 和 C++ Agent 开发的区别？

| 维度 | Python | C++ |
|------|--------|-----|
| **性能** | 中等（GIL限制） | 极高（无GIL、零分配） |
| **开发效率** | 高（快速迭代） | 中（需要内存管理） |
| **适用场景** | Web后端、数据分析、快速原型 | 低延迟系统、高频交易、游戏引擎 |
| **内存安全** | 依赖GC | 需手动管理 |

### Q3: 如何设计 Agent 的记忆系统？

**答**：三层记忆架构：
1. **短期记忆**：上下文窗口、对话历史
2. **中期记忆**：FTS5全文搜索、LLM摘要
3. **长期记忆**：向量数据库、知识图谱

示例：
```python
# 添加记忆
memory.add("用户喜欢简洁的回答")

# 检索记忆
context = memory.search("回答风格偏好")
```

### Q4: 如何处理多 Agent 协作？

**答**：推荐模式：
- **Pipeline模式**：顺序执行（如 MindFlow 写作流程）
- **Roundtable模式**：多 Agent 讨论（如辩论、评审）
- **Swarm模式**：分布式协作（如 QuantFlow 交易网络）

### Q5: 如何保证 Agent 的安全性？

**答**：多层次安全策略：
1. **权限控制**：基于角色的访问控制（RBAC）
2. **命令审批**：敏感操作需用户确认
3. **容器隔离**：Docker容器运行 Agent
4. **输入验证**：严格验证所有用户输入

## A.2 常见错误与解决方案

### 错误1：数据库连接失败

**症状**：
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**原因**：
- PostgreSQL 未启动
- 连接参数错误（host、port、database）

**解决方案**：
```bash
# 检查 PostgreSQL 状态
pg_ctl status -D /path/to/data

# 启动 PostgreSQL
pg_ctl -D /path/to/data start

# 检查连接参数
psql -h localhost -p 5433 -U postgres -d agent_admin
```

### 错误2：异步函数调用错误

**症状**：
```
RuntimeError: no running event loop
```

**原因**：
- 在同步函数中调用 await，但事件循环未运行

**解决方案**：
```python
# 正确：在异步函数中使用 await
async def process():
    result = await async_operation()

# 错误：在同步函数中使用 await
def process():
    result = await async_operation()  # 错误
```

### 错误3：测试失败率过高

**症状**：
```
pytest --tb=short
282 passed, 98 failed, 7 errors
```

**原因**：
- 数据库表结构不一致
- 测试数据污染
- 硬编码值错误

**解决方案**：
```bash
# 1. 重置数据库
make reset_db

# 2. 清理测试缓存
rm -rf .pytest_cache

# 3. 重新运行测试
pytest --tb=short -v

# 4. 查看覆盖率
pytest --cov=src --cov-report=html
```

## A.3 性能优化技巧

### 1. 数据库查询优化

```python
# 低效：N+1查询
for user in users:
    orders = session.query(Order).filter_by(user_id=user.id).all()

# 高效：批量查询
user_ids = [u.id for u in users]
orders = session.query(Order).filter(Order.user_id.in_(user_ids)).all()
```

### 2. 缓存策略

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_user_config(user_id: int) -> dict:
    return db.query(UserConfig).filter_by(id=user_id).first()
```

### 3. 异步IO优化

```python
# 同步IO阻塞
def fetch_data():
    data = requests.get('http://api.example.com')  # 阻塞
    return data.json()

# 异步IO非阻塞
async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://api.example.com') as resp:
            return await resp.json()
```

## A.4 总结

常见问题主要集中在：
- **数据库连接**：检查服务状态、连接参数
- **异步编程**：确保在异步函数中使用 await
- **测试维护**：定期清理缓存、重置数据库
- **性能优化**：使用批量查询、缓存、异步IO

## A.5 相关资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)
- [pytest 文档](https://docs.pytest.org/)
- [Celery 文档](https://docs.celeryproject.org/)
