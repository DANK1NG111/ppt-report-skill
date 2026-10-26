"""Check current release evidence; never generate visual or native-open attestations."""

import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ppt_report_skill.delivery import finalize_delivery
from ppt_report_skill.models import save_json


def verify_release(last_phase=30):
    root = Path(__file__).resolve().parents[1]
    log = (root / "development_log.md").read_text()
    statuses = {
        int(m.group(1)): m.group(2)
        for m in re.finditer(r"## Phase (\d+)\s+Status:\s*(PASS|FIXING|BLOCKED)", log)
    }
    assert all(statuses.get(i) == "PASS" for i in range(last_phase + 1)), statuses
    for name in [
        "SKILL.md",
        "README.md",
        "DEVELOPMENT.md",
        "FINAL_REPORT.md",
        "references/acceptance_matrix.md",
        "pyproject.toml",
        "requirements.txt",
    ]:
        assert (root / name).is_file(), name
    regression = json.loads(
        (root / "output/regression/regression_report.json").read_text()
    )
    assert regression["status"] == "PASS" and regression["counts"]["tests"] >= 143
    assert all(
        regression["counts"][key] == 0 for key in ["failures", "errors", "skipped"]
    )
    assert all(regression["categories"].values())
    audit = json.loads((root / "output/acceptance/object_audit.json").read_text())
    assert audit["status"] == "PASS" and len(audit["cases"]) == 5
    deliveries = []
    for case in audit["cases"]:
        output = Path(case["path"]).parent
        result = json.loads((output / "pipeline_receipt.json").read_text())
        assert case["sha256"] == result["sha256"]
        delivery = finalize_delivery(
            result, output / "visual_review.json", include_pdf=True
        )
        assert delivery["status"] == "DELIVERED"
        deliveries.append(
            {
                k: delivery[k]
                for k in [
                    "path",
                    "sha256",
                    "slide_count",
                    "generation_report",
                    "visual_review",
                ]
            }
        )
    a = root / "01 西南交通大学红色系模板1.pptx"
    b = root / "assets/templates/base_template.pptx"
    assert (
        hashlib.sha256(a.read_bytes()).digest()
        == hashlib.sha256(b.read_bytes()).digest()
    )
    for name in ["base_template.json", "base_template.md"]:
        assert (root / "assets/template_profiles" / name).is_file()
    assert len(list((root / "assets/previews").glob("slide-*.png"))) == 21
    report = {
        "status": "PASS",
        "phases_checked": list(range(last_phase + 1)),
        "regression": regression["counts"],
        "delivered_cases": deliveries,
        "delivered_pages": sum(d["slide_count"] for d in deliveries),
        "source_facts": sum(c["source_facts"] for c in audit["cases"]),
        "original_template_unchanged": True,
    }
    save_json(report, root / "output/acceptance/release_audit.json")
    for name in ["SKILL.md", "README.md", "DEVELOPMENT.md", "FINAL_REPORT.md"]:
        p = root / name
        for link in re.findall(r"\]\(([^)]+)\)", p.read_text()):
            if not link.startswith(("http", "app:")):
                assert (p.parent / link).exists(), (name, link)
    print(
        f"PASS: phases 0-{last_phase}, {report['regression']['tests']} tests, 5 delivered cases, {report['delivered_pages']} pages, exact source facts and current hashes"
    )
    return report


if __name__ == "__main__":
    verify_release(int(sys.argv[1]) if len(sys.argv) > 1 else 30)
