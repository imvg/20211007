# -*- coding: utf-8 -*-
import re
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import logging
import pymysql
import requests

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


def checkKey(data):
    try:
        url = f"https://vod.toutiaomil.com{data[-1]}"
        res = requests.get(url)
        for m3u8 in re.split('\n', res.text):
            if m3u8.startswith('#EXT-X-KEY'):
                key = re.split('"', re.split(',', m3u8)[1])[1]
                if not key.endswith("key") and not key.endswith("text"):
                    logging.warning(f"视频 {data[0]}, Key文件异常 {key}")
                else:
                    vodurl = '/'.join(re.split('/', data[-1])[:-1])
                    logging.info(f"检查key文件 {data[0]} {key} https://sourcefile-1304080031.cos.ap-hongkong.myqcloud.com{vodurl}/{key}")
                    keyres = requests.get(f"https://sourcefile-1304080031.cos.ap-hongkong.myqcloud.com{vodurl}/{key}")
                    if keyres.status_code != 200 or 'html' in keyres.text or 'Not' in keyres.text:
                        logging.warning(f"视频 {data[0]}, Key文件异常 {key}")
                        upfile('./1628080687645032903.text', f'{vodurl}/{key}')
    except Exception as e:
        logging.error(e)


def getVideos():
    logging.info(f"获取所有视频...")
    sql = "select vid,video_uri2 from t_video_stock where video_uri2 like '/vg/%' and vid>30085;"
    connection = pymysql.connect(host="hk-cdb-aumsfh1d.sql.tencentcdb.com", user="root", password="wvqhthpbd!Wv$da4",
                                 port=63734, db="db_yy", connect_timeout=10, write_timeout=10)
    with connection.cursor() as cur:
        cur.execute(sql)
        res = cur.fetchall()
        return res


def upfile(sfile, dfile):
    secret_id = 'AKIDc084lCWN1SeaFnp2NSFnWy81fm2EF4pK'
    secret_key = 'NAiAST3RovlMbZIl2yZu87pJ7i3C7wiF'
    region = 'ap-hongkong'
    domain = 'sourcefile-1304080031.cos.accelerate.myqcloud.com'
    client = CosS3Client(CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Domain=domain))
    cos_bucket = 'sourcefile-1304080031'
    client.upload_file(
        Bucket=cos_bucket,
        LocalFilePath=sfile,
        Key=dfile,
        PartSize=1,
        MAXThread=10,
        EnableMD5=False
    )


if __name__ == '__main__':
    videos = getVideos()
    for v in videos:
        checkKey(v)
