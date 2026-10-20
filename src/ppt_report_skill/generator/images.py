from pathlib import Path
from PIL import Image,ImageOps
from ppt_report_skill.models import ReportError


def add_image(slide,path,box,fit='contain'):
    if fit not in {'contain','crop','center_crop','fill'}:raise ReportError('INVALID_IMAGE_FIT','图片 fit 策略不支持。')
    path=Path(path)
    try:
        with Image.open(path) as image:
            width,height=image.size
            if image.getexif().get(274,1)!=1:
                raise ReportError('IMAGE_ORIENTATION','请先将照片旋转方向保存到图像像素。')
    except ReportError:raise
    except Exception as exc:raise ReportError('INVALID_IMAGE','图片无法读取。',str(exc)) from exc
    x,y,w,h=(int(box[k]) for k in ['x','y','width','height'])
    ratio=width/height
    if fit=='contain':
        if w/h>ratio:nw,nh=int(h*ratio),h
        else:nw,nh=w,int(w/ratio)
        picture=slide.shapes.add_picture(str(path),x+(w-nw)//2,y+(h-nh)//2,nw,nh)
    else:
        picture=slide.shapes.add_picture(str(path),x,y,w,h)
        if ratio>w/h:
            crop=(1-(w/h)/ratio)/2;picture.crop_left=picture.crop_right=crop
        else:
            crop=(1-ratio/(w/h))/2;picture.crop_top=picture.crop_bottom=crop
    return picture


def replace_picture(slide,picture,path,fit='center_crop'):
    box=dict(x=picture.left,y=picture.top,width=picture.width,height=picture.height)
    new=add_image(slide,path,box,fit)
    element=picture._element;element.getparent().remove(element)
    return new
