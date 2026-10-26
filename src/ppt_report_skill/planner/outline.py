from ppt_report_skill.content.report_type import detect_report_type
from ppt_report_skill.models import PresentationOutline, ReportError
from .timing import estimate_count

SECTIONS = {
    "work_report": ["目标", "已完成工作", "成果", "问题", "下一步"],
    "project_progress": [
        "项目目标",
        "当前进度",
        "阶段成果",
        "关键数据",
        "风险",
        "下一步",
    ],
    "academic_report": ["背景", "问题", "方法", "实验", "结果", "讨论", "结论"],
    "defense": ["个人情况", "学习情况", "工作经历", "实践成果", "总结"],
}
CATEGORY_SECTION = {
    "background": 0,
    "goal": 0,
    "progress": 1,
    "experience": 1,
    "method": 2,
    "result": 2,
    "data": 2,
    "problem": 3,
    "risk": 3,
    "plan": -1,
    "conclusion": -1,
    "evidence": 2,
}


def assign_facts(request, facts, sections, kind):
    groups = {s: [] for s in sections}
    for fact in facts:
        exact = next(
            (
                s
                for s in sections
                if fact.section == s or fact.section.lstrip("# ").endswith(s)
            ),
            None,
        )
        matching = next(
            (
                s
                for s in sections
                if len(s) > 1 and (s in fact.section or s in fact.content)
            ),
            None,
        )
        if exact or matching:
            target = exact or matching
        elif request.required_sections:
            # Unassigned evidence remains visible in a designated existing section.
            target = sections[0]
        elif kind == "academic_report":
            mapping = {
                "background": 0,
                "problem": 1,
                "method": 2,
                "data": 4,
                "result": 4,
                "conclusion": 6,
                "risk": 5,
                "plan": 5,
            }
            target = sections[min(mapping.get(fact.category, 3), len(sections) - 1)]
        elif kind == "project_progress":
            mapping = {
                "goal": 0,
                "background": 0,
                "progress": 1,
                "result": 2,
                "data": 3,
                "risk": 4,
                "problem": 4,
                "plan": 5,
                "conclusion": 5,
            }
            target = sections[min(mapping.get(fact.category, 2), len(sections) - 1)]
        else:
            target = sections[
                min(CATEGORY_SECTION.get(fact.category, 0), len(sections) - 1)
            ]
        groups[target].append(fact)
    return groups


def plan_outline(request, facts, profile=None):
    kind = detect_report_type(request, facts)
    sections = request.required_sections or (
        list(dict.fromkeys(f.section for f in facts if f.section))
        if kind == "custom"
        else SECTIONS[kind]
    )
    sections = sections or ["汇报内容"]
    groups = assign_facts(request, facts, sections, kind)
    count = request.target_slide_count or estimate_count(
        request.duration, len(facts), len(sections)
    )
    if count < len(sections) and count != 1:
        raise ReportError(
            "CONSTRAINT_CONFLICT", f"{len(sections)} 个必选章节无法放入 {count} 页。"
        )
    assumptions = []
    if not request.audience:
        assumptions.append("未指定听众，按熟悉主题的一般汇报听众组织；未作为事实写入。")
    if not request.duration:
        assumptions.append("未指定时长，按页数与证据密度估算。")
    if not request.target_slide_count:
        assumptions.append(f"自动规划 {count} 页，包含封面和结尾。")
    return PresentationOutline(
        request.topic,
        kind,
        request.duration or round(count * 0.55, 1),
        count,
        sections,
        {s: sum(f.importance for f in group) or 1 for s, group in groups.items()},
        assumptions,
    )
