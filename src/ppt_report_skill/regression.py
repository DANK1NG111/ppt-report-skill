"""One command runs every test category and real-template scenario."""
from pathlib import Path
import json
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from .models import save_json


def run_regression(root=None):
    root=Path(root or Path(__file__).resolve().parents[2]).resolve()
    output=root/'output/regression';output.mkdir(parents=True,exist_ok=True)
    start=time.monotonic()
    process=subprocess.run([sys.executable,'-m','pytest','-q','--junitxml',str(output/'pytest.xml')],cwd=root,capture_output=True,text=True,timeout=600)
    (output/'pytest.log').write_text(process.stdout+process.stderr)
    counts={};categories={}
    if (output/'pytest.xml').exists():
        xml=ET.parse(output/'pytest.xml')
        for suite in xml.iter('testsuite'):
            for field in ['tests','failures','errors','skipped']:counts[field]=counts.get(field,0)+int(suite.get(field,0))
        groups={'material':['loader'],'template':['template'],'fact':['facts','draft'],'planning':['outline','slide_planner','type','requests'],'layout':['matcher','text','images','tables','charts','shapes','flexible'],'generation':['generation','pipeline'],'validation':['validator','visual'],'render':['render','repair']}
        cases=list(xml.iter('testcase'))
        for group,words in groups.items():categories[group]=sum(any(word in c.get('classname','') for word in words) for c in cases)
    real=None
    if process.returncode==0:
        real_process=subprocess.run([sys.executable,'scripts/run_real_template_cases.py'],cwd=root,capture_output=True,text=True,timeout=600)
        (output/'real_template.log').write_text(real_process.stdout+real_process.stderr)
        if real_process.returncode==0:real=json.loads((root/'output/real_template_cases/real_template_report.json').read_text())
    passed=process.returncode==0 and all(categories.values()) and real is not None and real['status']=='PASS'
    report={'status':'PASS' if passed else 'FAIL','pytest_returncode':process.returncode,'counts':counts,'categories':categories,'real_template':real,'elapsed_seconds':round(time.monotonic()-start,2)}
    save_json(report,output/'regression_report.json')
    (output/'regression_report.md').write_text('# Regression report\n\n'+report['status']+'\n\n'+json.dumps({'counts':counts,'categories':categories,'elapsed_seconds':report['elapsed_seconds']},ensure_ascii=False,indent=2)+'\n\n详细证据见 pytest.log、pytest.xml、real_template.log 和 regression_report.json。\n')
    return report
