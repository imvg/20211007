#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import random
import logging
import re
import time

import pymysql
import requests
from multiprocessing import Pool
from PIL import Image
from numpy import average, dot, linalg

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.WARNING)


def ranstr(num):
    H = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    salt = ''
    for i in range(num):
        salt += random.choice(H)
    return salt


def get_thum(image, size=(64, 64), greyscale=False):
    try:
        image = image.resize(size, Image.ANTIALIAS)
        if greyscale:
            image = image.convert('L')
        return image
    except Exception as e:
        logging.error(f"图片转换异常 {e} {image}")
        return False


def getFile(url):
    try:
        data = requests.get(url).content
        res = data[8:]
        filename = ranstr(8)
        filetype = re.split('\.', url)[-1]
        with open(f'tmp/{filename}.{filetype}', 'wb') as f:
            f.write(res)
        return f'tmp/{filename}.{filetype}'
    except Exception as e:
        logging.error(f"文件获取失败 {e}")
        return False


def repeat(image1, image2):
    try:
        img1data = getFile(image1)
        img2data = getFile(image2)
        if not img1data or not img2data:
            return False
        image1 = get_thum(Image.open(img1data))
        image2 = get_thum(Image.open(img2data))
        if not image1 or not image2:
            return False
        images = [image1, image2]
        vectors = []
        norms = []
        for image in images:
            vector = []
            for pixel_tuple in image.getdata():
                vector.append(average(pixel_tuple))
            vectors.append(vector)
            norms.append(linalg.norm(vector, 2))
        a, b = vectors
        a_norm, b_norm = norms
        res = dot(a / a_norm, b / b_norm)
        os.remove(img1data)
        os.remove(img2data)
        return res
    except Exception as e:
        logging.error(f"图片识别异常 {e} {image1} {image2}")
        return False


def getImages():
    try:
        conn = pymysql.connect(host="hk-cdb-aumsfh1d.sql.tencentcdb.com", user="root", password="wvqhthpbd!Wv$da4", port=63734, db="db_yy", connect_timeout=10, write_timeout=10)
        with conn.cursor() as cur:
            sql = 'select vid,cover_uri from t_video where status>-2 and video_type=1;'
            cur.execute(sql)
            res = cur.fetchall()
            conn.commit()
            return res
    except Exception as e:
        logging.error(f"数据库连接失败 {e}")


def controler(data):
    try:
        time.sleep(0.1)
        rootimage = data['root']['path']
        rootvid = data['root']['vid']
        objimage = data['obj']['path']
        objvid = data['obj']['vid']
        if rootvid != objvid and len(rootimage) > 8 and len(objimage) > 8:
            cosin = repeat(rootimage, objimage)
            if float(cosin) >= 0.98:
                logging.warning(f"<图像识别提醒> 视频 {rootvid} {objvid} 可能是重复的 {cosin}")
            else:
                logging.info(f"检查结果 {rootvid} <-> {objvid} Resource: {cosin}")
    except Exception as e:
        logging.error(f"全局异常 {e}")


if __name__ == '__main__':
    sourceDomain = "https://sourcefile-1304080031.cos.ap-hongkong.myqcloud.com"
    p = Pool(4)
    logging.info(f"任务开始...")
    images = getImages()
    logging.info(f"已获取到所有视频信息")
    for rootimage in images:
        for objimage in images:
            data = {'root': {'path': f'{sourceDomain}{rootimage[1]}', 'vid': rootimage[0]},
                    'obj': {'path': f'{sourceDomain}{objimage[1]}', 'vid': objimage[0]}}
            p.apply_async(controler, args=(data,))
    p.close()
    p.join()
    logging.info(f"任务结束")
