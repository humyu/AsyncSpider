# -*- coding: utf-8 -*-
"""图像识别测试方法"""

import tesserocr
from PIL import Image
import requests


def img_recognition(url):
    """将图片下载至本地进行图像识别"""
    r = requests.get(url)
    with open('img.png', 'wb') as f:
        f.write(r.content)
    image = Image.open("img.png")
    result = tesserocr.image_to_text(image)
    return result
