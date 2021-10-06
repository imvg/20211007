# -*- coding: utf-8 -*-
import time
import pymysql
import logging
import re
import os
from telethon import TelegramClient, sync
from telethon.tl.types import InputMessagesFilterVideo
from boto3.session import Session

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
s3_id = "AKIA3NIGOUTKFVLQMCFB"
s3_key = "g2lvpP6H9Fm5D4jovk1OvQd8RVmGjkCJmCTwlk+K"
session = Session(s3_id, s3_key, region_name='ap-east-1')
s3_client = session.client('s3')
s3_bucket = "tgbotvideos"

connection = pymysql.connect(host="101.32.202.66", user="root", password="1q2w3e4r..A", port=3306, db="db_yy_1",
                             connect_timeout=10, write_timeout=10)


def click_next(client, chat):
    client.get_messages(chat)[0].click(1)
    return 0


def save_vod(client, chat, num):
    try:
        res = client.iter_messages(entity=chat, filter=InputMessagesFilterVideo, limit=1)
        nowtime = str(time.time()).replace(".", "")
        mp4path = "tg/%s.mp4" % nowtime
        if not os.path.exists('./tg'): os.mkdir('./tg')
        for s in res:
            logging.info(s)
            longtime = s.media.document.attributes[0].duration
            vodsize = s.media.document.size / 1024 / 1024
            if vodsize <= 50:
                logging.info("(%s) %s 正在下载视频 %s.mp4, 视频时长:%s秒, 视频大小: %s MB" % (
                    num, time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime()), nowtime, round(longtime), vodsize))
                client.download_media(s, file=mp4path)
                if round(longtime) <= 600:
                    vtype = 0
                else:
                    vtype = 1
                result = {"file": mp4path, "vtype": vtype, "duration": round(longtime)}
                return result
            else:
                return 1
    except Exception as e:
        logging.error(f"视频元数据异常 {e}")
        return False


def upload(file, vtype):
    logging.info(f"上传视频 {file}")
    try:
        filename = re.split('/', file)[-1]
        if vtype == 0:
            s3_client.upload_file(Filename=file, Key=f'short/{filename}', Bucket=s3_bucket,
                                  ExtraArgs={'ACL': 'public-read'})
        else:
            s3_client.upload_file(Filename=file, Key=f'long/{filename}', Bucket=s3_bucket,
                                  ExtraArgs={'ACL': 'public-read'})
        os.remove(file)
        return filename
    except Exception as e:
        logging.error(e)
        return False


def saveBase(connection, type, uri, duration):
    try:
        connection.ping()
    except:
        connection = pymysql.connect(host="101.32.202.66", user="root", password="1q2w3e4r..A", port=3306, db="db_yy_1",
                                     connect_timeout=10, write_timeout=10)
        saveBase(connection, type, uri, duration)
    else:
        logging.info(f"视频入库 {uri}")
        sql = f"insert into tg_bot_videos(`v_uri`, `v_type`, `v_duration`, `v_source`) value('{uri}', {type}, {duration}, 'sexytt_bot');"
        try:
            with connection.cursor() as cur:
                cur.execute(sql)
                connection.commit()
            return True
        except:
            logging.info(f"sql提交失败 {sql}")
            return False


if __name__ == '__main__':
    logging.info("初始化Telegram连接")
    key = 1374272
    hash = "59d14bf9afbc980b6906d1e7949d7eed"
    client = TelegramClient(hash, key, hash).start()
    chat = "@sexytt_bot"
    n = 1
    while True:
        logging.info("=" * 100)
        try:
            click_next(client, chat)
            res = save_vod(client, chat, n)
            if res and res != 1:
                up = upload(res['file'], res['vtype'])
                if up:
                    vtype = res['vtype']
                    duration = res['duration']
                    if res['vtype'] == 0:
                        uri = f'/short/{up}'
                    elif res['vtype'] == 1:
                        uri = f'/long/{up}'
                    else:
                        uri = f'/short/{up}'
                    if saveBase(connection, vtype, uri, duration):
                        logging.info(f"处理完成 {up}")
                else:
                    logging.error(f"上传失败 {up}")
            elif res == 1:
                logging.info(f"视频大于50M, 跳过")
            else:
                logging.error(f"处理失败 {res}")
        except Exception as e:
            logging.error(e)
        continue
