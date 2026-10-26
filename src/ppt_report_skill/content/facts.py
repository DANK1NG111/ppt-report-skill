"""Lossless extraction and conservative cross-source conflict detection."""

import hashlib
import re
from collections import defaultdict
from ppt_report_skill.models import SourceFact, ReportError

NUMBER = re.compile(
    r"(?<![A-Za-z0-9_.])[-+]?\d[\d,]*(?:\.\d+)?\s*(?:%|％|万元|亿元|元|个|人|项|次|台|套|公里|km|kg|秒|分钟|小时|天|万|亿)?"
)
DATE = re.compile(
    r"\d{4}(?:[-/]\d{1,2}(?:[-/]\d{1,2})?|年(?:\d{1,2}月(?:\d{1,2}日)?)?)"
)
CATEGORIES = [
    ("risk", "风险|延期|依赖|不确定"),
    ("problem", "问题|不足|缺陷|困难"),
    ("plan", "下一步|计划|拟于|将于|后续"),
    ("goal", "目标|旨在|预期"),
    ("result", "成果|实现|完成|获奖|提升|降低"),
    ("progress", "进度|进展|已接入|已交付"),
    ("method", "方法|采用|算法|实验设计"),
    ("conclusion", "结论|总结|表明"),
    ("experience", "经历|负责|参与"),
    ("evidence", "证据|证明|附件"),
    ("background", "背景|现状|需求"),
]


def extract_facts(blocks, focus_points=()):
    facts = []
    seen = set()
    for block in blocks:
        if (
            block.kind in {"heading", "title", "image"}
            or block.text.strip() == "TEST FIXTURE"
        ):
            continue
        for sentence in re.split(r"(?<=[。！？；])\s*|\n+", block.text):
            text = sentence.strip()
            if not text:
                continue
            key = (block.source, block.location, text)
            if key in seen:
                continue
            seen.add(key)
            category = next(
                (c for c, p in CATEGORIES if re.search(p, text)),
                "data" if NUMBER.search(text) else "background",
            )
            numbers = [m.group(0).strip() for m in NUMBER.finditer(text)]
            units = [re.sub(r"^[-+\d,.\s]+", "", x) for x in numbers]
            importance = (
                3
                if category in {"result", "data", "risk", "conclusion"}
                else 2
                if category in {"goal", "progress", "problem", "plan", "method"}
                else 1
            ) + sum(2 for x in focus_points if x in text or x in block.section)
            facts.append(
                SourceFact(
                    "fact-" + hashlib.sha256("|".join(key).encode()).hexdigest()[:16],
                    text,
                    block.source,
                    block.location,
                    category,
                    text,
                    DATE.findall(text),
                    numbers,
                    [u for u in units if u],
                    importance,
                    1.0,
                    block.section,
                )
            )
    return facts


def detect_conflicts(facts):
    groups = defaultdict(list)
    for fact in facts:
        if not fact.value:
            continue
        text = fact.content
        dates = DATE.findall(text)
        for i, date in enumerate(dates):
            text = text.replace(date, f"DATESCOPE_{chr(65 + i)}")
        signature = re.sub(r"\s+", "", NUMBER.sub("#", text)).strip("。；;")
        groups[(signature, tuple(dates))].append(fact)
    conflicts = []
    for (signature, dates), group in groups.items():
        if len({tuple(x.value) for x in group}) > 1:
            for fact in group:
                fact.status = "CONFLICT"
            conflicts.append(
                {
                    "status": "CONFLICT",
                    "metric": signature,
                    "dates": list(dates),
                    "facts": [f.id for f in group],
                    "variants": [
                        {
                            "content": f.content,
                            "source": f.source,
                            "location": f.location,
                        }
                        for f in group
                    ],
                }
            )
    return conflicts


def require_consistent(facts):
    conflicts = detect_conflicts(facts)
    if conflicts:
        raise ReportError(
            "CONTENT_CONFLICT",
            "多份材料同一指标存在不同数值，请提供明确的来源决议。",
            str(conflicts),
        )
    return facts
