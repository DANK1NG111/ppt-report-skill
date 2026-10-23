from copy import deepcopy
from pathlib import Path
import pytest
from ppt_report_skill.delivery import finalize_delivery,warning_key
from ppt_report_skill.models import ReportError
from ppt_report_skill.pipeline import create_presentation


@pytest.mark.render
def test_delivery_requires_current_render_and_complete_review(tmp_path):
    result=create_presentation('assets/templates/base_template.pptx',['tests/fixtures/work_report/material.md'],{'topic':'TEST FIXTURE 交付验证','presentation_type':'work_report'},tmp_path/'final_presentation.pptx')
    review={'sha256':result['sha256'],'pages':[{'slide':i,'status':'PASS','observation':'TEST FIXTURE gate test; not real delivery evidence'} for i in range(1,result['slide_count']+1)],'facts_checked':True,'section_order_checked':True,'native_open':{'application':'Microsoft PowerPoint','repair_prompt':False,'observation':'TEST FIXTURE simulated input for gate test'},'warning_dispositions':{warning_key(i):'TEST FIXTURE disposition' for i in result['qa']['issues'] if i['severity']=='warning'}}
    bad=deepcopy(review);bad['pages'].pop()
    with pytest.raises(ReportError,match='逐页'):finalize_delivery(result,bad)
    bad=deepcopy(review);bad['warning_dispositions']={}
    with pytest.raises(ReportError,match='Warning'):finalize_delivery(result,bad)
    done=finalize_delivery(result,review,include_pdf=True)
    assert done['status']=='DELIVERED' and Path(done['pdf']).is_file()
    assert '页数' in Path(done['generation_report']).read_text()
    image=Path(result['rendered']['images'][0]);image.write_bytes(b'changed')
    with pytest.raises(ReportError,match='渲染产物'):finalize_delivery(result,review)
    Path(result['path']).write_bytes(b'changed')
    with pytest.raises(ReportError,match='PPTX'):finalize_delivery(result,review)
