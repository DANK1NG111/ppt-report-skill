"""Validate explicit constraints without silently relaxing them."""
from dataclasses import fields
from .models import PresentationRequest, ReportError

TYPES = {'work_report','project_progress','academic_report','defense','custom'}


def parse_request(data):
    unknown = set(data)-{f.name for f in fields(PresentationRequest)}
    if unknown:
        raise ReportError('INVALID_REQUEST',f'未知请求字段：{", ".join(sorted(unknown))}')
    request=PresentationRequest(**data)
    if request.presentation_type is not None and request.presentation_type not in TYPES:
        raise ReportError('INVALID_REQUEST','不支持的汇报类型。')
    if request.template_mode not in {'STRICT_TEMPLATE','FLEXIBLE_TEMPLATE'}:
        raise ReportError('INVALID_REQUEST','模板模式必须是 STRICT_TEMPLATE 或 FLEXIBLE_TEMPLATE。')
    if request.duration is not None and (not isinstance(request.duration,(int,float)) or request.duration<=0):
        raise ReportError('INVALID_REQUEST','时长必须是正数，单位为分钟。')
    if request.target_slide_count is not None and (type(request.target_slide_count) is not int or request.target_slide_count<1):
        raise ReportError('INVALID_REQUEST','目标页数必须是正整数，包含封面和结尾。')
    for key in ['required_sections','focus_points','must_include']:
        value=getattr(request,key)
        if not isinstance(value,list) or any(not isinstance(x,str) or not x.strip() for x in value):
            raise ReportError('INVALID_REQUEST',f'{key} 必须是非空字符串列表。')
    if len(set(request.required_sections)) != len(request.required_sections):
        raise ReportError('INVALID_REQUEST','固定目录不能包含重复章节。')
    return request
