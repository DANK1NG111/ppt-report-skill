"""Build a public source bundle from an explicit repo-owned allowlist."""

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import argparse
import hashlib
import json

TOP_FILES = [
    "SKILL.md",
    "README.md",
    "BOOTSTRAP.md",
    "AGENTS.md",
    "CLAUDE.md",
    "DEVELOPMENT.md",
    "development_log.md",
    "FINAL_REPORT.md",
    "V1_1_REPORT.md",
    "pyproject.toml",
    "requirements.txt",
    "setup.sh",
    "setup.ps1",
    ".gitignore",
]
TOP_DIRS = ["src", "scripts", "references", "agents", ".github", "tests"]


def package_release(root, output):
    root = Path(root).resolve()
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    files = [root / name for name in TOP_FILES if (root / name).is_file()]
    for name in TOP_DIRS:
        files.extend(
            p
            for p in (root / name).rglob("*")
            if p.is_file()
            and not p.is_symlink()
            and not any(
                part in {"__pycache__", ".pytest_cache", ".ruff_cache"}
                or part.endswith(".egg-info")
                for part in p.relative_to(root).parts
            )
            and p.suffix not in {".pyc", ".pyo"}
        )
    files = sorted(set(files))
    if not (root / "BOOTSTRAP.md").is_file():
        raise ValueError("missing installer instructions")
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, "ppt-report-skill/" + path.relative_to(root).as_posix())
    receipt = {
        "path": str(output),
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "files": [p.relative_to(root).as_posix() for p in files],
        "excluded": [
            "user templates",
            "output",
            "environments",
            "local runtime",
            "research checkouts",
        ],
    }
    output.with_suffix(".manifest.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2)
    )
    return receipt


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output", default=".dist/ppt-report-skill.zip")
    args = p.parse_args()
    r = package_release(Path(__file__).resolve().parents[1], args.output)
    print(f"PASS: {len(r['files'])} public source files, {r['path']}")
