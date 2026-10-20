import pytest
from ppt_report_skill.models import PresentationRequest,ReportError
from ppt_report_skill.content.loader import text_blocks
from ppt_report_skill.content.facts import extract_facts
from ppt_report_skill.planner.outline import plan_outline
from ppt_report_skill.planner.slide_planner import plan_slides,fragment


@pytest.mark.parametrize('kind',['work_report','project_progress','defense'])
def test_complete_slide_plans(kind):
    r=PresentationRequest(topic='TEST FIXTURE',presentation_type=kind,duration=5)
    fs=extract_facts(text_blocks('# 成果\n已完成 12 项测试。\n下一步接入 4 个监测点。'))
    outline=plan_outline(r,fs);plans=plan_slides(r,fs,outline)
    assert len(plans)==outline.target_slide_count
    assert all(p.title and p.core_message and p.estimated_speaking_time>0 for p in plans)
    assert {f.id for f in fs}<={i for p in plans for i in p.supporting_facts}
    texts=[t for p in plans if p.slide_type=='content' for t in p.payload['text_items']]
    assert len(texts)==len(set(texts))
    assert abs(sum(p.estimated_speaking_time for p in plans)-300)<.1


def test_dense_and_fixed_order():
    r=PresentationRequest(required_sections=['甲','乙','丙'],target_slide_count=12)
    fs=extract_facts(text_blocks('# 甲\n'+'\n'.join(f'项目{i}完成率 87.6%，已完成接入。' for i in range(12))))
    outline=plan_outline(r,fs);plans=plan_slides(r,fs,outline)
    order=list(dict.fromkeys(p.section for p in plans if p.slide_type in {'content','section'}))
    assert order==['甲','乙','丙']
    assert ''.join(fragment('测试预算87.6万元，2026-10-01完成。'*40,100))=='测试预算87.6万元，2026-10-01完成。'*40


def test_fixed_count_not_silently_exceeded():
    r=PresentationRequest(target_slide_count=2,presentation_type='work_report')
    with pytest.raises(ReportError,match='CONSTRAINT_CONFLICT'):plan_outline(r,[])
