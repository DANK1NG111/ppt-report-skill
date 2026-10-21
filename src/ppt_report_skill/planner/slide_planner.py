"""Allocate evidence without silently losing facts or changing constraints."""
import re
from ppt_report_skill.models import SlidePlan,ReportError
from .outline import assign_facts
from .timing import speaking_times


def fragment(text,limit):
    result=[]
    while len(text)>limit:
        candidates=[m.end() for m in re.finditer(r'[，,；;。！？\s]',text[:limit]) if m.end()>limit*.4]
        cut=max(candidates,default=limit)
        # Do not split a decimal, date, number, or Latin identifier.
        while cut>1 and re.match(r'[A-Za-z0-9.%/-]',text[cut-1]) and re.match(r'[A-Za-z0-9.%/-]',text[cut]):cut-=1
        if cut<=1:raise ReportError('CONTENT_TOO_LONG','单个不可拆分标识超出页面容量，请提供简短标签。')
        result.append(text[:cut]);text=text[cut:]
    if text:result.append(text)
    return result


def plan_slides(request,facts,outline,profile=None,max_chars=280):
    groups=assign_facts(request,facts,outline.sections,outline.presentation_type)
    pages=[]
    for section,group in groups.items():
        chunks=[];seen=set()
        for fact in sorted(group,key=lambda f:-f.importance):
            if fact.content in seen:continue
            seen.add(fact.content)
            for text in fragment(fact.content,max_chars):chunks.append((fact,text))
        packed=[];batch=[];size=0
        for item in chunks:
            if batch and (size+len(item[1])>max_chars or len(batch)>=3):packed.append(batch);batch=[];size=0
            batch.append(item);size+=len(item[1])
        if batch:packed.append(batch)
        if not packed:packed=[[]]
        for j,items in enumerate(packed):
            title=section if len(packed)==1 else f'{section}（{j+1}）'
            texts=[text for _,text in items] or [f'[待补充：{section}的材料与证据]']
            refs=[dict(fact_id=f.id,source=f.source,location=f.location,original_text=f.original_text) for f,_ in items]
            importance=max([f.importance for f,_ in items] or [1])
            pages.append(SlidePlan(0,section,'content',title,texts[0],[f.id for f,_ in items],refs,
                importance=importance,payload={'text_items':texts}))
    target=outline.target_slide_count
    if target==1:
        items=[f.content for f in facts]
        if sum(map(len,items))>max_chars or len(items)>5 or len(outline.sections)>1:
            raise ReportError('CONSTRAINT_CONFLICT','单页容量不足以保留全部必选内容。')
        pages=[SlidePlan(1,outline.sections[0],'content',request.topic,items[0] if items else '[待补充：汇报材料]',[f.id for f in facts],[dict(fact_id=f.id,source=f.source,location=f.location,original_text=f.original_text) for f in facts],payload={'text_items':items})]
    else:
        minimum=len(pages)+2
        if target<minimum:
            if request.target_slide_count is not None:
                raise ReportError('CONSTRAINT_CONFLICT',f'保留全部证据至少需要 {minimum} 页，目标为 {target} 页。')
            target=minimum;outline.target_slide_count=target
            outline.assumptions.append(f'材料容量要求将页数增加到 {target}。')
        remaining=target-minimum
        toc=[]
        if remaining:
            # Each real contents layout may have a finite number of slots.
            slots=4
            if profile:
                candidates=[l for l in profile.layouts if l.layout_type=='contents']
                if candidates:
                    candidate=candidates[0]
                    boxes=([candidate.title_box] if candidate.title_box else [])+candidate.body_boxes
                    slots=max(1,len([b for b in boxes if len(b['text'].strip())>1 and not re.search(r'contents|目录',b['text'],re.I)]))
            needed=(len(outline.sections)+slots-1)//slots
            if needed<=remaining:
                for start in range(0,len(outline.sections),slots):
                    toc.append(SlidePlan(0,'目录','contents','目录','汇报目录',[],[],layout_requirement='contents',payload={'text_items':outline.sections[start:start+slots],'start_index':start+1}))
                remaining-=needed
        while remaining:
            splittable=next((p for p in pages if p.slide_type=='content' and len(p.payload.get('text_items',[]))>1),None)
            if splittable:
                texts=splittable.payload['text_items'];cut=(len(texts)+1)//2
                second=SlidePlan(0,splittable.section,'content',splittable.section+'（续）',texts[cut],splittable.supporting_facts[cut:],splittable.source_refs[cut:],importance=splittable.importance,payload={'text_items':texts[cut:]})
                splittable.payload['text_items']=texts[:cut];splittable.supporting_facts=splittable.supporting_facts[:cut];splittable.source_refs=splittable.source_refs[:cut]
                pages.insert(pages.index(splittable)+1,second)
            else:
                section=outline.sections[(remaining-1)%len(outline.sections)]
                position=max(i for i,p in enumerate(pages) if p.section==section)+1
                label=f'[待补充：{section}的补充证据]'
                pages.insert(position,SlidePlan(0,section,'content',section+'补充',label,[],[],payload={'text_items':[label]}))
            remaining-=1
        pages=[SlidePlan(0,'封面','cover',request.topic,request.topic,[],[],layout_requirement='cover'),*toc,*pages,SlidePlan(0,'结束','closing','感谢聆听','感谢聆听',[],[],layout_requirement='closing')]
    for n,page in enumerate(pages,1):page.slide_number=n
    speaking_times(pages,request.duration or outline.estimated_duration)
    return pages
