from ppt_report_skill.models import ReportError

COMPATIBLE={'comparison':['comparison','two_column'],'summary':['summary','title_content'],'image_text':['image_text','image_full'],'data':['data','chart','table'],'chart':['chart','data','title_content'],'table':['table','data','title_content'],'process':['process','timeline','title_content']}


def score_layout(plan,layout):
    if 'exclude_from_generation' in layout.secondary_tags:return -10000
    desired=plan.layout_requirement
    score=100 if layout.layout_type==desired else 65 if layout.layout_type in COMPATIBLE.get(desired,[]) or desired in layout.secondary_tags else 0
    if desired in {'cover','contents','section','closing'} and layout.layout_type!=desired:score-=500
    if desired not in {'cover','contents','section','closing'} and layout.layout_type in {'cover','contents','section','closing','unknown'}:score-=500
    size=sum(len(x) for x in plan.payload.get('text_items',[]))
    if size>layout.max_content_size and desired not in {'cover','section','closing'}:score-=150
    elif size<=layout.recommended_content_size:score+=15
    if plan.visual_type=='image':score+=35 if layout.image_boxes else -30
    if plan.visual_type=='chart':score+=30 if layout.chart_boxes else 0
    if plan.visual_type=='table':score+=30 if layout.table_boxes else 0
    if plan.visual_type=='text':score-=10*len(layout.image_boxes)
    score+=min(layout.recommended_content_size/100,10)
    return score


def match_layout(plan,profile,mode='STRICT_TEMPLATE'):
    if not profile.layouts:raise ReportError('LAYOUT_NOT_FOUND','模板没有可用页面。')
    layout=max(profile.layouts,key=lambda l:score_layout(plan,l))
    if score_layout(plan,layout)<0:
        raise ReportError('LAYOUT_NOT_FOUND',f'模板缺少 {plan.layout_requirement} 版式，请映射模板档案或使用 FLEXIBLE_TEMPLATE。')
    plan.layout_id=layout.layout_id
    return layout
