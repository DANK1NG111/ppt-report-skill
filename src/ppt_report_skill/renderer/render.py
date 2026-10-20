"""Render through a real office engine, never a synthetic approximation."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import fitz
from pptx import Presentation
from ppt_report_skill.models import ReportError, save_json
from .contact_sheet import contact_sheet


def render_presentation(path, output, *, dpi=110):
    path, output = Path(path).resolve(), Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    engine = os.environ.get("PPT_REPORT_SOFFICE") or shutil.which("soffice") or shutil.which("libreoffice")
    if not engine:
        raise ReportError("RENDER_FAILED", "未找到 LibreOffice/soffice，请安装或设置 PPT_REPORT_SOFFICE。")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    receipt = output / "render_receipt.json"
    if receipt.exists():
        cached = json.loads(receipt.read_text())
        if cached.get("sha256") == digest and cached.get("dpi") == dpi and all(Path(p).exists() for p in cached["images"]) and Path(cached["pdf"]).exists():
            return cached
    # Unique office profile makes simultaneous conversions independent.
    with tempfile.TemporaryDirectory(prefix="ppt-report-render-") as work:
        try:
            process = subprocess.run([engine, f"-env:UserInstallation={Path(work).as_uri()}", "--headless", "--convert-to", "pdf", "--outdir", str(output), str(path)], capture_output=True, text=True, timeout=180)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ReportError("RENDER_FAILED", "Office 渲染未完成。", str(exc)) from exc
    pdf = output / f"{path.stem}.pdf"
    if process.returncode or not pdf.exists():
        raise ReportError("RENDER_FAILED", "无法生成 PDF。", process.stdout + process.stderr)
    images = []
    with fitz.open(pdf) as document:
        if len(document) != len(Presentation(path).slides):
            raise ReportError("RENDER_FAILED", "渲染页数与 PPTX 不一致。")
        for i, page in enumerate(document):
            image = output / f"slide-{i+1:03}.png"
            page.get_pixmap(dpi=dpi).save(image)
            images.append(str(image))
    sheet = contact_sheet(images, output / "contact_sheet.png")
    result = dict(sha256=digest, dpi=dpi, engine=engine, pdf=str(pdf), images=images, contact_sheet=str(sheet), page_count=len(images))
    save_json(result, receipt)
    return result
