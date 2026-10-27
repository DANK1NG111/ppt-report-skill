#!/usr/bin/env python3
"""Standard-library bootstrap, intentionally runnable before project dependencies exist."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time


class SetupError(Exception):
    pass


def run(command, log, env=None):
    with Path(log).open("a", encoding="utf-8") as stream:
        stream.write("\n$ " + repr([str(x) for x in command]) + "\n")
        stream.flush()
        result = subprocess.run(
            [str(x) for x in command], stdout=stream, stderr=subprocess.STDOUT, env=env
        )
    if result.returncode:
        raise SetupError("命令执行失败，技术日志：" + str(log))


def python_path(venv):
    return Path(venv) / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def good_python(path):
    try:
        result = subprocess.run(
            [str(path), "-c", "import sys;raise SystemExit(sys.version_info < (3,11))"],
            capture_output=True,
            timeout=15,
        )
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def office_path():
    candidates = [
        os.environ.get("PPT_REPORT_SOFFICE"),
        shutil.which("soffice"),
        shutil.which("libreoffice"),
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    ]
    for key, default in [
        ("PROGRAMFILES", "C:/Program Files"),
        ("PROGRAMFILES(X86)", "C:/Program Files (x86)"),
    ]:
        candidates.append(
            str(Path(os.environ.get(key, default)) / "LibreOffice/program/soffice.exe")
        )
    return next(
        (str(Path(p).resolve()) for p in candidates if p and Path(p).is_file()), None
    )


def office_install_commands(system, which, is_root=False):
    if system == "Darwin" and which("brew"):
        return [[which("brew"), "install", "--cask", "libreoffice"]]
    if system == "Windows" and which("winget"):
        return [
            [
                which("winget"),
                "install",
                "--id",
                "TheDocumentFoundation.LibreOffice",
                "--exact",
                "--silent",
                "--disable-interactivity",
            ]
        ]
    if system == "Linux":
        prefix = [] if is_root else [which("sudo") or "sudo", "-n"]
        if which("apt-get"):
            return [
                prefix + [which("apt-get"), "update"],
                prefix
                + [
                    which("apt-get"),
                    "install",
                    "-y",
                    "libreoffice-impress",
                    "fonts-noto-cjk",
                ],
            ]
        if which("dnf"):
            return [
                prefix
                + [
                    which("dnf"),
                    "install",
                    "-y",
                    "libreoffice-impress",
                    "google-noto-sans-cjk-fonts",
                ]
            ]
    return []


def register_skill(root, agent, skills_dir=None, home=None):
    root = Path(root).resolve()
    home = Path(home or Path.home())
    if agent == "none":
        return {"status": "NOT_REQUESTED", "path": None}
    if agent == "auto":
        agent = (
            "claude"
            if os.environ.get("CLAUDECODE")
            else "codex"
            if os.environ.get("CODEX_HOME") or (home / ".codex").exists()
            else "generic"
        )
    parent = (
        Path(skills_dir)
        if skills_dir
        else home / (".claude/skills" if agent == "claude" else ".agents/skills")
    )
    destination = parent / "ppt-report-skill"
    if destination.is_symlink():
        if destination.resolve() != root:
            raise SetupError("SKILL_DESTINATION_CONFLICT: " + str(destination))
        return {
            "status": "ALREADY_REGISTERED",
            "path": str(destination),
            "agent": agent,
            "mode": "symlink",
        }
    if destination.exists():
        marker = destination / ".ppt-report-pointer.json"
        if destination.resolve() == root:
            return {
                "status": "ALREADY_REGISTERED",
                "path": str(destination),
                "agent": agent,
                "mode": "directory",
            }
        try:
            owned = json.loads(marker.read_text()).get("root") == str(root)
        except (OSError, ValueError):
            owned = False
        if not owned:
            raise SetupError(
                "SKILL_DESTINATION_CONFLICT: 保留现有目录 " + str(destination)
            )
        return {
            "status": "ALREADY_REGISTERED",
            "path": str(destination),
            "agent": agent,
            "mode": "pointer",
        }
    parent.mkdir(parents=True, exist_ok=True)
    try:
        destination.symlink_to(root, target_is_directory=True)
        mode = "symlink"
    except OSError:
        destination.mkdir()
        mode = "pointer"
        (destination / "SKILL.md").write_text(
            "---\nname: ppt-report-skill\ndescription: 基于模板和来源材料制作可编辑汇报PPT，支持原生对象、渲染、QA及排练。\n---\n\n先读取完整Skill：["
            + str(root / "SKILL.md")
            + "]("
            + str(root / "SKILL.md")
            + ")。\n\n运行目录为 `"
            + str(root)
            + "`，使用该目录 `.venv` 中的 Python。此入口仅定位已配置的完整技能。\n",
            encoding="utf-8",
        )
        (destination / ".ppt-report-pointer.json").write_text(
            json.dumps({"root": str(root)})
        )
    return {
        "status": "REGISTERED",
        "path": str(destination),
        "agent": agent,
        "mode": mode,
    }


def bootstrap(args):
    root = Path(args.root).resolve()
    runtime = root / ".runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    log = runtime / "setup.log"
    venv = Path(args.venv).resolve() if args.venv else root / ".venv"
    python = python_path(venv)
    result = {
        "status": "CONFIGURING",
        "root": str(root),
        "python": str(python),
        "platform": platform.system(),
        "started_at": time.time(),
    }
    receipt = runtime / "setup_receipt.json"
    try:
        if not (root / "SKILL.md").is_file() or not (root / "pyproject.toml").is_file():
            raise SetupError("不是完整的ppt-report-skill仓库。")
        if not good_python(python):
            if venv.exists():
                raise SetupError(
                    "已有虚拟环境不可用，请指定新的--venv路径，现有文件已保留。"
                )
            interpreter = args.python or sys.executable
            if good_python(interpreter):
                run([interpreter, "-m", "venv", venv], log)
            else:
                uv = shutil.which("uv") or str(
                    runtime / "bin" / ("uv.exe" if os.name == "nt" else "uv")
                )
                if not Path(uv).is_file():
                    raise SetupError(
                        "PYTHON_NOT_READY: 请按BOOTSTRAP.md用官方uv准备Python3.12，再重试。"
                    )
                run([uv, "venv", "--python", "3.12", venv], log)
        fingerprint = hashlib.sha256(
            (root / "pyproject.toml").read_bytes()
            + (root / "requirements.txt").read_bytes()
        ).hexdigest()
        previous = {}
        try:
            previous = json.loads(receipt.read_text())
        except (ValueError, OSError):
            pass
        imports = subprocess.run(
            [
                str(python),
                "-c",
                "import pptx,fitz,docx,openpyxl,fontTools,ppt_report_skill",
            ],
            capture_output=True,
        )
        if (
            args.refresh
            or imports.returncode
            or previous.get("dependencies_sha256") != fingerprint
            or previous.get("python") != str(python)
        ):
            run(
                [
                    python,
                    "-m",
                    "pip",
                    "install",
                    "--disable-pip-version-check",
                    "--no-input",
                    "-e",
                    root,
                ],
                log,
            )
        office = office_path()
        if not office and args.install_system:
            commands = office_install_commands(
                platform.system(),
                shutil.which,
                hasattr(os, "geteuid") and os.geteuid() == 0,
            )
            if not commands:
                raise SetupError(
                    "OFFICE_NOT_READY: 未检测到受支持的系统包管理器。按BOOTSTRAP.md安装LibreOffice后重试。"
                )
            for command in commands:
                run(command, log)
            office = office_path()
        if not office:
            raise SetupError(
                "OFFICE_NOT_READY: 安装LibreOffice/soffice，或使用--install-system自动安装。"
            )
        (runtime / "config.json").write_text(
            json.dumps({"soffice": office}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        # Run from the target installation, not the caller's working directory.
        run(
            [
                python,
                "-m",
                "ppt_report_skill.cli",
                "doctor",
                "--smoke",
                "--output",
                runtime / "doctor",
            ],
            log,
        )
        doctor = json.loads((runtime / "doctor/doctor_report.json").read_text())
        if doctor["status"] != "READY":
            raise SetupError("DOCTOR_FAILED: 实际生成或渲染未通过。")
        registration = register_skill(root, args.agent, args.skills_dir)
        result.update(
            status="READY",
            dependencies_sha256=fingerprint,
            soffice=office,
            doctor=str(runtime / "doctor/doctor_report.json"),
            registration=registration,
            finished_at=time.time(),
        )
    except (SetupError, OSError, subprocess.SubprocessError) as exc:
        result.update(status="BLOCKED", message=str(exc), log=str(log))
        receipt.write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print("BLOCKED: " + str(exc))
        return 2
    receipt.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("READY: " + str(receipt))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="一次完成独立Python环境、依赖、实际渲染自检及Agent技能注册"
    )
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--venv")
    parser.add_argument("--python")
    parser.add_argument(
        "--agent",
        choices=["auto", "codex", "claude", "generic", "none"],
        default="auto",
    )
    parser.add_argument("--skills-dir")
    parser.add_argument("--install-system", action="store_true")
    parser.add_argument("--refresh", action="store_true")
    return bootstrap(parser.parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
