import logging
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.loop import MessageLoop
import pymysql
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

connection = pymysql.connect(host="101.32.202.66", user="root", password="1q2w3e4r..A", port=3306, db="db_yy_1",
                                     connect_timeout=10, write_timeout=10)

vtype = 1

try:
    with connection.cursor() as cur:
        if vtype == 0:
            cur.execute('select vid from tg_bot_videos where v_type=0;')
        else:
            cur.execute('select vid from tg_bot_videos where v_type=1;')
        total = cur.fetchall()
        vlist = []
        for v in total:
            vlist.append(v[0])
        logging.info(vlist)
        vid = random.randint(0, len(total) - 1)
        logging.info(vid)
        logging.info(f'select v_uri from tg_bot_videos where vid={vlist[vid]}')
        cur.execute(f'select v_uri from tg_bot_videos where vid={vlist[vid]}')
        vuri = cur.fetchone()[0]
        cosUrl = "https://tgbotvideos.s3.ap-east-1.amazonaws.com"
        res = cosUrl + vuri
        logging.info(res)
except Exception as e:
    logging.error(f"查询视频失败 {e}")
    logging.info("https://tgbotvideos.s3.ap-east-1.amazonaws.com/short/16283416911821556.mp4")