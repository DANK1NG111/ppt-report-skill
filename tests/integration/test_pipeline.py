from pathlib import Path
import pytest
from pptx import Presentation
from ppt_report_skill.pipeline import create_presentation


@pytest.mark.render
def test_complete_pipeline_native_table(tmp_path):
    materials=[Path('tests/fixtures/materials/sample.xlsx')]
    result=create_presentation('assets/templates/base_template.pptx',materials,{'topic':'TEST FIXTURE 原生数据汇报','presentation_type':'custom'},tmp_path/'report.pptx')
    assert result['status']=='READY_FOR_VISUAL_REVIEW' and result['qa']['errors']==0
    p=Presentation(result['path']);assert any(sh.has_table for s in p.slides for sh in s.shapes)
    assert result['rendered']['page_count']==len(p.slides)
    assert Path(result['build'],'source_facts.json').is_file()
