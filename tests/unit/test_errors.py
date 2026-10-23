from types import SimpleNamespace
import pytest
from ppt_report_skill.cli import main
from ppt_report_skill.request import parse_request
from ppt_report_skill.models import ReportError
from ppt_report_skill.fonts import font_report


def test_concise_error_and_technical_log(tmp_path,capsys):
    output=tmp_path/'out'
    assert main(['analyze','--template',str(tmp_path/'missing.pptx'),'--output',str(output)])==2
    text=capsys.readouterr().out
    assert 'TEMPLATE_NOT_FOUND' in text and 'Traceback' not in text
    assert 'Traceback' in (output/'error.log').read_text()
    bad=tmp_path/'request.json';bad.write_text('{bad')
    assert main(['create','--request',str(bad),'--output',str(output)])==2
    assert 'INVALID_REQUEST' in capsys.readouterr().out


@pytest.mark.parametrize('data',[[],{'topic':None},{'duration':float('nan')},{'duration':True},{'presentation_type':{}},{'speaker_notes':'yes'}])
def test_invalid_request_inputs(data):
    with pytest.raises(ReportError,match='INVALID_REQUEST'):parse_request(data)


def test_missing_font_is_reported_with_fallback():
    report=font_report(SimpleNamespace(fonts=['TEST_MISSING_FONT','Arial']),{'Arial','Hiragino Sans GB'})
    assert report['missing_families']==['TEST_MISSING_FONT']
    assert report['available_fallback']=='Hiragino Sans GB'
