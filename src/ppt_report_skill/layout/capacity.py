import math
import unicodedata


def glyph_units(text):
    return sum(
        1 if unicodedata.east_asian_width(c) in {"W", "F"} else 0.55 for c in text
    )


def estimated_lines(text, width, font_size):
    units = max(width / 914400 * 72 / max(font_size, 1), 1)
    return sum(
        max(1, math.ceil(glyph_units(line) / units)) for line in text.split("\n")
    )


def fits(text, box, font_size=None):
    size = font_size or box.get("font_size", 20)
    # Insets and ascenders need real vertical space beyond the nominal font size.
    return (
        estimated_lines(text, max(box["width"] - 91440, 1), size) * size * 1.25
        <= box["height"] / 914400 * 72 + 2
    )
