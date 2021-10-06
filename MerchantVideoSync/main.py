#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pymysql
import logging
import requests

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)


def getMysql(name):
    connDict = {
        'master': pymysql.connect(host="172.19.0.12", user="root", password="wvqhthpbd!Wv$da4", port=3306, db="db_yy", connect_timeout=10, write_timeout=10),
        '91lu': pymysql.connect(host="172.19.0.7", user="root", password="C7x9i0RhmqRPCk6swXQH", port=3306, db="db_yy", connect_timeout=10, write_timeout=10)
    }
    return connDict[name]


def getBaseData(conn, table: str):
    logging.debug(f"{conn.host} 查询 {table} 表数据...")
    with conn.cursor() as cur:
        sql = f"select * from {table}"
        cur.execute(sql)
        return cur.fetchall()


def saveData(conn, table, data):
    try:
        for d in data:
            if len(d) == 32 and table == "t_video":
                sql = f"insert into t_video(`vid`,`sku`,`title`,`cover_uri`,`video_uri1`,`video_uri2`,`video_uri3`,"\
                      f"`district`,`pv`,`uv`,`vnum`,`top`,`vip`,`favorites`,`likes`,`shares`,`status`,`creator`,"\
                      f"`video_type`,`video_code`,`sort`,`description`,`ctime`,`uptime`,`duration`,`resolution`,"\
                      f"`source`,`buy_times`,`provider_id`,`provider_ratio`,`buy_amount`,`stime`) "\
                      f"value({d[0]},{d[1]},'{d[2]}','{d[3]}','{d[4]}','{d[5]}','{d[6]}','{d[7]}',{d[8]},{d[9]},"\
                      f"'{d[10]}',{d[11]},{d[12]},{d[13]},{d[14]},{d[15]},{d[16]},'{d[17]}',{d[18]},{d[19]},{d[20]},"\
                      f'"{d[21]}"'\
                      f",{d[22]},{d[23]},{d[24]},'{d[25]}',{d[26]},{d[27]},{d[28]},{d[29]},{d[30]},{d[31]})"
                logging.info(sql)
            elif len(d) == 22 and table == "t_video_stock":
                if d[6] == '-2' or d[6] == -2:
                    d[6] = 1
                sql = f"insert into t_video_stock(`vid`,`title`,`cover_uri`,`video_uri`,`district`,"\
                      f"`vnum`,`status`,`video_type`,`video_code`,`description`,`ctime`,`resolution`,"\
                      f"`duration`,`md5`,`name`,`ch_name`,`video_test_uri`,`source`,`tag`,`video_uri1`,"\
                      f"`video_uri2`,`video_uri3`) "\
                      f"value({d[0]},'{d[1]}','{d[2]}','{d[3]}','{d[4]}','{d[5]}',{d[6]},{d[7]},{d[8]},"\
                      f'"{d[9]}",'\
                      f"'{d[10]}','{d[11]}','{d[12]}','{d[13]}','{d[14]}','{d[15]}','{d[16]}',"\
                      f"{d[17]},'{d[18]}','{d[19]}','{d[20]}','{d[21]}')"
            else:
                logging.error(f"数据字段数量不对 {len(d)} {d}")
                return False
            try:
                logging.debug(f"执行SQL: {sql}")
                with conn.cursor() as cur:
                    cur.execute(sql)
                    conn.commit()
            except Exception as e:
                logging.error(f"saveData方法异常 {e} {sql}")
                return False
    except Exception as e:
        logging.error(e)
        return False
    else:
        return True


def controler(tableList: list):
    # 获取两个库的实例
    masterConn = getMysql('master')
    mch2Conn = getMysql('91lu')
    try:
        for table in tableList:
            # 获取两个库的视频表数据
            masterVideoData = getBaseData(masterConn, table)
            mch2VideoData = getBaseData(mch2Conn, table)

            # 获取两个库的表视频数据ID
            masterVideoId = [x[0] for x in masterVideoData]
            mch2VideoId = [s[0] for s in mch2VideoData]

            # 计算两个表的差异数据
            differenceVideoId = [i for i in masterVideoId if i not in mch2VideoId]
            differenceVideoData = [d for d in masterVideoData if d[0] in differenceVideoId]

            if len(differenceVideoData) >= 1:
                logging.info(f"{table} 91撸缺少 {len(differenceVideoData)} 条视频数据")
                if saveData(mch2Conn, table, differenceVideoData):
                    logging.info(f"{table} 同步完成")
                    sendMessage(f"{table} 表同步完成 {len(differenceVideoData)} 条差异数据")
                else:
                    logging.error(f"{table} 数据同步写入失败")
                    sendMessage(f"{table} 数据同步写入失败")
                    return False
            else:
                logging.info(f"{table} 数据完整, 无需同步")
                sendMessage(f"{table} 数据完整, 无需同步")
    except Exception as e:
        logging.error(f"数据同步异常 {e}")
        sendMessage(f"数据同步异常 {e}")
        return False
    finally:
        masterConn.close()
        mch2Conn.close()
        logging.info(f"任务结束")
        return True


def sendMessage(Message):
    logging.debug(f"发送通知...")
    BotToken = "1590534238:AAFYL23LSVWZdZi4H_Q_Fy7v1ivggD7UBs8"
    ChannelId = "-1001175029636"
    try:
        data = {'chat_id': str(ChannelId).replace('\'', ''), 'text': '<视频数据表同步> '+Message}
        requests.post(url=f'https://api.telegram.org/bot{BotToken}/sendMessage', data=data)
        return True
    except Exception as e:
        logging.error(f"通知消息发送失败 {e}")


if __name__ == '__main__':
    syncList = ['t_video', 't_video_stock']
    controler(syncList)
