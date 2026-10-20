import pytest
from types import SimpleNamespace
from ppt_report_skill.models import LayoutProfile,SlidePlan
from ppt_report_skill.layout.matcher import match_layout


@pytest.mark.parametrize('desired',['contents','section','image_text','data','comparison','summary'])
@pytest.mark.parametrize('size',[10,50,100,200,400])
def test_30_matching_cases(desired,size):
    layouts=[LayoutProfile(k,k,k,i+1,recommended_content_size=500,max_content_size=600,image_boxes=[{}] if k=='image_text' else []) for i,k in enumerate(['contents','section','image_text','data','comparison','summary','title_content'])]
    plan=SlidePlan(1,'s','content','title','message',[],[],layout_requirement=desired,payload={'text_items':['a'*size]})
    assert match_layout(plan,SimpleNamespace(layouts=layouts)).layout_type==desired
