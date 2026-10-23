"""Content-addressed profile cache invalidated by analyzer implementation changes."""
import hashlib
import json
from pathlib import Path
from ppt_report_skill.models import TemplateProfile,ReportError,save_json
from .analyzer import analyze_template


def cached_profile(path,cache_dir,output=None):
    path=Path(path).resolve();cache_dir=Path(cache_dir)
    if not path.is_file():raise ReportError('TEMPLATE_NOT_FOUND',f'模板不存在：{path}')
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    version=hashlib.sha256(b''.join(p.read_bytes() for p in [Path(__file__).with_name('analyzer.py'),Path(__file__).with_name('classifier.py'),Path(__file__).parents[1]/'models.py'])).hexdigest()[:12]
    cached=cache_dir/f'{digest}-{version}.json';profile=None;hit=False
    if cached.exists():
        try:
            profile=TemplateProfile.from_dict(json.loads(cached.read_text()))
            if profile.sha256!=digest:profile=None
            else:hit=True
        except (ValueError,TypeError,KeyError):profile=None
    if profile is None:profile=analyze_template(path,cached)
    profile.template_path=str(path)
    if output:save_json(profile,output)
    return profile,{'hit':hit,'sha256':digest,'cache_path':str(cached.resolve()),'analyzer_version':version}
