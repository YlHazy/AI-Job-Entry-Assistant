# Skill｜extract_job_fields

## 目的
从岗位原始文本中抽取可结构化落库的基础字段。

## 输入
- raw_text: 岗位 JD 原文
- source_platform: 来源平台，可为空
- source_url: 来源链接，可为空

## 输出字段
- company
- job_title
- location
- is_internship
- jd_summary
- keywords
- skills
- education_requirement

## 抽取要求
1. 优先提取明确出现的信息，不要猜测。
2. 如果公司名没有明确出现，返回空字符串。
3. `jd_summary` 保持 50~120 字，概括岗位主要工作与要求。
4. `keywords` 控制在 5~10 个，优先保留高价值词。
5. `skills` 偏技术 / 方法 / 工具，如 Python、SQL、RAG、PRD、数据分析。
6. 学历要求没有明确写出时，返回空字符串。

## 输出格式
返回 JSON 对象，例如：

```json
{
  "company": "某某科技",
  "job_title": "AI 产品经理实习生",
  "location": "北京",
  "is_internship": true,
  "jd_summary": "负责 AI 应用场景调研、需求分析和功能设计，协同研发推进产品落地。",
  "keywords": ["AI产品", "需求分析", "场景设计", "AIGC", "协同研发"],
  "skills": ["需求分析", "PRD", "竞品分析", "数据分析"],
  "education_requirement": "本科及以上"
}
```

## 失败处理
- 不确定的字段返回空值，不要编造
- 保证 JSON 可解析
