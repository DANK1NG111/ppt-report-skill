"""Read font family metadata without changing system font installation."""

from functools import lru_cache
from pathlib import Path
import os


@lru_cache(maxsize=1)
def installed_fonts():
    from fontTools.ttLib import TTFont, TTCollection

    roots = [
        Path("/System/Library/Fonts"),
        Path("/Library/Fonts"),
        Path.home() / "Library/Fonts",
        Path("/usr/share/fonts"),
        Path.home() / ".local/share/fonts",
    ]
    if os.environ.get("WINDIR"):
        roots.append(Path(os.environ["WINDIR"]) / "Fonts")
    names = set()
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if path.suffix.lower() not in {".ttf", ".ttc", ".otf", ".otc"}:
                continue
            handle = None
            try:
                handle = (
                    TTCollection(path, lazy=True)
                    if path.suffix.lower() in {".ttc", ".otc"}
                    else TTFont(path, lazy=True)
                )
                for font in (
                    handle.fonts if isinstance(handle, TTCollection) else [handle]
                ):
                    for record in font["name"].names:
                        if record.nameID in {1, 16}:
                            names.add(record.toUnicode())
            except Exception:
                continue
            finally:
                if handle:
                    handle.close()
    return frozenset(names)


def font_report(profile, available=None):
    available = installed_fonts() if available is None else available
    missing = [family for family in profile.fonts if family not in available]
    fallback = next(
        (
            f
            for f in [
                "Hiragino Sans GB",
                "Noto Sans CJK SC",
                "Microsoft YaHei",
                "微软雅黑",
                "Arial Unicode MS",
                "Arial Unicode",
            ]
            if f in available
        ),
        None,
    )
    return {
        "requested_families": profile.fonts,
        "missing_families": missing,
        "available_fallback": fallback,
        "pptx_font_declarations_preserved": True,
        "scope": "模板字体声明与本机安装字体对照；具体 PDF 字体替代见 render_receipt.json。",
    }
