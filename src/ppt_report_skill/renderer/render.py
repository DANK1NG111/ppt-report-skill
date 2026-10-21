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


def find_office():
    candidates=[os.environ.get('PPT_REPORT_SOFFICE'),shutil.which('soffice'),shutil.which('libreoffice'),'/Applications/LibreOffice.app/Contents/MacOS/soffice']
    return next((str(Path(p).resolve()) for p in candidates if p and Path(p).is_file()),None)


def render_presentation(path, output, *, dpi=110):
    path, output = Path(path).resolve(), Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    engine = find_office()
    if not engine:
        raise ReportError("RENDER_FAILED", "未找到 LibreOffice/soffice，请安装或设置 PPT_REPORT_SOFFICE。")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if not 60<=dpi<=300:raise ReportError('INVALID_REQUEST','渲染 DPI 应为 60–300。')
    receipt = output / "render_receipt.json"
    if receipt.exists():
        cached = json.loads(receipt.read_text())
        if cached.get("sha256") == digest and cached.get("dpi") == dpi and cached.get("font_config_version") == 2 and all(Path(p).exists() for p in cached["images"]) and Path(cached["pdf"]).exists():
            return cached
    # Unique office profile makes simultaneous conversions independent.
    with tempfile.TemporaryDirectory(prefix="ppt-report-render-") as work:
        env = os.environ.copy()
        substitutions = []
        if Path('/System/Library/Fonts').is_dir():
            # The bundled headless office does not automatically discover macOS fonts.
            config = Path(work) / 'fonts.conf'
            config.write_text('<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd"><fontconfig>'
                '<dir>/System/Library/Fonts</dir><dir>/System/Library/Fonts/Supplemental</dir><dir>/Library/Fonts</dir>'
                f'<cachedir>{work}/font-cache</cachedir>'
                '<alias><family>微软雅黑</family><prefer><family>Hiragino Sans GB</family></prefer></alias>'
                '<alias><family>Microsoft YaHei</family><prefer><family>Hiragino Sans GB</family></prefer></alias>'
                '<alias><family>宋体</family><prefer><family>Songti SC</family></prefer></alias>'
                '<alias><family>sans-serif</family><prefer><family>Arial</family><family>Hiragino Sans GB</family></prefer></alias>'
                '</fontconfig>')
            env['FONTCONFIG_FILE'] = str(config)
            substitutions = ['渲染环境：微软雅黑/Microsoft YaHei → Hiragino Sans GB；宋体 → Songti SC；PPTX 字体声明保留。']
        try:
            process = subprocess.run([engine, f"-env:UserInstallation={(Path(work)/'profile').as_uri()}", "--headless", "--convert-to", "pdf", "--outdir", work, str(path)], capture_output=True, text=True, timeout=180, env=env)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ReportError("RENDER_FAILED", "Office 渲染未完成。", str(exc)) from exc
        fresh_pdf=Path(work)/f'{path.stem}.pdf'
        if process.returncode or not fresh_pdf.exists():
            raise ReportError("RENDER_FAILED", "无法生成 PDF。", process.stdout + process.stderr)
        pdf = output / f"{path.stem}.pdf"
        shutil.copy2(fresh_pdf,pdf)
    images = [];texts=[]
    with fitz.open(pdf) as document:
        if len(document) != len(Presentation(path).slides):
            raise ReportError("RENDER_FAILED", "渲染页数与 PPTX 不一致。")
        for i, page in enumerate(document):
            image = output / f"slide-{i+1:03}.png"
            page.get_pixmap(dpi=dpi).save(image)
            images.append(str(image))
            texts.append(page.get_text(sort=True))
    for stale in output.glob('slide-*.png'):
        if str(stale) not in images:stale.unlink()
    sheet = contact_sheet(images, output / "contact_sheet.png")
    result = dict(sha256=digest, dpi=dpi, engine=engine, pdf=str(pdf), images=images, contact_sheet=str(sheet), page_count=len(images), font_config_version=2, font_substitutions=substitutions, page_texts=texts)
    save_json(result, receipt)
    return result
