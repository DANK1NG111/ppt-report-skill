"""Derive layouts from a real content page only when explicitly enabled."""
from copy import deepcopy


def extend_layouts(profile,mode):
    if mode!='FLEXIBLE_TEMPLATE':return profile
    usable=[l for l in profile.layouts if l.title_box and l.body_boxes and 'exclude_from_generation' not in l.secondary_tags]
    if not usable:return profile
    source=max(usable,key=lambda l:l.recommended_content_size)
    present={l.layout_type for l in profile.layouts}
    for kind in ['cover','contents','section','closing','image_text','table','chart','process','summary','comparison']:
        if kind in present:continue
        layout=deepcopy(source);layout.layout_id=f'flex-{kind}-{source.source_slide}';layout.layout_type=kind
        layout.secondary_tags=['flexible_derived'];layout.layout_name=f'{source.layout_name} / {kind}'
        if kind in {'cover','section','closing'}:
            layout.title_box.update(x=int(profile.slide_width*.08),y=int(profile.slide_height*.34),width=int(profile.slide_width*.84),height=int(profile.slide_height*.22))
        if kind=='image_text' and not layout.image_boxes:
            body=max(layout.body_boxes,key=lambda b:b['width']*b['height'])
            layout.image_boxes=[{**body,'shape_id':-1}]
        profile.layouts.append(layout)
    return profile
