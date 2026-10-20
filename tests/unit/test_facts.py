import json
from pathlib import Path
from ppt_report_skill.content.loader import text_blocks
from ppt_report_skill.content.facts import extract_facts,detect_conflicts


def test_known_facts_lossless():
    expected=json.loads(Path('tests/fixtures/known_facts.json').read_text())
    facts=extract_facts(text_blocks('\n'.join(expected),'known.md'))
    assert [f.content for f in facts]==expected
    for fact in facts:
        assert fact.original_text==fact.content and fact.source=='known.md' and fact.location
        for value in fact.value:assert value in fact.original_text
        for date in fact.date:assert date in fact.original_text


def test_conflicts_and_date_scopes():
    facts=extract_facts(text_blocks('项目完成率 82%。','a.md')+text_blocks('项目完成率 87%。','b.md'))
    assert len(detect_conflicts(facts))==1
    assert all(f.status=='CONFLICT' for f in facts)
    facts=extract_facts(text_blocks('2026年1月项目完成率 82%。','a.md')+text_blocks('2026年2月项目完成率 87%。','b.md'))
    assert not detect_conflicts(facts)


def test_decimal_and_units():
    facts=extract_facts(text_blocks('2026-10-01 完成率 87.6%，预算 12.50万元，负责人张华。'))
    assert len(facts)==1 and '87.6%' in facts[0].value and '12.50万元' in facts[0].value
    assert '张华' in facts[0].content
