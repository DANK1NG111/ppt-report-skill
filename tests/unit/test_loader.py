from pathlib import Path
import pytest
from ppt_report_skill.content.loader import load_material,load_materials
from ppt_report_skill.models import ReportError


@pytest.mark.parametrize('suffix',['txt','md','docx','pdf','pptx','xlsx'])
def test_formats(suffix):
    blocks=load_material(Path('tests/fixtures/materials')/f'sample.{suffix}')
    text='\n'.join(b.text for b in blocks)
    assert '87.6%' in text and '2026' in text and '12' in text
    assert all(b.location and b.source for b in blocks)


def test_direct_text_and_empty():
    assert load_materials(direct_text='# 目标\n完成率 87.6%')[1].section=='目标'
    with pytest.raises(ReportError,match='MATERIAL_EMPTY'):load_materials()


def test_docx_order():
    b=load_material('tests/fixtures/materials/sample.docx')
    assert [x.kind for x in b]==['heading','paragraph','table','paragraph']
