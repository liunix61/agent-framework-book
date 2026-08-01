#| 附录E：Hermes Agent 介绍

## E.1 Hermes Agent 是什么？

**Hermes Agent** 是由 Nous Research 构建的**自主进化 AI Agent**。它是唯一具有**内置学习循环**的 Agent —— 它从经验中创建技能，在使用中改进技能，推动自己保持知识，并在跨会话中建立对你更深的理解。

### 核心特性

- **自主进化**：从经验中创建技能，在使用中持续改进
- **跨会话记忆**：FTS5 全文搜索 + LLM 总结，持久化记忆
- **多平台支持**：支持 CLI、Telegram、Discord、Slack、WhatsApp 等 20+ 平台
- **随处运行**：本地、Docker、SSH、Daytona、Singularity、Modal
- **内置工具**：60+ 内置工具（搜索、图像生成、TTS、浏览器等）
- **MCP 集成**：连接任何 MCP 服务器扩展工具能力
- **定时自动化**：内置 cron，支持定时任务
- **子代理并行**：可创建隔离的子代理处理并行任务流

## E.2 安装方式

### 1. 最快方式（推荐）

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

### 2. 使用 Hermes Desktop

下载并运行 Hermes Desktop 安装器：
https://hermes-agent.nousresearch.com/

### 3. Windows 原生安装

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

## E.3 快速开始

### 首次设置

```bash
hermes setup --portal
```

**说明**：一次 OAuth 认证即可覆盖模型和所有四个 Tool Gateway 工具（网络搜索、图像生成、TTS、浏览器）。

### 基本对话

```bash
hermes
```

然后在交互式 CLI 中开始对话：

```
> 你好，请介绍一下你自己

Hermes 是一个自主进化的 AI Agent，由 Nous Research 构建...
```

### 多平台对话

Hermes 支持通过多个平台与它对话：

- **Telegram**
- **Discord**
- **Slack**
- **WhatsApp**
- **Signal**
- **Matrix**
- **Mattermost**
- **Email**
- **SMS**
- **DingTalk**
- **Feishu**
- **WeCom**
- **Weixin**
- **QQ Bot**
- **Yuanbao**
- **BlueBubbles**
- **Home Assistant**
- **Microsoft Teams**
- **Google Chat**

## E.4 核心功能

### 1. 记忆系统（Memory System）

**特点**：
- 跨会话持久化记忆
- FTS5 全文搜索
- LLM 摘要压缩
- 定期自我提示（nudges）

**使用示例**：

```bash
# 添加记忆
> 记住我喜欢简洁的回答，不喜欢废话

# 查询记忆
> 我喜欢什么风格的回答？

# Hermes 会自动记住你的偏好，并在后续对话中应用
```

### 2. 技能系统（Skills System）

**特点**：
- 从经验中创建技能
- 技能自我改进
- 技能可复用和分享
- 兼容 agentskills.io 标准

**使用示例**：

```bash
# 创建技能
> 创建一个技能，用于分析代码质量

# Hermes 会根据你的需求创建技能，并在后续任务中复用
```

### 3. 工具系统（Tools）

**内置工具**（60+）：
- **搜索工具**：网络搜索、提取、浏览
- **图像工具**：图像生成、视觉分析
- **语音工具**：文本转语音、语音识别
- **代码工具**：代码执行、代码审查
- **文件工具**：文件读取、写入、搜索
- **系统工具**：进程管理、环境变量

**配置工具**：

```bash
# 查看可用工具
> 列出所有可用工具

# 使用工具
> 使用搜索工具查找 "Python 最佳实践"
```

### 4. MCP 集成

**MCP（Model Context Protocol）** 是一个开放标准，用于连接 Agent 和外部工具。

**使用示例**：

```bash
# 连接 MCP 服务器
> 连接 MCP 服务器 http://localhost:3000/mcp

# 过滤工具
> 只显示与文件相关的工具

# 扩展 Hermes
> 使用 MCP 服务器扩展工具能力
```

### 5. 定时自动化（Cron）

**内置 cron 支持**，可配置定时任务：

```bash
# 设置定时任务
> 每天早上 9 点发送邮件报告

# 查看所有定时任务
> 列出所有定时任务

# 删除定时任务
> 删除定时任务 123
```

### 6. 子代理并行（Delegates）

**特点**：
- 创建隔离的子代理
- 并行处理多个任务流
- 程序化工具调用

**使用示例**：

```bash
# 创建子代理
> 创建一个子代理处理数据清洗任务

# 并行处理
> 同时处理任务 A 和任务 B
```

## E.5 配置

### 配置文件位置

- **Linux/macOS**：`~/.config/hermes/config.yaml`
- **Windows**：`%USERPROFILE%\.config\hermes\config.yaml`

### 基本配置示例

```yaml
model:
  provider: anthropic
  model_name: claude-sonnet-4
  api_key: your-api-key

memory:
  backend: sqlite
  database_path: ~/.cache/hermes/memory.db

tools:
  enabled:
    - search
    - code
    - file
    - web
    - image
    - tts
    - browser

platforms:
  - telegram
  - discord
  - slack

temperature: 0.7
max_tokens: 4096
```

### 配置平台

```bash
# 配置 Telegram
hermes config set telegram_token your-token

# 配置 Discord
hermes config set discord_token your-token

# 配置 Slack
hermes config set slack_token your-token
```

## E.6 高级功能

### 1. 语音模式（Voice Mode）

**特点**：
- 实时语音交互
- 支持 CLI、Telegram、Discord、Discord VC
- 语音识别和合成

**使用示例**：

```bash
# 启用语音模式
> 启用语音模式

# 在 Discord VC 中使用
> 在 Discord 语音频道中使用语音模式
```

### 2. 个性系统（Personality & SOUL.md）

**特点**：
- 定义 Hermes 的默认语气
- 使用 SOUL.md 全局配置

**SOUL.md 示例**：

```markdown
# SOUL.md

你是一个专业、简洁、高效的 AI 助手。

# 规则
1. 回答要简洁明了
2. 避免废话
3. 提供可操作的答案

# 语气
专业、友好、直接
```

### 3. 上下文文件（Context Files）

**特点**：
- 项目上下文文件
- 每次对话都会考虑上下文

**使用示例**：

```bash
# 创建上下文文件
> 创建项目上下文文件 /path/to/project/context.md

# 在上下文中对话
> 在这个项目中，帮我分析代码
```

### 4. 安全功能

**特点**：
- 命令审批
- 授权控制
- 容器隔离

**配置示例**：

```bash
# 启用命令审批
> 启用命令审批

# 配置授权规则
> 允许运行文件工具，禁止运行系统工具
```

## E.7 使用场景

### 场景1：代码开发

```bash
> 我需要重构这个 Python 项目
> 分析代码结构
> 提供重构建议
> 生成重构代码
```

### 场景2：数据清洗

```bash
> 读取 /path/to/data.csv
> 清洗数据
> 去除重复行
> 处理缺失值
> 保存清洗后的数据
```

### 场景3：自动化任务

```bash
# 设置定时任务
> 每天早上 9 点发送邮件报告
> 邮件内容：项目状态、待办事项

# 定时任务会自动执行
```

### 场景4：多平台监控

```bash
# 配置多个平台
> 配置 Telegram
> 配置 Discord
> 配置 Slack

# 在所有平台接收通知
```

## E.8 开发者指南

### 架构概览

```
用户输入
    ↓
意图理解
    ↓
记忆检索
    ↓
工具调用
    ↓
执行任务
    ↓
结果返回
```

### 自定义工具

```bash
# 注册自定义工具
> 注册工具 my_tool，描述：自定义工具函数

# 使用工具
> 调用工具 my_tool，参数：查询参数
```

### 调试

```bash
# 启用调试模式
> 启用调试模式

# 查看日志
> 查看最近的日志
```

## E.9 常见问题

### Q1: 如何重置记忆？

```bash
> 重置所有记忆
```

### Q2: 如何删除技能？

```bash
> 删除技能 my_skill
```

### Q3: 如何更新配置？

```bash
> 更新配置文件
```

### Q4: 如何连接 MCP 服务器？

```bash
> 连接 MCP 服务器 http://localhost:3000/mcp
```

### Q5: 如何查看所有工具？

```bash
> 列出所有可用工具
```

## E.10 相关资源

- **官方文档**：https://hermes-agent.nousresearch.com/docs
- **GitHub 仓库**：https://github.com/NousResearch/hermes-agent
- **下载**：https://hermes-agent.nousresearch.com/
- **Discord 社区**：https://discord.gg/NousResearch
- **Skills Hub**：https://agentskills.io

## E.11 版本历史

- **v1.0** (2024-01): 初始版本
- **v1.1** (2024-02): 添加记忆系统
- **v1.2** (2024-03): 新增多平台支持
- **v1.3** (2024-04): 添加 MCP 集成
- **v1.4** (2024-05): 优化性能
- **v1.5** (2024-06): 新增语音模式
- **v1.6** (2024-07): 增强技能系统

## E.12 总结

Hermes Agent 是一个**自主进化、多平台、多工具**的 AI Agent。通过合理的配置和使用，它可以：

- ✅ 自动化重复任务
- ✅ 辅助开发和代码审查
- ✅ 处理复杂数据任务
- ✅ 跨平台监控和通知
- ✅ 定时自动化工作流

**开始使用 Hermes Agent，让 AI 成为你的自主助手！**
