# -*- coding: utf-8 -*-
import os
import logging
import re
import pymysql
import requests
from multiprocessing import Pool
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.WARN)


def controller(vid, url, uri, oldKey, newKey, client, cos_bucket, tab):
    try:
        if not os.path.exists('tmp'):
            os.mkdir('tmp')
        change = m3u8Action(url, uri, oldKey, newKey)
        if change:
            dpath = '/'.join(re.split('/', uri)[:-1]) + '/' + change
            upload('tmp/'+change, dpath, client, cos_bucket)
            res = setdb(video_uri1=uri, video_uri2=dpath, vid=vid, tab=tab)
            if res:
                logging.warning(f"{tab} 表 VID {vid} 修改完成")
                return True
            else:
                logging.error(f"{tab} 表 VID {vid} 数据库更新失败 {res}")
                return False
    except Exception as e:
        logging.error(f"Controller {tab} 表 VID {vid} 处理失败 {e}")


def getList():
    try:
        connection = pymysql.connect(host="hk-cdb-aumsfh1d.sql.tencentcdb.com", user="root", password="wvqhthpbd!Wv$da4", port=63734, db="db_yy", connect_timeout=10, write_timeout=10)
    except Exception as e:
        logging.error(f"数据库链接失败 {e}")
    else:
        datalst = {}
        try:
            with connection.cursor() as cur:
                videoList = []
                sql = "select vid,video_uri2 from t_video where video_uri2 not like '%-2.m3u8' and video_uri2 like '%.m3u8' and status>-3 and source=1;"
                cur.execute(sql)
                video_res = cur.fetchall()
                for s in video_res:
                    videoList.append({'vid': s[0], 'uri': s[1]})
                datalst['video'] = videoList
                stockList = []
                sql = "select vid,video_uri2 from t_video_stock where video_uri2 not like '%-2.m3u8' and video_uri2 like '%.m3u8' and status>-3 and source=1;"
                cur.execute(sql)
                stock_res = cur.fetchall()
                for d in stock_res:
                    stockList.append({'vid': d[0], 'uri': d[1]})
                datalst['stock'] = stockList
                return datalst
        except Exception as e:
            logging.error(e)
            return False
        finally:
            connection.close()


def m3u8Action(url, uri, oldKey, newKey):
    try:
        filename = re.split('\.', re.split('/', uri)[-1])[0] + '-2.m3u8'
        data = requests.get(url + uri).content.decode()
        des = data.replace(oldKey, newKey)
        with open(f'tmp/{filename}', 'w') as f:
            f.write(des)
        return filename
    except Exception as e:
        logging.error(e)
        return False


def upload(sfile, dfile, client, cos_bucket):
    try:
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
        return False


def setdb(video_uri1, video_uri2, vid, tab):
    try:
        connection = pymysql.connect(host="hk-cdb-aumsfh1d.sql.tencentcdb.com", user="root", password="wvqhthpbd!Wv$da4", port=63734, db="db_yy", connect_timeout=10, write_timeout=10)
    except Exception as e:
        logging.error(f"{vid} 数据库链接失败 {e}")
    else:
        try:
            with connection.cursor() as cur:
                if tab == "video":
                    UpdateSql = f"update t_video set video_uri1='{video_uri1}', video_uri2='{video_uri2}' where vid={vid};"
                elif tab == "stock":
                    UpdateSql = f"update t_video_stock set video_uri1='{video_uri1}', video_uri2='{video_uri2}' where vid={vid};"
                cur.execute(UpdateSql)
                connection.commit()
                return True
        except Exception as e:
            logging.error(f"更新数据库失败 {e}")
            return False
        finally:
            connection.close()


if __name__ == '__main__':
    logging.warning("初始化...")
    secret_id = 'AKIDc084lCWN1SeaFnp2NSFnWy81fm2EF4pK'
    secret_key = 'NAiAST3RovlMbZIl2yZu87pJ7i3C7wiF'
    region = 'ap-hongkong'
    domain = 'sourcefile-1304080031.cos.accelerate.myqcloud.com'
    client = CosS3Client(CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Domain=domain))
    cos_bucket = 'sourcefile-1304080031'
    cosurl = "https://sourcefile-1304080031.cos.accelerate.myqcloud.com"
    oldKey = "https://xktnapox.mlxjz.com/vkey/enc.key"
    newKey = "/vkey/enc.key"
    m3u8List = getList()
    p = Pool(4)
    for data in m3u8List['stock']:
        p.apply_async(controller, args=(data['vid'], cosurl, data['uri'], oldKey, newKey, client, cos_bucket, "stock"))

    for data in m3u8List['video']:
        p.apply_async(controller, args=(data['vid'], cosurl, data['uri'], oldKey, newKey, client, cos_bucket, "video"))
    p.close()
    p.join()
