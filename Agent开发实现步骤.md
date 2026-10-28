# Agent 开发实现步骤（DeepSeek + LangChain）

> 本文是**具体怎么做**的操作手册：每一步写清「做什么」和「为什么」。  
> 总览路线图见 [`开发流程.md`](./开发流程.md)。  
> **约定：** 每完成一步，把对应勾选框打成 `[x]`；后续阶段的实现细节也持续追加到本文。

**技术选型（已定）：**

| 项 | 选择 | 原因（一句话） |
|----|------|----------------|
| 大模型 | DeepSeek | 国内可用、性价比高、支持工具调用 |
| LangChain 集成 | `langchain-deepseek` / `ChatDeepSeek` | 官方集成，比 `ChatOpenAI`+自定义 URL 更适合 Agent（工具调用、推理字段更完整） |
| Web 框架 | FastAPI | 项目已具备，API 与 Agent 分层清晰 |
| 包管理 | uv | 项目已采用 |

---

## 使用方式（你与助手）

1. 先读本节对应「阶段」，理解目标与为什么。
2. 按步骤操作；需要助手改代码时说：「按《Agent开发实现步骤》做第 X 步」。
3. 验收通过后勾选，再进入下一步/下一阶段。
4. **只改当前阶段相关文件**，避免一次堆太多能力。

---

## 阶段 0：确认现状（已完成）

- [x] 项目骨架：`backend/` + FastAPI + `/chat` 模拟接口
- [x] 依赖已有：`langchain`、`langchain-openai`、`fastapi`、`pydantic-settings`
- [x] 选定方案 B：`ChatDeepSeek`（而非仅改 `OPENAI_BASE_URL`）

**为什么先确认现状：** 避免重复造轮子，后续改动落在正确分层（`agents/` 管模型，`api/` 只管 HTTP）。

---

## 阶段 1：接通 DeepSeek（真实对话）

### 目标

`POST /chat/` 在配置了密钥后返回 DeepSeek 的真实回答；未配置密钥时仍返回友好提示、不崩溃。

### 为什么先做这一阶段

Agent（工具、记忆、RAG）都建立在「能稳定调用模型」之上。先跑通最小闭环，再加能力，出问题更好定位。

---

### 步骤 1.1：申请 DeepSeek API Key

**做什么：**

1. 打开 [DeepSeek 开放平台](https://platform.deepseek.com/)。
2. 注册/登录 → 创建 API Key → 复制保存（只显示一次，妥善保管）。

**为什么：**

- 调用云端模型必须有鉴权；Key 相当于「账号密码」，**绝不能提交到 Git**。
- 本项目用 `.env` 本地存放，仓库只保留 `.env.example` 模板。

**验收：** 你手头有一串以 `sk-` 开头的密钥。

- [ ] 已拿到 API Key

---

### 步骤 1.2：安装 `langchain-deepseek`

**做什么：**

在项目根目录执行：

```bash
uv add langchain-deepseek
```

**为什么：**

- 项目虽已有 `langchain-openai`，但用 `ChatOpenAI(base_url=DeepSeek)` 只保证「协议长得像 OpenAI」。
- Agent 后续要用工具调用、`deepseek-reasoner` 的推理内容等；官方包 `ChatDeepSeek` 会处理这些差异。
- 用 `uv add` 会同时写入 `pyproject.toml` 和锁文件，团队环境可复现。

**验收：** `pyproject.toml` 的 `dependencies` 中出现 `langchain-deepseek`。

- [x] 已安装依赖（`langchain-deepseek==1.1.1`，由助手执行 `uv add`）

---

### 步骤 1.3：配置环境变量（`.env`）

**做什么：**

1. 若还没有 `.env`，复制模板：

```bash
# Windows PowerShell
Copy-Item .env.example .env
```

2. 编辑 `.env`，使用 DeepSeek 专用变量（与真·OpenAI 区分）：

```env
# DeepSeek（Agent 主模型）
DEEPSEEK_API_KEY=sk-你的密钥
DEEPSEEK_MODEL=deepseek-chat
# 一般不用改；官方默认即此地址
# DEEPSEEK_API_BASE=https://api.deepseek.com/v1
```

常用模型：

| 模型名 | 用途 |
|--------|------|
| `deepseek-chat` | 日常对话、工具调用（阶段 1～4 默认用这个） |
| `deepseek-reasoner` | 强推理；需要思考过程时再切 |

**为什么：**

- 配置集中在环境变量：换机器、换密钥不必改代码。
- 字段名用 `DEEPSEEK_*`：语义清晰，避免「变量叫 OPENAI 实际却是 DeepSeek」的长期混乱。
- `.env` 已在 `.gitignore` 中忽略（若未忽略，务必补上）。

**验收：** 本地存在 `.env`，且 `DEEPSEEK_API_KEY` 非空。

- [ ] 已配置 `.env`

---

### 步骤 1.4：在 `core/config.py` 读取 DeepSeek 配置

**做什么：**

在 `Settings` 中增加（或改为）DeepSeek 相关字段，例如：

- `deepseek_api_key`
- `deepseek_model`（默认 `deepseek-chat`）
- `deepseek_api_base`（可选，默认官方地址）

`pydantic-settings` 会自动把环境变量 `DEEPSEEK_API_KEY` 映射为 `deepseek_api_key`。

**为什么：**

- 业务代码通过 `settings.xxx` 读配置，而不是到处 `os.getenv`，便于测试与替换。
- 无密钥时 Agent 可走「友好提示」分支，有密钥再真正调模型。

**验收：** 启动应用后能读到配置（可在临时打印或断点确认，调试完删除打印）。

- [x] 已更新 `config.py`（字段：`deepseek_api_key` / `deepseek_model` / `deepseek_api_base`）

---

### 步骤 1.5：实现 `agents/chat_agent.py`

**做什么：**

用 `ChatDeepSeek` + 系统提示 + 用户问题，`invoke` 后返回文本。伪逻辑：

```text
若无 DEEPSEEK_API_KEY → 返回友好模拟提示（不抛错）
否则 →
  创建 ChatDeepSeek(model=..., api_key=...)
  messages = [SystemMessage(SYSTEM_PROMPT), HumanMessage(question)]
  return llm.invoke(messages).content
```

**为什么：**

- **模型调用放在 `agents/`**：符合本项目分层；`api/routers` 只做 HTTP，以后加流式、会话也不用重写路由骨架。
- **SystemMessage**：固定助手人设与回答风格，减少每次请求重复拼长提示。
- **无密钥降级**：本地没 Key 时接口仍可用，方便前端/联调先通。

**验收：** 有 Key 时不再出现 `NotImplementedError`。

- [x] 已实现 `chat_agent.py`（无 Key 友好提示；有 Key 则 `ChatDeepSeek.invoke`）

---

### 步骤 1.6：更新 `.env.example` 与文档勾选

**做什么：**

- `.env.example` 写上 `DEEPSEEK_*` 占位（不要写真实密钥）。
- 把本文阶段 1 相关勾选打上。
- （可选）在 `开发流程.md` 阶段一注明：主模型为 DeepSeek + `ChatDeepSeek`。

**为什么：** 新同事/未来的你能按模板配环境，不靠口头传授。

- [x] 已更新 `.env.example`（`DEEPSEEK_*` 占位）

---

### 步骤 1.7：启动并验收

**做什么：**

```bash
uv sync
uv run uvicorn backend.main:app --reload
```

浏览器打开：http://127.0.0.1:8000/docs → 试 `POST /chat/`。

或 curl：

```bash
curl -X POST http://127.0.0.1:8000/chat/ ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"用一句话介绍你自己\"}"
```

**验收标准：**

| 条件 | 期望 |
|------|------|
| 已配置有效 Key | 返回自然中文回答，两次提问内容可不完全相同 |
| 未配置 Key / 空 Key | 返回提示配置密钥的文案，HTTP 不 500 |

**为什么要做手工验收：** 密钥、网络、模型名任一错误都会在这一层暴露；阶段 2 再加流式时，先保证非流式是稳的。

- [ ] 阶段 1 验收通过

---

## 阶段 2：流式输出（SSE）— 待实现

> 实现时把具体文件改动、命令、为什么追加到本节。

### 目标（预告）

前端可逐字显示；新增如 `POST /chat/stream`，保留原 `/chat/`。

### 为什么做

长回答时「等全部生成再返回」体验差；Agent 思考/调工具过程也可以后续用事件流推给前端。

### 实现时注意

- Agent 侧：`llm.stream` / `astream`
- API 侧：`StreamingResponse` 或 SSE
- 细节步骤：□ 待填写

---

## 阶段 3：会话与记忆 — 待实现

### 目标（预告）

同一 `session_id` 多轮可引用上文。

### 为什么做

无记忆则每次都是「失忆」；工具型 Agent 也需要对话状态（LangGraph 的 `thread_id` 与此相关）。

### 实现时注意

- Schema 增加 `session_id`
- 先内存存储，再 Redis/DB
- 细节步骤：□ 待填写

---

## 阶段 4：工具调用（Agent Tools）— 待实现

### 目标（预告）

模型能调用 `tools/` 中的工具（时间、计算、业务 API 等）。

### 为什么做

这是「聊天机器人」和「Agent」的分水岭：模型决定何时调工具、用结果再回答。

### 实现时注意

- DeepSeek `deepseek-chat` 支持 tool calling；与 `ChatDeepSeek.bind_tools` / LangGraph 配合
- 细节步骤：□ 待填写

---

## 阶段 5：RAG — 待实现

### 目标（预告）

基于自有文档回答，减少幻觉。

### 为什么做

模型参数里没有你的私有知识；检索片段再生成，是 Agent 常见能力组合。

### 实现时注意

- 向量模型与 DeepSeek 聊天模型可分离选型
- 细节步骤：□ 待填写

---

## 阶段 6：工程化 — 待实现

日志、限流、测试、README、可选 Docker / 前端。细节步骤：□ 待填写。

---

## 变更记录

| 日期 | 说明 |
|------|------|
| 2026-10-28 | 新建本文；确定 ChatDeepSeek 方案；写下阶段 1 完整步骤与为什么；预留阶段 2～6 |
| 2026-10-28 | 代码落地阶段 1.2～1.6：依赖、config、chat_agent、.env.example；待你完成 Key 配置与验收 |
