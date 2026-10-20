from pathlib import Path
from PIL import Image, ImageDraw


def contact_sheet(images, output, columns=3):
    width, height = 480, 294
    sheet = Image.new("RGB", (width*columns, height*((len(images)+columns-1)//columns)), "#eeeeee")
    draw = ImageDraw.Draw(sheet)
    for i, file in enumerate(images):
        with Image.open(file) as image:
            image.thumbnail((460, 259))
            x, y = i % columns*width+10, i//columns*height+24
            sheet.paste(image.convert("RGB"), (x,y))
            draw.text((x,y-18), str(i+1), fill="black")
    sheet.save(output)
    return Path(output)
