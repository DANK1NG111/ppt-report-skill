import re
from ppt_report_skill.models import Issue
from ppt_report_skill.template.analyzer import walk_shapes

SAMPLE = re.compile(
    r"单击此处添加|添加标题内容|添加标题文本内容|您的内容打在这里|在此处添加您的文本|章节页标题文字|西南交通大学汇报通用模板|Click to edit|99\+|3\.5k|52,000",
    re.I,
)


def slide_text(slide):
    texts = []
    for sh in walk_shapes(slide.shapes):
        if sh.has_text_frame:
            texts.append(sh.text)
        if sh.has_table:
            texts.extend(c.text for r in sh.table.rows for c in r.cells)
        if sh.has_chart:
            chart = sh.chart
            if chart.has_title:
                texts.append(chart.chart_title.text_frame.text)
            for series in chart.series:
                texts.append(series.name)
    return "\n".join(texts)


def compact(text):
    return re.sub(r"\s+", "", text)


def content_issues(prs, plans=None, request=None):
    issues = []
    texts = [slide_text(s) for s in prs.slides]
    for i, text in enumerate(texts, 1):
        slide = prs.slides[i - 1]
        if slide.shapes.title is not None and not slide.shapes.title.text.strip():
            issues.append(Issue("EMPTY_TITLE", "error", "标题占位符为空。", i))
        for shape in slide.shapes:
            if (
                shape.has_text_frame
                and shape.top > prs.slide_height * 0.9
                and shape.text.strip().isdigit()
                and int(shape.text.strip()) != i
            ):
                issues.append(
                    Issue(
                        "PAGE_NUMBER",
                        "warning",
                        "底部数字与当前页号不同，需核对是否为页码。",
                        i,
                        shape.shape_id,
                    )
                )
        if not text.strip():
            issues.append(Issue("BLANK_SLIDE", "error", "页面无可编辑文字。", i))
        matches = list(SAMPLE.finditer(text))
        authorized = "\n".join(
            [
                str(r.get("original_text", ""))
                for p in (plans or [])
                for r in p.source_refs
            ]
            + [p.title for p in (plans or [])]
        )
        if any(m.group() not in authorized for m in matches):
            issues.append(
                Issue("TEMPLATE_SAMPLE", "error", "残留模板示例文字或数字。", i)
            )
        if "[待补充" in text:
            issues.append(Issue("MISSING_CONTENT", "warning", "存在明确待补充项。", i))
        if plans and i <= len(plans):
            plan = plans[i - 1]
            if plan.slide_type != "contents" and compact(plan.title) not in compact(
                text
            ):
                issues.append(Issue("MISSING_TITLE", "error", "页面缺少计划标题。", i))
            for expected in plan.payload.get("text_items", []):
                if compact(expected) not in compact(text):
                    issues.append(
                        Issue(
                            "FACT_MISSING",
                            "error",
                            "计划内容未出现在页面：" + expected[:50],
                            i,
                        )
                    )
            for fragment in plan.payload.get("text_items", []):
                if (
                    plan.source_refs
                    and not fragment.startswith("[待补充")
                    and not any(
                        compact(fragment) in compact(r.get("original_text", ""))
                        for r in plan.source_refs
                    )
                ):
                    issues.append(
                        Issue(
                            "UNSUPPORTED_FACT", "error", "正文无法回溯到原始材料。", i
                        )
                    )
    for i in range(1, len(texts)):
        if compact(texts[i]) and compact(texts[i]) == compact(texts[i - 1]):
            issues.append(
                Issue("DUPLICATE_SLIDE", "warning", "相邻页面内容完全相同。", i + 1)
            )
    if request:
        all_text = "\n".join(texts)
        for required in request.must_include:
            if compact(required) not in compact(all_text):
                issues.append(
                    Issue(
                        "REQUIRED_CONTENT_MISSING", "error", "缺少必选信息：" + required
                    )
                )
        if plans:
            actual = []
            for p in plans:
                if p.slide_type in {"content", "section"} and (
                    not actual or actual[-1] != p.section
                ):
                    actual.append(p.section)
            if request.required_sections and actual != request.required_sections:
                issues.append(
                    Issue("SECTION_ORDER", "error", "章节顺序与固定目录不一致。")
                )
    return issues
