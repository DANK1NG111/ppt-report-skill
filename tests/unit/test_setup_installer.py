import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location("installer", Path("scripts/setup.py"))
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


def test_register_twice_and_preserve_existing(tmp_path):
    root = tmp_path / "repo with spaces"
    root.mkdir()
    (root / "SKILL.md").write_text("skill")
    skills = tmp_path / "skills"
    first = installer.register_skill(root, "codex", skills)
    assert (
        first["status"] == "REGISTERED"
        and Path(first["path"], "SKILL.md").read_text() == "skill"
    )
    assert (
        installer.register_skill(root, "codex", skills)["status"]
        == "ALREADY_REGISTERED"
    )
    other = tmp_path / "different"
    other.mkdir()
    with pytest.raises(installer.SetupError, match="CONFLICT"):
        installer.register_skill(other, "codex", skills)
    assert (root / "SKILL.md").read_text() == "skill"


def test_pointer_fallback_has_absolute_entry(tmp_path, monkeypatch):
    root = tmp_path / "root"
    root.mkdir()

    def denied(*a, **k):
        raise OSError("symlink unavailable")

    monkeypatch.setattr(Path, "symlink_to", denied)
    result = installer.register_skill(root, "claude", tmp_path / "skills")
    assert result["mode"] == "pointer"
    assert str(root / "SKILL.md") in Path(result["path"], "SKILL.md").read_text()
    assert (
        installer.register_skill(root, "claude", tmp_path / "skills")["status"]
        == "ALREADY_REGISTERED"
    )


@pytest.mark.parametrize(
    "system,manager,expected",
    [
        ("Darwin", "brew", "libreoffice"),
        ("Windows", "winget", "TheDocumentFoundation.LibreOffice"),
        ("Linux", "apt-get", "fonts-noto-cjk"),
        ("Linux", "dnf", "libreoffice-impress"),
    ],
)
def test_supported_package_managers(system, manager, expected):
    commands = installer.office_install_commands(
        system, lambda name: "/bin/" + name if name in {manager, "sudo"} else None
    )
    assert expected in " ".join(sum(commands, []))
    assert all(isinstance(command, list) for command in commands)


def test_unrelated_existing_directory_is_preserved(tmp_path):
    skills = tmp_path / "skills"
    destination = skills / "ppt-report-skill"
    destination.mkdir(parents=True)
    file = destination / "mine.txt"
    file.write_text("keep")
    with pytest.raises(installer.SetupError, match="CONFLICT"):
        installer.register_skill(tmp_path / "repo", "generic", skills)
    assert file.read_text() == "keep"


@pytest.mark.skipif(__import__("os").name == "nt", reason="POSIX shell entry")
def test_shell_honors_explicit_python_without_path_python_or_uv(tmp_path):
    import subprocess
    import sys
    import shutil

    root = tmp_path / "repo with spaces"
    (root / "scripts").mkdir(parents=True)
    shutil.copy("setup.sh", root / "setup.sh")
    (root / "scripts/setup.py").write_text(
        'import sys;print("EXPLICIT_INTERPRETER",sys.executable);print(sys.argv)'
    )
    tools = tmp_path / "tools"
    tools.mkdir()
    (tools / "dirname").symlink_to(shutil.which("dirname"))
    result = subprocess.run(
        [
            "/bin/sh",
            str(root / "setup.sh"),
            "--python",
            sys.executable,
            "--agent",
            "none",
        ],
        env={"PATH": str(tools)},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "EXPLICIT_INTERPRETER" in result.stdout and sys.executable in result.stdout
