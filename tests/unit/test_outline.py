import pytest
from ppt_report_skill.request import parse_request
from ppt_report_skill.content.loader import text_blocks
from ppt_report_skill.content.facts import extract_facts
from ppt_report_skill.planner.outline import plan_outline


@pytest.mark.parametrize('kind',['work_report','project_progress','academic_report','defense'])
def test_outline(kind):
    sections=['个人情况','学习情况','工作经历','实践成果','总结'] if kind=='defense' else []
    r=parse_request(dict(topic='TEST FIXTURE',presentation_type=kind,duration=5,required_sections=sections,focus_points=['成果']))
    facts=extract_facts(text_blocks('# 成果\n已完成 12 项工作。\n下一步开展测试。'),r.focus_points)
    outline=plan_outline(r,facts)
    assert 6<=outline.target_slide_count<=10
    assert outline.estimated_duration==5
    if sections:assert outline.sections==sections
    assert outline.section_weights
