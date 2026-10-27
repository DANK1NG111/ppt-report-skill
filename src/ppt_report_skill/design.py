"""A compact template-derived design contract and immutable page roster."""

import hashlib
import json
from pathlib import Path
from .models import ReportError, save_json
from .layout.regions import body_regions, union_box


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def make_design_contract(profile, plans, request, outline, output):
    layouts = {l.layout_id: l for l in profile.layouts}
    pages = []
    for plan in plans:
        layout = layouts[plan.layout_id]
        identity = {
            "section": plan.section,
            "title": plan.title,
            "facts": plan.supporting_facts,
            "refs": plan.source_refs,
            "visual": plan.visual_type,
            "payload": plan.payload,
        }
        base = hashlib.sha256(canonical(identity).encode()).hexdigest()[:16]
        occurrence = sum(p["identity"] == base for p in pages)
        pages.append(
            {
                "slide_id": f"{base}-{occurrence + 1}",
                "identity": base,
                "slide_number": plan.slide_number,
                "section": plan.section,
                "title": plan.title,
                "purpose": plan.core_message,
                "layout_id": layout.layout_id,
                "source_slide": layout.source_slide,
                "visual_type": plan.visual_type,
                "rhythm": "opening"
                if plan.slide_type == "cover"
                else "closing"
                if plan.slide_type == "closing"
                else "evidence"
                if plan.visual_type in {"chart", "table", "image", "diagram"}
                else "orientation"
                if plan.slide_type in {"section", "contents"}
                else "explanation",
                "estimated_seconds": plan.estimated_speaking_time,
                "image_slot": (
                    layout.image_boxes[0]
                    if layout.image_boxes
                    else union_box(body_regions(layout.body_boxes, profile))
                )
                if plan.visual_type == "image"
                else None,
                "fact_ids": plan.supporting_facts,
            }
        )
    contract = {
        "schema": "ppt-report.design.v1",
        "template_sha256": profile.sha256,
        "mode": request.template_mode,
        "objective": request.topic,
        "audience": request.audience,
        "presentation_type": outline.presentation_type,
        "sections": outline.sections,
        "palette": profile.colors,
        "fonts": profile.fonts,
        "canvas": {"width": profile.slide_width, "height": profile.slide_height},
        "allowed_layout_ids": list(layouts),
        "pages": pages,
    }
    contract["lock_sha256"] = hashlib.sha256(canonical(contract).encode()).hexdigest()
    output = Path(output)
    save_json(contract, output / "design_spec.json")
    lines = [
        "# 设计与逐页锁定",
        f"\n主题：{request.topic}\n\n模板 SHA256：{profile.sha256}\n\n模式：{request.template_mode}\n\n锁定摘要：{contract['lock_sha256']}",
        "\n| 页 | 稳定ID | 章节 / 标题 | 原模板页 | 视觉类型 / 节奏 | 秒 |",
        "|---|---|---|---:|---|---:|",
    ]
    for p in pages:
        lines.append(
            f"| {p['slide_number']} | {p['slide_id']} | {p['section']} / {p['title'].replace('|', '/')} | {p['source_slide']} | {p['visual_type']} / {p['rhythm']} | {p['estimated_seconds']:.1f} |"
        )
    (output / "design_spec.md").write_text("\n".join(lines))
    return contract


def verify_design_contract(contract, profile, plans):
    value = {k: v for k, v in contract.items() if k != "lock_sha256"}
    if hashlib.sha256(canonical(value).encode()).hexdigest() != contract["lock_sha256"]:
        raise ReportError("DESIGN_DRIFT", "设计锁定文件被修改，请重新规划。")
    if profile.sha256 != contract["template_sha256"] or len(plans) != len(
        contract["pages"]
    ):
        raise ReportError("DESIGN_DRIFT", "模板或页数与设计锁定不一致。")
    for plan, page in zip(plans, contract["pages"]):
        identity = {
            "section": plan.section,
            "title": plan.title,
            "facts": plan.supporting_facts,
            "refs": plan.source_refs,
            "visual": plan.visual_type,
            "payload": plan.payload,
        }
        if hashlib.sha256(canonical(identity).encode()).hexdigest()[:16] != page[
            "identity"
        ] or (plan.layout_id, plan.title, plan.section, plan.visual_type) != (
            page["layout_id"],
            page["title"],
            page["section"],
            page["visual_type"],
        ):
            raise ReportError(
                "DESIGN_DRIFT", f"第{plan.slide_number}页偏离锁定的标题、章节或版式。"
            )
    return True
