import json
from pathlib import Path
import pytest
from ppt_report_skill.request import parse_request
from ppt_report_skill.models import ReportError

CASES=json.loads(Path('tests/fixtures/request_cases.json').read_text())


@pytest.mark.parametrize('case',CASES,ids=lambda c:c['id'])
def test_request_policy(case):
    if case.get('error'):
        with pytest.raises(ReportError): parse_request(case['request'])
    else:
        r=parse_request(case['request'])
        assert r.template_mode in {'STRICT_TEMPLATE','FLEXIBLE_TEMPLATE'}
        assert r.required_sections == case['request'].get('required_sections',[])
        assert case['strategy']
