#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import re
import logging
import requests
import pymysql
from multiprocessing import Pool
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from PIL import Image
from PIL import ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)

connection = pymysql.connect(host="101.32.202.66", user="root", password="1q2w3e4r..A", port=3306, db="db_yy_1",
                             connect_timeout=10, write_timeout=10)


def action(tab, vid, uri):
    if not os.path.exists('tmp'):
        os.mkdir('tmp')
    try:
        if str(uri).endswith('jpg') or str(uri).endswith('JPG') or str(uri).endswith('jpeg') or str(uri).endswith(
                'JPEG') or str(uri).endswith('png') or str(uri).endswith('PNG'):
            filename = re.split('/', uri)[-1]
            bucketUrl = "https://sourcefile-1304080031.cos.accelerate.myqcloud.com"
            if download(bucketUrl + uri, f'tmp/{filename}'):
                name = re.split('\.', filename)[0]
                filetype = re.split('\.', filename)[-1]
                if decrypt(f'tmp/{filename}', f'tmp/{name}-decrypt.{filetype}'):
                    if compress(f'tmp/{name}-decrypt.{filetype}', f'tmp/{name}-compress.{filetype}'):
                        if encrypt(f'tmp/{name}-compress.{filetype}', f'tmp/{name}-encrypt.{filetype}'):
                            file_uri = re.split('\.', uri)[0] + '-compress.' + re.split('\.', uri)[-1]
                            if upload(bucketUrl, f'tmp/{name}-encrypt.{filetype}', file_uri):
                                if update(tab, vid, file_uri):
                                    logging.info(f"处理完成 {uri}")
    except Exception as e:
        logging.error(f"全局异常 {e}")


def download(url, dfile):
    try:
        with open(dfile, 'wb') as f:
            f.write(requests.get(url, timeout=30).content)
        return True
    except Exception as e:
        logging.error(f"下载异常 {url} {e}")
        return False


def decrypt(sfile, dfile):
    try:
        data = open(sfile, 'rb')
        with open(dfile, 'wb') as enc:
            enc.write(data.read()[8:-1])
            data.close()
            _del(sfile)
        tm = open(dfile, 'rb')
        try:
            Image.open(tm)
            tm.close()
            return True
        except:
            logging.debug(f"图片解密失败 {sfile}")
            tm.close()
            _del(dfile)
            return False
    except Exception as e:
        _del(sfile)
        logging.error(f"解密异常 {sfile} {e}")
        return False


def compress(sfile, dfile, zoom_ratio=0.5):
    imfile = open(sfile, 'rb')
    try:
        img = Image.open(imfile)
        w, h = img.size
        filesize = os.path.getsize(sfile) / float(1024)  # K
        if w <= 959 or h <= 540 or filesize <= 300:
            logging.debug(f"封面已经足够小了, 不再处理 {w}x{h} {filesize}K {sfile}")
            imfile.close()
            _del(sfile)
            return False

        if sfile.endswith('png') or sfile.endswith('PNG'):
            img_resize = img.resize((int(w * zoom_ratio), int(h * zoom_ratio)), resample=Image.ANTIALIAS)
            resize_w, resize_h = img_resize.size
            img_resize.save(dfile, 'png', quality=80, optimize=True)
        elif sfile.endswith('jpg') or sfile.endswith('jpeg') or sfile.endswith('JPG') or sfile.endswith('JPEG'):
            img = img.convert('RGB')
            img_resize = img.resize((int(w * zoom_ratio), int(h * zoom_ratio)), resample=Image.ANTIALIAS)
            resize_w, resize_h = img_resize.size
            img_resize.save(dfile, 'jpeg', quality=80, optimize=True)
        else:
            logging.debug(f"封面格式非PNG/JPG, 跳过 {sfile}")
            imfile.close()
            _del(sfile)
            return False
        s_size = "%.2f" % (filesize / 1024)
        d_size = "%.2f" % (os.path.getsize(dfile) / float(1024 * 1024))
        logging.info(f"压缩完成 压缩率 {zoom_ratio} 尺寸 {w}x{h} -> {resize_w}x{resize_h} {s_size}M -> {d_size}M, {sfile}")
        imfile.close()
        _del(sfile)
        return True
    except Exception as e:
        logging.error(f"压缩异常 {sfile} {e}")
        imfile.close()
        _del(sfile)
        _del(dfile)
        return False


def encrypt(sfile, dfile):
    try:
        data = open(sfile, 'rb')
        key = os.urandom(8)
        with open(dfile, 'wb') as enc:
            enc.write(key)
            enc.write(data.read())
        data.close()
        _del(sfile)
        return True
    except Exception as e:
        _del(sfile)
        logging.error(f"加密异常 {sfile} {e}")
        return False


def upload(bucketUrl, sfile, uri):
    try:
        if requests.get(bucketUrl + uri).status_code == 404:
            secret_id = 'AKIDc084lCWN1SeaFnp2NSFnWy81fm2EF4pK'
            secret_key = 'NAiAST3RovlMbZIl2yZu87pJ7i3C7wiF'
            region = 'ap-hongkong'
            domain = 'sourcefile-1304080031.cos.accelerate.myqcloud.com'
            client = CosS3Client(CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Domain=domain))
            cos_bucket = 'sourcefile-1304080031'
            client.upload_file(
                Bucket=cos_bucket,
                LocalFilePath=sfile,
                Key=uri,
                PartSize=1,
                MAXThread=10,
                EnableMD5=False
            )
        else:
            logging.warning(f"文件已存在, 跳过上传 {bucketUrl + uri}")
        _del(sfile)
        return True
    except Exception as e:
        _del(sfile)
        logging.error(f"上传失败 {e}")
        return False


def update(tab, vid, uri):
    try:
        with connection.cursor() as cur:
            sql = f"update {tab} set cover_uri='{uri}' where vid={vid}"
            cur.execute(sql)
            connection.commit()
        return True
    except Exception as e:
        logging.error(e)
        return False


def _del(sfile):
    if os.path.exists(sfile):
        os.remove(sfile)


def getList(connection):
    with connection.cursor() as cur:
        sql = f"select vid,cover_uri from t_video where video_type=1;"
        cur.execute(sql)
        return cur.fetchall()


if __name__ == '__main__':
    vres = getList(connection)
    p = Pool(4)
    for data in vres:
        p.apply_async(action, args=('t_video', data[0], data[1]))
    p.close()
    p.join()

    # action('t_video', 35450, '/movie/jp-rok/Mao-Hamasaki/MACB-016/MACB-016.jpg')
