"""Phase-14 draft integration; full delivery QA is a later pipeline stage."""

from dataclasses import asdict
from pathlib import Path
from ppt_report_skill.models import save_json, ReportError
from ppt_report_skill.request import parse_request
from ppt_report_skill.template.analyzer import analyze_template
from ppt_report_skill.content.loader import load_materials
from ppt_report_skill.content.facts import extract_facts, detect_conflicts
from ppt_report_skill.planner.outline import plan_outline
from ppt_report_skill.planner.slide_planner import plan_slides
from ppt_report_skill.generator.presentation import generate_presentation


def create_draft(template, materials, request_data, output, direct_text=None):
    output = Path(output)
    build = output.parent / "build"
    build.mkdir(parents=True, exist_ok=True)
    request = parse_request(request_data)
    profile = analyze_template(template, build / "template_profile.json")
    blocks = load_materials(materials, direct_text, build / "extracted_images")
    facts = extract_facts(blocks, request.focus_points)
    if not facts:
        raise ReportError("MATERIAL_EMPTY", "材料中无可用于汇报的事实。")
    conflicts = detect_conflicts(facts)
    save_json([asdict(b) for b in blocks], build / "material_blocks.json")
    save_json([asdict(f) for f in facts], build / "source_facts.json")
    save_json(conflicts, build / "conflicts.json")
    if conflicts:
        raise ReportError(
            "CONTENT_CONFLICT", "材料存在数值冲突，详见 build/conflicts.json。"
        )
    for required in request.must_include:
        if not any(required in f.content for f in facts):
            raise ReportError(
                "REQUIRED_CONTENT_MISSING", f"材料中未找到必选信息：{required}"
            )
    outline = plan_outline(request, facts, profile)
    plans = plan_slides(request, facts, outline, profile)
    save_json(request, build / "request.json")
    save_json(outline, build / "outline.json")
    path = generate_presentation(template, profile, plans, request, output, build)
    save_json(
        {
            "status": "DRAFT_UNVALIDATED",
            "slide_count": len(plans),
            "path": str(path.resolve()),
            "pending": ["structural_qa", "visual_qa", "final_delivery"],
        },
        build / "draft_status.json",
    )
    return path
