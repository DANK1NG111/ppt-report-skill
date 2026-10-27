"""Probe the actual authoring/rendering path instead of checking imports alone."""

from pathlib import Path
import importlib
import platform
import sys
from .models import save_json
from .renderer.render import find_office
from .starter import create_starter


def doctor(output, *, smoke=False):
    output = Path(output).resolve()
    checks = []

    def check(name, passed, detail):
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check("python", sys.version_info >= (3, 11), platform.python_version())
    for module in ["pptx", "lxml", "PIL", "fitz", "docx", "openpyxl", "fontTools"]:
        try:
            importlib.import_module(module)
        except Exception as exc:
            check(module, False, str(exc))
        else:
            check(module, True, "imported")
    office = find_office()
    check("office", office is not None, office or "LibreOffice/soffice not found")
    result = None
    if smoke and all(c["passed"] for c in checks):
        try:
            from .pipeline import create_presentation

            template = create_starter(output / "smoke/starter_template.pptx")
            result = create_presentation(
                template,
                [],
                {
                    "topic": "TEST FIXTURE 环境自检",
                    "presentation_type": "custom",
                    "required_sections": ["目标", "成果", "计划"],
                    "target_slide_count": 5,
                },
                output / "smoke/presentation.pptx",
                direct_text="# 目标\nTEST FIXTURE：验证中文和原生编辑功能。\n# 成果\n截至2026年9月30日，完成率87.6%，接入12个监测点。\n# 计划\n计划复核2项待处理问题。",
            )
            check(
                "generate_and_render",
                result["qa"]["errors"] == 0 and result["rendered"]["page_count"] == 5,
                "5-page actual PPTX → PDF → PNG, Chinese text and exact values checked",
            )
        except Exception as exc:
            check("generate_and_render", False, str(exc))
    elif smoke:
        check("generate_and_render", False, "prerequisites unavailable")
    report = {
        "status": "READY"
        if all(c["passed"] for c in checks) and smoke
        else "CHECKS_PASSED"
        if all(c["passed"] for c in checks)
        else "BLOCKED",
        "python": sys.executable,
        "checks": checks,
        "smoke_requested": smoke,
        "smoke_receipt": str(output / "smoke/pipeline_receipt.json")
        if result
        else None,
        "scope": "Authoring and headless rendering; native PowerPoint and human visual review remain delivery checks.",
    }
    save_json(report, output / "doctor_report.json")
    return report
