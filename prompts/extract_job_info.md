# Prompt Template｜extract_job_info

请从以下岗位描述中提取结构化信息，并严格输出 JSON。

要求：
1. 不要输出多余解释。
2. 缺失字段返回空字符串或空数组。
3. 确保 JSON 可解析。

字段：
- company
- job_title
- location
- is_internship
- jd_summary
- keywords
- skills
- education_requirement

岗位文本：
{{raw_text}}
