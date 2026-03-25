# Skill｜score_priority_and_resume_need

## 目的
基于岗位内容和匹配结果，判断投递优先级，并给出是否建议单独改简历。

## 输入
- role_category
- match_direction
- match_score
- jd_summary
- keywords
- skills

## 输出
- priority
- custom_resume_needed
- resume_focus
- short_note

## 规则

### 高优先级
满足多数条件时可判高：
- 与 AI Agent 开发 / AI 产品高度相关
- match_score >= 85
- 值得定制简历
- 岗位方向清晰且和用户经历有可包装连接点

### 中优先级
- 方向相关
- 但并不完全贴合
- 可作为补充投递

### 低优先级
- 相关性弱
- 不建议投入过多时间

## 是否建议改单独简历
以下情况优先判“是”：
- 岗位方向非常匹配
- JD 有明确高频关键词值得定向命中
- 该岗位可能进入面试概率较高

## resume_focus
返回 2~4 条简历强调建议，必须具体，不要空泛。

## 输出格式
```json
{
  "priority": "高",
  "custom_resume_needed": "是",
  "resume_focus": [
    "强调工程图评测系统中的工程实现与闭环设计",
    "突出 Python 后端和接口开发能力",
    "补充与 Agent / RAG 相关的项目关键词"
  ],
  "short_note": "值得优先投递，建议做一版开发向定制简历。"
}
```
