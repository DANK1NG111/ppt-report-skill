import json
import re
from copy import deepcopy
from pathlib import Path
import pytest
from ppt_report_skill.models import ReportError, PresentationRequest, SourceFact
from ppt_report_skill.pipeline import create_presentation
from ppt_report_skill.starter import create_starter
from ppt_report_skill.rehearsal import export_rehearsal
from ppt_report_skill.design import make_design_contract, verify_design_contract
from ppt_report_skill.template.analyzer import analyze_template
from ppt_report_skill.planner.outline import plan_outline
from ppt_report_skill.pipeline import combine_plans
from ppt_report_skill.layout.matcher import match_layout


def test_contract_rejects_payload_change_and_stable_ids_survive_reorder(tmp_path):
    template = create_starter(tmp_path / "starter.pptx")
    profile = analyze_template(template)
    request = PresentationRequest(
        presentation_type="custom", required_sections=["成果"], target_slide_count=3
    )
    facts = [
        SourceFact(
            "fact1",
            "完成率87.6%。",
            "source",
            "1",
            "data",
            "完成率87.6%。",
            section="成果",
        )
    ]
    outline = plan_outline(request, facts, profile)
    plans = combine_plans(request, facts, outline, profile, [], 280, 6)
    for p in plans:
        match_layout(p, profile)
    contract = make_design_contract(profile, plans, request, outline, tmp_path)
    assert verify_design_contract(contract, profile, plans)
    changed = deepcopy(plans)
    changed[1].payload["text_items"] = ["完成率90%。"]
    with pytest.raises(ReportError, match="DESIGN_DRIFT"):
        verify_design_contract(contract, profile, changed)
    reordered = make_design_contract(
        profile, list(reversed(plans)), request, outline, tmp_path / "reorder"
    )
    assert [p["slide_id"] for p in reordered["pages"]] == [
        p["slide_id"] for p in reversed(contract["pages"])
    ]


@pytest.mark.render
def test_rehearsal_embeds_current_pages_and_escapes_notes(tmp_path):
    template = create_starter(tmp_path / "starter.pptx")
    result = create_presentation(
        template,
        [],
        {
            "topic": "TEST FIXTURE </script> <img onerror=alert(1)>",
            "presentation_type": "custom",
            "required_sections": ["成果"],
            "target_slide_count": 3,
        },
        tmp_path / "report.pptx",
        direct_text="# 成果\n完成率87.6%，已接入12个监测点。",
    )
    path = Path(export_rehearsal(result))
    html = path.read_text()
    blob = re.search(
        r'<script id="deck-data" type="application/json">(.*?)</script>', html, re.S
    ).group(1)
    data = json.loads(blob)
    assert len(data["pages"]) == 3 and all(
        p["image"].startswith("data:image/png;base64,") for p in data["pages"]
    )
    assert data["pages"][0]["title"] == "TEST FIXTURE </script> <img onerror=alert(1)>"
    assert "</script>" not in blob and "87.6%" in html
    Path(result["rendered"]["images"][0]).write_bytes(b"changed")
    with pytest.raises(ReportError, match="STALE_REHEARSAL"):
        export_rehearsal(result)
