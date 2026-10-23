"""Complete authoring pipeline. Auto-QA and human visual review remain distinct."""
from dataclasses import asdict
from copy import deepcopy
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import shutil
import uuid
from ppt_report_skill.models import MaterialBlock,SourceFact,SlidePlan,ReportError,Issue,save_json
from ppt_report_skill.request import parse_request
from ppt_report_skill.template.analyzer import analyze_template
from ppt_report_skill.template.profile import cached_profile
from ppt_report_skill.content.loader import load_materials
from ppt_report_skill.content.facts import extract_facts,detect_conflicts
from ppt_report_skill.planner.outline import plan_outline,assign_facts
from ppt_report_skill.planner.slide_planner import plan_slides
from ppt_report_skill.planner.timing import speaking_times
from ppt_report_skill.generator.presentation import generate_presentation
from ppt_report_skill.generator.tables import table_pages
from ppt_report_skill.repair import repair_loop
from ppt_report_skill.layout.flexible import extend_layouts
from ppt_report_skill.fonts import font_report
from ppt_report_skill.validator.presentation import write_report


def native_plans(blocks,request,facts,outline,max_rows=6):
    pages=[];excluded=set()
    def section_for(block):
        group=assign_facts(request,[SourceFact('x',block.text,block.source,block.location,'data',block.text,section=block.section)],outline.sections,outline.presentation_type)
        return next(s for s,fs in group.items() if fs)
    for block in blocks:
        matching=[f for f in facts if f.source==block.source and f.location==block.location]
        refs=[dict(fact_id=f.id,source=f.source,location=f.location,original_text=f.original_text) for f in matching]
        section=section_for(block)
        if block.kind=='table' and block.rows and len(block.rows)>1:
            excluded.update(f.id for f in matching)
            for rows in table_pages(block.rows,max_rows=max_rows):
                pages.append(SlidePlan(0,section,'content',section+'数据',section, [f.id for f in matching],refs,visual_type='table',layout_requirement='table',importance=3,payload={'rows':rows}))
        if block.kind=='image' and block.image_path:
            pages.append(SlidePlan(0,section,'content',section+'图示',section,[],[dict(fact_id='image-'+hashlib.sha256(block.image_path.encode()).hexdigest()[:12],source=block.source,location=block.location,original_text='用户材料图片')],visual_type='image',layout_requirement='image_text',payload={'image':block.image_path}))
    for i,visual in enumerate(request.visuals):
        section=visual.get('section',outline.sections[0])
        if section not in outline.sections:raise ReportError('INVALID_REQUEST',f'visuals[{i}].section 不在目录内。')
        kind=visual['type'];title=visual.get('title',section)
        original=json.dumps(visual,ensure_ascii=False)
        refs=[dict(fact_id=f'request-visual-{i}',source='<user request>',location=f'visuals[{i}]',original_text=original)]
        data=visual.get('data',{})
        payload={'image':visual.get('path'),'fit':visual.get('fit','contain')} if kind=='image' else {'rows':data.get('rows',[])} if kind=='table' else {kind:deepcopy(data)}
        pages.append(SlidePlan(0,section,'content',title,title,[],refs,visual_type=kind,layout_requirement='image_text' if kind=='image' else 'process' if kind=='diagram' else kind,importance=3,payload=payload))
    return pages,excluded


def combine_plans(request,facts,outline,profile,blocks,max_chars,max_rows):
    native,excluded=native_plans(blocks,request,facts,outline,max_rows)
    text_facts=[f for f in facts if f.id not in excluded]
    local_request=deepcopy(request);local_outline=deepcopy(outline)
    # Reserve explicit total-page space for native evidence before text planning.
    if native:
        if request.target_slide_count:
            local_request.target_slide_count=request.target_slide_count-len(native)
            local_outline.target_slide_count=local_request.target_slide_count
        else:local_outline.target_slide_count=max(len(outline.sections)+2,outline.target_slide_count-len(native))
    plans=plan_slides(local_request,text_facts,local_outline,profile,max_chars=max_chars)
    for section in outline.sections:
        additions=[p for p in native if p.section==section]
        if not additions:continue
        placeholders=[p for p in plans if p.section==section and p.slide_type=='content' and all(t.startswith('[待补充') for t in p.payload.get('text_items',[]))]
        for p in placeholders:plans.remove(p)
        index=max([i for i,p in enumerate(plans) if p.section==section]+[next((i for i,p in enumerate(plans) if p.slide_type=='closing'),len(plans))-1])+1
        plans[index:index]=additions
    if request.target_slide_count and len(plans)!=request.target_slide_count:
        if len(plans)>request.target_slide_count:raise ReportError('CONSTRAINT_CONFLICT',f'原生对象与必选章节至少需要 {len(plans)} 页，目标为 {request.target_slide_count} 页。')
        # Use existing section dividers to honor an explicitly larger count.
        while len(plans)<request.target_slide_count:
            section=outline.sections[(len(plans)-1)%len(outline.sections)]
            index=next(i for i,p in enumerate(plans) if p.section==section)
            plans.insert(index,SlidePlan(0,section,'section',section,section,[],[],layout_requirement='section'))
    for n,p in enumerate(plans,1):p.slide_number=n
    outline.target_slide_count=len(plans)
    speaking_times(plans,request.duration or outline.estimated_duration)
    return plans


def create_presentation(template,materials,request_data,output,direct_text=None):
    output=Path(output).resolve();run_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8]
    build=output.parent/'build'/run_id;build.mkdir(parents=True,exist_ok=True)
    request=parse_request(request_data);profile,cache=cached_profile(template,output.parent/'template_cache',build/'template_profile.json')
    save_json(cache,build/'template_cache_receipt.json')
    profile=extend_layouts(profile,request.template_mode)
    save_json(profile,build/'template_profile.json')
    blocks=load_materials(materials,direct_text,build/'material_images')
    facts=extract_facts(blocks,request.focus_points)
    if not facts:raise ReportError('MATERIAL_EMPTY','材料中没有可用于汇报的文字事实。')
    conflicts=detect_conflicts(facts)
    for name,value in [('request',request),('material_blocks',[asdict(b) for b in blocks]),('source_facts',[asdict(f) for f in facts]),('conflicts',conflicts)]:save_json(value,build/f'{name}.json')
    save_json({'build':str(build),'run_id':run_id},output.parent/'build/latest.json')
    if conflicts:raise ReportError('CONTENT_CONFLICT',f'材料数值冲突，详见 {build}/conflicts.json。')
    for required in request.must_include:
        if not any(required in f.content for f in facts):raise ReportError('REQUIRED_CONTENT_MISSING',f'材料缺少必选信息：{required}')
    outline=plan_outline(request,facts,profile);attempts=[]
    for attempt,(chars,rows) in enumerate([(280,6),(160,3),(90,2)],1):
        try:
            plans=combine_plans(request,facts,outline,profile,blocks,chars,rows)
            path=generate_presentation(template,profile,plans,request,build/f'candidate-{attempt}.pptx',build)
            attempts.append({'attempt':attempt,'status':'GENERATED','max_chars':chars,'max_rows':rows})
            break
        except ReportError as exc:
            attempts.append({'attempt':attempt,'code':exc.code,'detail':exc.detail})
            if exc.code not in {'TEXT_OVERFLOW','TABLE_OVERFLOW','LAYOUT_CAPACITY'} or attempt==3:
                save_json(attempts,build/'generation_attempts.json');raise
    save_json(outline,build/'outline.json');save_json(attempts,build/'generation_attempts.json')
    repaired=repair_loop(path,build/'repair',plans,request,profile)
    fonts=font_report(profile);save_json(fonts,build/'font_report.json')
    if fonts['missing_families']:
        repaired['report']['warnings']+=1
        repaired['report']['issues'].append({'code':'FONT_MISSING','severity':'warning','message':'模板部分字体本机未安装；PPTX 声明保留，渲染使用替代字体，详见 font_report.json。','slide':None,'shape_id':None,'repaired':False})
        if repaired['report']['errors']==0:repaired['report']['status']='PASS_WITH_WARNINGS'
    write_report([Issue(**i) for i in repaired['report']['issues']],output.parent)
    if not repaired['resolved']:raise ReportError('QA_FAILED',f'自动修复后仍有 {repaired["report"]["errors"]} 项 Error，详见 {build}/repair。')
    output.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(repaired['path'],output)
    result={'status':'READY_FOR_VISUAL_REVIEW','path':str(output),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'build':str(build),'slide_count':len(plans),'qa':repaired['report'],'rendered':repaired['rendered'],'assumptions':outline.assumptions,'presentation_type':outline.presentation_type,'template':str(Path(template).resolve()),'sources':sorted({f.source for f in facts}),'fonts':fonts}
    save_json(result,build/'pipeline_receipt.json');save_json(result,output.parent/'pipeline_receipt.json')
    return result
