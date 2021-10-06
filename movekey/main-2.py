# -*- coding: utf-8 -*-
import logging
import pymysql
import requests
from requests.adapters import HTTPAdapter

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
session = requests.session()
session.mount('https://', HTTPAdapter(max_retries=3))
vurl = "https://vod.qhdjpsm.com"


def process(data):
    n = 0
    for d in data:
        if str(d[0]).endswith('.m3u8'):
            data = session.get(f"{vurl}{d[0]}").text
            if "xktnapox.mlxjz.com" in data:
                logging.info(f"{vurl}{d[0]}")
                n += 1
    logging.info(f"找到 {n} 个视频")


def getM3u8List():
    try:
        conn = pymysql.connect(host="hk-cdb-aumsfh1d.sql.tencentcdb.com", user="root", password="wvqhthpbd!Wv$da4", port=63734, db="db_yy", connect_timeout=10, write_timeout=10)
        with conn.cursor() as cur:
            sql = "select video_uri2 from t_video_stock where video_uri2 like '%.m3u8' and status>-3 and source=1;"
            cur.execute(sql)
            res = cur.fetchall()
            return res
    except Exception as e:
        logging.error(e)


if __name__ == '__main__':
    data = getM3u8List()
    process(data)
