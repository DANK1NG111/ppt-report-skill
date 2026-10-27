import importlib.util
from pathlib import Path
from zipfile import ZipFile


def test_public_package_excludes_user_assets_and_runtime(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "package_release", Path("scripts/package_release.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    root = tmp_path / "repo"
    root.mkdir()
    for name in ["SKILL.md", "BOOTSTRAP.md", "pyproject.toml"]:
        (root / name).write_text("public")
    for path in [
        "assets/templates/base_template.pptx",
        "output/private.txt",
        ".venv/private.txt",
        ".runtime/config.json",
        "src/pkg.py",
        "references/rules.md",
    ]:
        f = root / path
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("data")
    result = m.package_release(root, tmp_path / "release.zip")
    with ZipFile(result["path"]) as z:
        names = z.namelist()
        assert all(
            "private" not in n and "base_template" not in n and ".runtime" not in n
            for n in names
        )
        assert "ppt-report-skill/src/pkg.py" in names
