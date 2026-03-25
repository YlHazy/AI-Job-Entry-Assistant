# Skill｜classify_role_category

## 目的
判断岗位更偏开发、产品、技术产品还是待判断。

## 输入
- job_title
- jd_summary
- keywords
- skills
- raw_text

## 输出
- role_category
- reason
- evidence_keywords

## 分类规则

### 开发
出现或强调以下内容时优先判为开发：
- Python
- 后端
- API
- RAG
- Agent
- Workflow
- Prompt Engineering
- Embedding
- 向量数据库
- 模型接入
- 服务部署
- 工程化实现

### 产品
出现或强调以下内容时优先判为产品：
- 用户需求
- 产品设计
- PRD
- 竞品分析
- 用户研究
- 场景分析
- 功能规划
- 指标分析
- 协调研发设计测试

### 技术产品
同时要求技术理解与产品推进时优先判为技术产品：
- 平台产品
- 工具产品
- AI 平台
- 数据平台
- 技术方案沟通
- 研发协同
- 跨团队推进

### 待判断
若信息不足或特征冲突明显，可返回待判断。

## 输出格式
```json
{
  "role_category": "技术产品",
  "reason": "JD 同时强调平台能力理解、需求抽象与跨研发团队推进。",
  "evidence_keywords": ["平台产品", "需求分析", "技术方案", "跨团队推进"]
}
```
