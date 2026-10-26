"""Retained real-template acceptance artifacts for the three report scenarios."""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pptx import Presentation
from ppt_report_skill.pipeline import create_presentation
from ppt_report_skill.models import save_json
from ppt_report_skill.validator.content import slide_text, compact


def run_cases(output="output/real_template_cases"):
    results = []
    for name in ["work_report", "project_report", "defense"]:
        fixture = Path("tests/fixtures") / name
        request = json.loads((fixture / "request.json").read_text())
        expected = json.loads((fixture / "expected.json").read_text())
        result = create_presentation(
            "assets/templates/base_template.pptx",
            [fixture / "material.md"],
            request,
            Path(output) / name / "presentation.pptx",
        )
        text = compact(
            "\n".join(slide_text(s) for s in Presentation(result["path"]).slides)
        )
        facts = json.loads(Path(result["build"], "source_facts.json").read_text())
        assert all(compact(f["content"]) in text for f in facts), (
            name,
            "missing source fact",
        )
        for value in expected["required_values"] + expected["required_phrases"]:
            assert compact(value) in text, (name, value)
        plans = json.loads(Path(result["build"], "slide_plans.json").read_text())
        order = list(
            dict.fromkeys(
                p["section"] for p in plans if p["slide_type"] in {"content", "section"}
            )
        )
        if expected["required_sections"]:
            assert order == expected["required_sections"]
        if request.get("target_slide_count"):
            assert result["slide_count"] == request["target_slide_count"]
        assert result["qa"]["errors"] == 0
        results.append(
            {
                "case": name,
                "status": "PASS",
                "slide_count": result["slide_count"],
                "fact_count": len(facts),
                "errors": result["qa"]["errors"],
                "warnings": result["qa"]["warnings"],
                "path": result["path"],
                "build": result["build"],
                "rendered": result["rendered"],
            }
        )
        print(
            f"PASS {name}: {result['slide_count']} slides, {len(facts)} facts, {result['qa']['warnings']} warnings",
            flush=True,
        )
    save_json(
        {"status": "PASS", "cases": results}, Path(output) / "real_template_report.json"
    )
    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="output/real_template_cases")
    run_cases(parser.parse_args().output)
