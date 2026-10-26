"""Geometry and content heuristics; unknown is an honest supported result."""

import re


def classify(text, boxes, images, width, height, index, total, tables=0, charts=0):
    if re.search(r"设计说明|Design Description|IMPORTANT NOTE", text, re.I):
        return "unknown", ["instruction", "exclude_from_generation"]
    if re.search(r"感谢|谢谢|thank you", text, re.I):
        return "closing", []
    if re.search(r"CONTENTS|目录", text, re.I):
        return "contents", []
    if len(boxes) <= 2 and any(b["font_size"] >= 36 for b in boxes) and index > 2:
        return "section", []
    if index <= 2 and any(b["font_size"] >= 36 for b in boxes):
        return "cover", []
    if charts:
        return "chart", ["data"]
    if tables:
        return "table", ["data"]
    if re.search(r"\d{4}年", text) and text.count("年") >= 3:
        return "timeline", ["image_text"] if images else []
    if re.search(r"\d[,.\d]*(?:k|\+|万|%)", text) and len(boxes) >= 6:
        return "data", []
    if images:
        return "image_text", []
    bodies = [b for b in boxes if b["y"] > height * 0.14 and len(b["text"]) > 20]
    if (
        len(bodies) >= 2
        and max(b["x"] for b in bodies) - min(b["x"] for b in bodies) > width * 0.25
    ):
        return "two_column", ["comparison"]
    return "title_content" if boxes else "unknown", []
