from ppt_report_skill.models import Issue
from ppt_report_skill.template.analyzer import walk_shapes


def editable_issues(prs, path, plans=None):
    issues = []
    for i, slide in enumerate(prs.slides, 1):
        shapes = list(walk_shapes(slide.shapes))
        if not any(s.has_text_frame and s.text.strip() for s in shapes):
            issues.append(
                Issue("NOT_EDITABLE", "error", "页面缺少可编辑正文或标题。", i)
            )
        if plans and i <= len(plans):
            plan = plans[i - 1]
            visual = plan.visual_type
            if visual == "table" and not any(s.has_table for s in shapes):
                issues.append(
                    Issue("NATIVE_TABLE_MISSING", "error", "表格未保留为原生对象。", i)
                )
            if visual == "chart" and not any(s.has_chart for s in shapes):
                issues.append(
                    Issue("NATIVE_CHART_MISSING", "error", "图表未保留为原生对象。", i)
                )
            if visual == "table":
                table = next((s.table for s in shapes if s.has_table), None)
                if table is not None:
                    rows = [[c.text for c in r.cells] for r in table.rows]
                    if rows != [[str(v) for v in r] for r in plan.payload["rows"]]:
                        issues.append(
                            Issue(
                                "TABLE_DATA_MISMATCH",
                                "error",
                                "原生表格与计划数据不同。",
                                i,
                            )
                        )
            if visual == "chart":
                chart = next((s.chart for s in shapes if s.has_chart), None)
                if chart is not None:
                    actual = [(s.name, list(s.values)) for s in chart.series]
                    expected = [
                        (s["name"], s["values"])
                        for s in plan.payload["chart"]["series"]
                    ]
                    if actual != expected:
                        issues.append(
                            Issue(
                                "CHART_DATA_MISMATCH",
                                "error",
                                "原生图表系列或数值与计划不同。",
                                i,
                            )
                        )
        for sh in shapes:
            if sh.has_chart:
                chart = sh.chart
                if not any(
                    r.reltype.endswith("/package") for r in chart.part.rels.values()
                ):
                    issues.append(
                        Issue(
                            "CHART_WORKBOOK_MISSING",
                            "error",
                            "图表缺少嵌入数据工作簿。",
                            i,
                            sh.shape_id,
                        )
                    )
                if any(not s.name for s in chart.series):
                    issues.append(
                        Issue(
                            "CHART_SERIES_INVALID",
                            "error",
                            "图表系列缺少名称。",
                            i,
                            sh.shape_id,
                        )
                    )
    return issues
