#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import pymysql
import time

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)

try:
    conn = pymysql.connect(host="hk-cdb-aumsfh1d.sql.tencentcdb.com", user="root",
                           password="wvqhthpbd!Wv$da4", port=63734, db="db_yy", connect_timeout=10,
                           write_timeout=10)
except Exception as e:
    logging.error(f"Mysql连接失败 {e}")
else:
    try:
        with conn.cursor() as cur:
            report_timestamp = int(time.time()) - 172800
            report_sql = f"delete from t_action_report where ctime<{report_timestamp};"
            cur.execute(report_sql)
            conn.commit()

            history_timestamp = int(time.time()) - 604800
            history_sql = f"delete from t_video_watch where ctime<{history_timestamp};"
            cur.execute(history_sql)
            conn.commit()
    except Exception as e:
        logging.error(f"数据表清除异常 {e}")
    finally:
        conn.close()


if __name__ == '__main__':
    pass