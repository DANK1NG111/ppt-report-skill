import json
import pytest
from ppt_report_skill.draft import create_draft
from ppt_report_skill.models import ReportError


def test_draft_sources_and_explicit_state(tmp_path):
    out = create_draft(
        "assets/templates/base_template.pptx",
        [],
        {"topic": "TEST FIXTURE"},
        tmp_path / "draft.pptx",
        direct_text="已完成 12 项工作，完成率 87.6%。",
    )
    status = json.loads((tmp_path / "build/draft_status.json").read_text())
    assert out.exists() and status["status"] == "DRAFT_UNVALIDATED"
    assert (tmp_path / "build/source_facts.json").exists()


def test_conflict_stops_generation(tmp_path):
    a = tmp_path / "a.md"
    b = tmp_path / "b.md"
    a.write_text("项目完成率 82%。")
    b.write_text("项目完成率 87%。")
    with pytest.raises(ReportError, match="CONTENT_CONFLICT"):
        create_draft(
            "assets/templates/base_template.pptx", [a, b], {}, tmp_path / "draft.pptx"
        )
    assert not (tmp_path / "draft.pptx").exists()
    assert json.loads((tmp_path / "build/conflicts.json").read_text())
