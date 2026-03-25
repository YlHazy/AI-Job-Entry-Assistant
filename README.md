# 岗位录入助手（Vue + FastAPI）

一个本地运行的岗位录入 Agent：把 JD 文本 / 岗位链接 / 岗位截图转换成结构化数据，并写入你已有的 Excel 求职看板。

## 你现在得到的版本

- 前端：Vue 3 + Vite（多页面路由、状态管理、加载动画、错误提示）
- 后端：FastAPI（统一错误模型、请求 ID、可追踪响应）
- 鉴权：用户名登录、Bearer token 会话、多用户数据隔离
- Agent：优先调用百炼 Qwen，失败时自动回退规则链路
- Excel：支持非空模板适配，兼容中文路径和带引号路径
- 历史库：本地存储、检索、疑似重复提示

## 核心功能

- 三种输入模式：文本 / 链接 / 截图（OCR）
- 登录 / 注册与用户级历史记录隔离
- 结构化提取：公司、岗位、方向、优先级、差距等字段
- 分析轨迹可视化：每一步执行结果可回看
- Excel 模板适配：自动识别 sheet、表头、数据起始行、列映射
- 写入失败可解释：返回可能原因和修复建议，而不是简单报错

## 环境要求

- Python 3.11+
- Node.js 18+

## 安装依赖

后端依赖：

```bash
pip install -r requirements.txt
```

前端依赖：

```bash
cd frontend
npm install
```

## 环境变量（百炼）

请在系统环境变量中配置：

```text
OPENAI_API_KEY=你的百炼 API Key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
JOB_AGENT_MODEL=qwen-plus
```

说明：

- `OPENAI_API_KEY` 必填
- `OPENAI_BASE_URL`、`JOB_AGENT_MODEL` 可使用上面的默认值

## 启动项目

1. 启动后端（项目根目录）：

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8001
```

2. 启动前端（新终端）：

```bash
cd frontend
npm run dev
```

3. 打开前端地址：

```text
http://127.0.0.1:5173
```

## 使用流程

1. 首次进入先注册账号，之后使用账号登录。
2. 在“工作台”选择输入模式并提交分析。
3. 在“结构化结果”区检查并修改字段（如有需要）。
4. 填写 Excel 路径（可选填写 Sheet 名称），点击写入。
5. 在“历史库”检索当前账号下的记录和详情。

## Excel 写入说明

- 支持写入到已有复杂模板（不要求空白文件）
- 支持中文路径、带引号路径（如 `"D:\求职\Day1_求职看板.xlsx"`）
- 默认不在前端预填个人路径，避免隐私暴露
- 写入时会做行高与字体优化，避免“行距异常大”的显示问题

## 常见问题

### 1) 写入失败：文件被占用

请关闭 Excel / WPS 后重试。

### 2) 链接抓取失败

可能是目标站点反爬、登录限制或网络不可达，建议先改用文本模式。

### 3) OCR 不可用

安装 `pytesseract` 后，还需在系统安装 Tesseract OCR 引擎。

## 测试

后端 API 与核心路径测试：

```bash
python -m pytest -q tests/test_backend_api.py tests/test_path_utils.py
```

## 项目结构

```text
backend/              # FastAPI 接口层
frontend/             # Vue 前端
src/                  # Agent 与业务核心逻辑
tests/                # 测试
data/                 # 本地数据库/模板缓存等数据
skills/               # 团队开发规范与技能说明
```
