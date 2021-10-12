# -*- coding: utf-8 -*-
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from multiprocessing import Pool
import pymysql
import logging
import requests
import re
import os

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)

if not os.path.exists('tmp'):
    os.mkdir('tmp')


def getMysql():
    return pymysql.connect(host="hk-cdb-aumsfh1d.sql.tencentcdb.com", user="root", password="wvqhthpbd!Wv$da4",
                           port=63734, db="db_yy", connect_timeout=10, write_timeout=10)


def getVodList(conn):
    try:
        with conn.cursor() as cur:
            sql = "select vid,video_uri2 from t_video_stock where status>-2 and video_type=2;"
            cur.execute(sql)
            res = cur.fetchall()
        return res
    except Exception as e:
        logging.error(e)
        raise RuntimeError(e)


def getVodData(vid, url):
    try:
        req = requests.get(url).text
        with open(f'tmp/{vid}.m3u8', 'w') as f:
            f.write(req)
        return True
    except Exception as e:
        logging.error(e)
        raise RuntimeError(e)


def getPreviewData(dataFile, start, end):
    try:
        res = ""
        line = 0
        totalTime = 0
        startLine = 0
        console = False
        console2 = False
        console3 = False
        data = open(dataFile, 'r')
        filedata = data.readlines()
        for ts in filedata:
            line += 1
            if console:
                res += ts
            if 'EXTINF' in ts:
                if not console3:
                    startLine = line
                    console3 = True
                longtime = float(re.split(':', ts)[-1].replace(',', ''))
                totalTime += longtime
                if totalTime >= start and not console2:
                    res += ts
                    console = True
                    console2 = True
                if totalTime >= end and console:
                    res += filedata[line]
                    console = False
        titleData = ""
        for title in filedata[:startLine-1]:
            titleData += title
        res = titleData + res
        if filedata[-1] not in res:
            res += filedata[-1]
        data.close()
        os.remove(dataFile)
        return res
    except Exception as e:
        return e


def savePreviewData(vid, data):
    try:
        with open(f'tmp/{vid}-preview.m3u8', 'w') as f:
            f.write(data)
        return True
    except Exception as e:
        logging.error(e)
        raise RuntimeError(e)


def uploadFile(sfile, dfile):
    try:
        secret_id = ''
        secret_key = ''
        region = 'ap-hongkong'
        client = CosS3Client(CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key))
        cos_bucket = 'sourcefile-1304080031'
        client.upload_file(
            Bucket=cos_bucket,
            LocalFilePath=sfile,
            Key=dfile,
            PartSize=1,
            MAXThread=10,
            EnableMD5=False
        )
        os.remove(sfile)
        return True
    except Exception as e:
        logging.error(e)
        raise RuntimeError(e)


def copyFile(spath, dpath):
    pass


def saveBase(conn, vid, previewUri):
    try:
        with conn.cursor() as cur:
            sql = f"update t_video_stock set video_uri3='{previewUri}' where vid={vid};"
            cur.execute(sql)
            conn.commit()
        return True
    except Exception as e:
        logging.error(e)
        raise RuntimeError(e)


def controler(data):
    try:
        palyerUrl = "https://vod.jxnbwjy.com"
        conn = getMysql()
        vid = data[0]
        getVodData(vid, f"{palyerUrl}{data[1]}")
        previewData = getPreviewData(f'tmp/{vid}.m3u8', 1, 15)
        cosPath = '/'.join(re.split('/', data[1])[:-1]) + f'/{vid}-preview.m3u8'
        savePreviewData(vid, previewData)
        uploadFile(f'tmp/{vid}-preview.m3u8', cosPath)
        # saveBase(conn, vid, cosPath)
        logging.info(f"处理完成 {data[0]}")
    except Exception as e:
        logging.info(f"异常 {data[0]} {e}")
        logging.error(e)


if __name__ == '__main__':
    p = Pool(4)
    conn = getMysql()
    vodList = getVodList(conn)
    for vod in vodList:
        p.apply_async(controler, args=(vod,))
    p.close()
    p.join()

