import re

PATTERNS = {
    "defense": r"答辩|个人贡献|个人情况|学习情况|入党|毕业论文",
    "academic_report": r"学术|课程汇报|研究背景|实验|文献|算法|讨论|方法",
    "project_progress": r"项目进展|里程碑|阶段交付|当前进度|项目目标|项目风险",
    "work_report": r"工作汇报|工作总结|下一步工作|季度|年度|部门|已完成工作",
}


def detect_report_type(request, facts):
    if request.presentation_type:
        return request.presentation_type
    text = request.topic + "\n" + "\n".join(f.section + " " + f.content for f in facts)
    scores = {
        kind: len(re.findall(pattern, text)) for kind, pattern in PATTERNS.items()
    }
    return max(scores, key=scores.get) if any(scores.values()) else "custom"
