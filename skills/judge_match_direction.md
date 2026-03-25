# Skill｜judge_match_direction

## 目的
判断该岗位和用户当前双线求职方向的匹配度。

## 用户目标方向
- AI Agent 开发
- AI 产品
- 技术产品（补充方向）

## 输入
- role_category
- job_title
- jd_summary
- keywords
- skills

## 输出
- match_direction
- match_score
- reason
- main_gap

## 判断逻辑

### AI Agent 开发
优先匹配以下岗位：
- LLM 应用开发
- AI Agent 开发
- RAG / 检索增强
- Prompt / Tool Calling
- Python 后端 + AI 集成
- 智能工作流 / 自动化流程

### AI 产品
优先匹配以下岗位：
- AI 应用产品
- 智能助手产品
- AIGC 产品
- 场景设计与产品流程
- 需求分析 + AI 功能设计

### 双向都可
同时具备技术理解与产品抽象要求，且与 AI 应用落地相关。

### 不推荐
与目标方向弱相关，例如：
- 纯前端
- 纯测试
- 强销售导向
- 与 AI / 产品 / 技术平台均弱相关

## 分数建议
- 85~100：高度匹配
- 70~84：中高匹配
- 50~69：一般匹配
- 0~49：不推荐

## 输出格式
```json
{
  "match_direction": "AI Agent 开发",
  "match_score": 88,
  "reason": "岗位强调 Python、RAG、Agent Workflow 和模型接入，和用户的开发主线高度一致。",
  "main_gap": "若用户缺少完整 AI 应用项目，需要在简历中补一个 Agent / RAG 项目样本。"
}
```
