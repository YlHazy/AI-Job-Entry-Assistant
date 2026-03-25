"""Rule-based classifier for role category and priority."""

from __future__ import annotations

from dataclasses import dataclass

from src.schemas import JobRecord

ROLE_KEYWORDS = {
    "开发": [
        "python",
        "后端",
        "api",
        "rag",
        "agent",
        "workflow",
        "embedding",
        "向量数据库",
        "prompt",
        "tool calling",
        "模型接入",
        "部署",
        "工程",
    ],
    "产品": [
        "用户需求",
        "产品设计",
        "prd",
        "竞品",
        "用户研究",
        "场景分析",
        "功能规划",
        "指标分析",
        "协同研发",
    ],
    "技术产品": [
        "平台产品",
        "ai 平台",
        "数据平台",
        "工具产品",
        "技术方案",
        "研发协同",
        "跨团队推进",
        "技术理解",
    ],
}

MATCH_KEYWORDS = {
    "AI Agent 开发": ["llm", "agent", "rag", "prompt", "tool calling", "python", "自动化", "工作流"],
    "AI 产品": ["ai 产品", "智能助手", "aigc", "产品设计", "用户价值", "场景设计", "需求分析"],
    "双向都可": ["技术理解", "产品思维", "跨团队", "平台产品", "技术方案"],
}

NOT_RECOMMENDED = ["前端", "测试", "销售", "纯算法研究", "运营"]


@dataclass
class RoleCategoryDecision:
    role_category: str
    reason: str
    evidence_keywords: list[str]


@dataclass
class MatchDecision:
    match_direction: str
    match_score: int
    reason: str
    main_gap: str


@dataclass
class PriorityDecision:
    priority: str
    custom_resume_needed: str
    resume_focus: list[str]
    short_note: str


def enrich_job_record(record: JobRecord) -> JobRecord:
    """Fill classification fields on a parsed record."""

    haystack = " ".join(
        [
            record.job_title,
            record.jd_summary,
            " ".join(record.keywords),
            " ".join(record.skills),
            record.raw_text,
        ]
    ).lower()

    role_decision = analyze_role_category(haystack)
    match_decision = analyze_match_direction(haystack, role_decision.role_category)
    priority_decision = analyze_priority(haystack, match_decision)

    return record.model_copy(
        update={
            "role_category": role_decision.role_category,
            "category_reason": role_decision.reason,
            "evidence_keywords": role_decision.evidence_keywords,
            "match_direction": match_decision.match_direction,
            "match_score": match_decision.match_score,
            "match_reason": match_decision.reason,
            "main_gap": match_decision.main_gap,
            "priority": priority_decision.priority,
            "recommend_resume_customization": priority_decision.custom_resume_needed,
            "resume_focus": priority_decision.resume_focus,
            "short_note": priority_decision.short_note,
        }
    )


def analyze_role_category(text: str) -> RoleCategoryDecision:
    hits_by_category = {
        category: [keyword for keyword in keywords if keyword in text]
        for category, keywords in ROLE_KEYWORDS.items()
    }
    scores = {category: len(hits) for category, hits in hits_by_category.items()}
    best_category = max(scores, key=scores.get)
    if scores[best_category] == 0:
        return RoleCategoryDecision("待判断", "没有命中足够明确的岗位类别关键词。", [])

    evidence = hits_by_category[best_category][:4]
    reason = f"命中 {best_category} 相关关键词：{', '.join(evidence)}。"
    return RoleCategoryDecision(best_category, reason, evidence)


def classify_role_category(text: str) -> str:
    return analyze_role_category(text).role_category


def analyze_match_direction(text: str, role_category: str = "") -> MatchDecision:
    if any(keyword in text for keyword in NOT_RECOMMENDED):
        return MatchDecision("不推荐", 35, "岗位关键词与目标方向相关性较弱。", "与 AI 应用、Agent 或技术产品方向连接较弱。")

    hits_by_direction = {
        direction: [keyword for keyword in keywords if keyword in text]
        for direction, keywords in MATCH_KEYWORDS.items()
    }
    scores = {direction: len(hits) for direction, hits in hits_by_direction.items()}
    best_direction = max(scores, key=scores.get)

    if scores[best_direction] == 0:
        if "ai" in text or role_category == "技术产品":
            return MatchDecision("双向都可", 68, "岗位与 AI 方向有关，但定位还不够集中。", "需要更明确的 Agent、AI 产品或平台经历。")
        return MatchDecision("待判断", 50, "信息不足，暂时无法稳定判断匹配方向。", "JD 对岗位核心目标描述不够集中。")

    base_score = {"AI Agent 开发": 88, "AI 产品": 82, "双向都可": 75}.get(best_direction, 60)
    score = min(100, base_score + min(8, scores[best_direction] * 2))
    evidence = hits_by_direction[best_direction][:4]
    reason = f"命中 {best_direction} 相关关键词：{', '.join(evidence)}。"
    main_gap = build_main_gap(best_direction)
    return MatchDecision(best_direction, score, reason, main_gap)


def classify_match_direction(text: str) -> str:
    return analyze_match_direction(text).match_direction


def analyze_priority(text: str, match_decision: MatchDecision) -> PriorityDecision:
    high_signal = sum(
        keyword in text
        for keyword in ["agent", "rag", "llm", "aigc", "平台产品", "python", "产品设计", "技术方案"]
    )
    if match_decision.match_direction in {"AI Agent 开发", "AI 产品"} and match_decision.match_score >= 85 and high_signal >= 3:
        return PriorityDecision("高", "是", build_resume_focus(match_decision.match_direction), "方向高度匹配，值得优先投递并做定向简历。")
    if match_decision.match_direction == "不推荐":
        return PriorityDecision("低", "否", [], "相关性偏弱，保留记录即可。")
    if high_signal >= 1:
        return PriorityDecision("中", "否", build_resume_focus(match_decision.match_direction), "方向有一定相关性，可以作为补充投递。")
    return PriorityDecision("低", "否", [], "信息不足或相关性有限，优先级较低。")


def score_priority(text: str, match_direction: str) -> str:
    return analyze_priority(text, MatchDecision(match_direction, 0, "", "")).priority


def build_main_gap(match_direction: str) -> str:
    if match_direction == "AI Agent 开发":
        return "需要在简历里强化 Agent、RAG、工作流和 Python 工程落地经历。"
    if match_direction == "AI 产品":
        return "需要突出 AI 场景设计、需求分析和产品闭环推进经历。"
    if match_direction == "双向都可":
        return "需要更明确地说明你偏开发还是偏产品，以及代表性项目。"
    return "需要补充更明确的岗位相关经历。"


def build_resume_focus(match_direction: str) -> list[str]:
    if match_direction == "AI Agent 开发":
        return [
            "突出 Agent 或 RAG 项目的工程实现与效果闭环。",
            "强化 Python 后端、API 集成和工作流编排能力。",
            "补充与 LLM、Prompt、工具调用相关的项目关键词。",
        ]
    if match_direction == "AI 产品":
        return [
            "突出 AI 场景设计、需求拆解与产品闭环能力。",
            "补充用户价值、指标分析和跨团队推进案例。",
            "强调你对 AI 功能定义和落地的理解。",
        ]
    if match_direction == "双向都可":
        return [
            "说明你同时具备技术理解和产品抽象能力。",
            "补充一个能体现跨团队推进的代表项目。",
        ]
    return []
