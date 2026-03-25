# 开发说明（Vue + FastAPI）

本文件仅描述当前生效架构，不包含历史版本信息。

## 1. 当前架构

- 前端：`frontend/`（Vue 3 + Vite）
- 后端：`backend/`（FastAPI API 层）
- 核心能力：`src/`（Agent、鉴权、解析、模板适配、Excel 写入、历史库、去重）
- 测试：`tests/`

## 2. 目录职责

- `frontend/src/views/`：页面（总览 / 工作台 / 历史 / 设置）
- `frontend/src/lib/api.js`：前端 API 封装（超时、错误兜底、Bearer token）
- `frontend/src/state.js`：全局状态（pending、notice、结果缓存、登录态）
- `backend/main.py`：API 入口与路由
- `backend/errors.py`：统一响应结构（`ok/data/error/request_id/timestamp`）
- `backend/service.py`：业务编排（auth/analyze/write/history/bootstrap）
- `src/auth_store.py`：用户与 session token 存储
- `src/history_store.py`：按 `user_id` 隔离的历史数据

## 3. 本地启动

1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

2. 安装前端依赖

```bash
cd frontend
npm install
```

3. 启动后端（项目根目录）

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8001
```

4. 启动前端（新终端）

```bash
cd frontend
npm run dev
```

## 4. 环境变量

```text
OPENAI_API_KEY=你的百炼 API Key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
JOB_AGENT_MODEL=qwen-plus
```

## 5. 开发规范（强制）

- 每次改动都要补最小必要测试
- 提交前必须通过测试与自检
- API 错误必须返回结构化可解释信息，不允许只返回 deny 式报错
- 前端交互必须有明确状态反馈（加载中/成功/失败）
- 不得在默认 UI 中暴露个人路径或隐私信息

## 6. 测试命令

后端接口与基础能力：

```bash
python -m pytest -q tests/test_backend_api.py tests/test_path_utils.py
```

如需前端打包验证：

```bash
cd frontend
npm run build
```

## 7. Git 提交规范

- 分支建议：`codex/<feature-name>`
- 提交信息建议：
  - `feat: ...` 新功能
  - `fix: ...` 缺陷修复
  - `refactor: ...` 重构
  - `test: ...` 测试补充
  - `docs: ...` 文档更新
- 一个提交只做一类事情，避免混杂

## 8. Code Review 检查项

- 是否引入行为回归
- 错误处理是否完整（含建议与上下文）
- 是否补了对应测试
- 性能是否退化（多余请求、重复渲染、阻塞加载）
- 命名与模块边界是否清晰
