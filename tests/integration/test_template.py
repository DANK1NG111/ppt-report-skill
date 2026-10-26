from pathlib import Path
import hashlib
from ppt_report_skill.template.analyzer import analyze_template
from ppt_report_skill.models import TemplateProfile
from dataclasses import asdict


def test_real_template_profile(tmp_path):
    path = Path("assets/templates/base_template.pptx")
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    p = analyze_template(path, tmp_path / "profile.json")
    assert len(p.layouts) == 21
    assert p.fonts and p.colors and p.theme_colors and p.logos
    assert {"cover", "contents", "section", "closing"} <= {
        l.layout_type for l in p.layouts
    }
    assert TemplateProfile.from_dict(asdict(p)).sha256 == before
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before
