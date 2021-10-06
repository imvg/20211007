# -*- coding: utf-8 -*-
import logging
import os
import re

import pytesseract
from PIL import Image
from PIL import ImageEnhance


logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


def iden(file):
    img = Image.open(file)
    img = img.convert('RGB')
    enhancer = ImageEnhance.Color(img)
    enhancer = enhancer.enhance(0)
    enhancer = ImageEnhance.Brightness(enhancer)
    enhancer = enhancer.enhance(2)
    enhancer = ImageEnhance.Contrast(enhancer)
    enhancer = enhancer.enhance(8)
    enhancer = ImageEnhance.Sharpness(enhancer)
    img = enhancer.enhance(20)
    imgdata = pytesseract.image_to_string(img)
    img.close()
    imgstr = imgdata.replace('\n', '')
    for vnum in re.split(' ', imgstr):
        if re.match('\w\w\d\d\d\d', vnum):
            logging.info(f"{file} 番号 {vnum}")
            return True
        elif re.match('\w\w\w\d\d\d\d', vnum):
            logging.info(f"{file} 番号 {vnum}")
            return True
        elif re.match('\w\w\w\w\d\d\d\d', vnum):
            logging.info(f"{file} 番号 {vnum}")
            return True
        elif re.match('\w\w\w\w\d\d\d\d', vnum):
            logging.info(f"{file} 番号 {vnum}")
            return True
    logging.info(f"{file} 识别失败 {imgstr}")
    return False


for file in os.listdir('./tmp'):
    if not file.startswith('.'):
        iden(f'tmp/{file}')
