from PIL import Image


def png2ico(png_path, ico_path):
    """
    @param png_path: png文件路径
    @param ico_path: ico文件路径
    """
    im = Image.open(png_path)
    im.save(ico_path, 'ICO')


png_path = 'C:\\Users\\iou17\\Desktop\\便当摇杆.png'
ico_path = 'C:\\Users\\iou17\\Desktop\\便当摇杆.ico'
png2ico(png_path, ico_path)