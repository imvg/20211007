#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import re
import logging
from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


def compress_encrypt(img_path, rate):
    img = Image.open(img_path)
    w, h = img.size
    img_resize = img.resize((int(w*rate), int(h*rate)), resample=Image.ANTIALIAS)
    # img_resize = img.resize((788, 444), resample=Image.ANTIALIAS)
    resize_w, resize_h = img_resize.size
    tmpfile = re.split('\.', img_path)[0] + "-temp." + re.split('\.', img_path)[-1]
    img_resize.save(tmpfile, 'jpeg', quality=80, optimize=True)

    # data = open(tmpfile, 'rb').read()
    # key = os.urandom(8)
    # dfile  = re.split('\.', img_path)[0] + "-compress." + re.split('\.', img_path)[-1]
    # with open(dfile, 'wb') as enc:
    #     enc.write(key)
    #     enc.write(data)
    #
    # os.remove(tmpfile)
    s_size = "%.2f" % (os.path.getsize(img_path)/float(1024*1024))
    d_size = "%.2f" % (os.path.getsize(tmpfile)/float(1024*1024))
    logging.info(f"处理完成 压缩率 {rate} 尺寸 {w}x{h} -> {resize_w}x{resize_h} {s_size}M -> {d_size}M, {img_path}")


if __name__ == '__main__':
    img_path = '/Users/mrvg/Desktop/BLACKED_101361_480lP-decrypt.jpg'
    rate = 0.5
    compress_encrypt(img_path, rate)
