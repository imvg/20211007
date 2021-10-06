#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import pymysql
import logging

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)


class Split:
    def __init__(self, save, table):
        self.readconn = self._getMysql("read")
        self.writeconn = self._getMysql("write")
        self.save = save
        self.table = table
        self.actionData = (datetime.datetime.now() - datetime.timedelta(days=self.save)).strftime("%Y-%m-%d %H:%M:%S")
        logging.debug(f"任务开始, 处理 {self.actionData} 前的数据...")
        data = self.getData()
        if len(data) > 0:
            if self.writeData(data):
                if self.deleteData():
                    logging.debug(f"处理完成")
        logging.debug(f"任务结束")

    def getData(self):
        try:
            self.readconn.ping()
        except:
            self.readconn = self._getMysql("read")
            self.getData()
        else:
            try:
                logging.debug(f"{self.readconn.get_host_info()} 正在获取 {self.table} 表 {self.save} 天前的数据...")
                with self.readconn.cursor() as cur:
                    sql = f"select * from {self.table} where ctime<='{self.actionData}';"
                    cur.execute(sql)
                    res = cur.fetchall()
                    logging.debug(f"{self.readconn.get_host_info()} {self.table} 获取到 {len(res)} 条数据")
                    return res
            except Exception as e:
                logging.error(e)
                return False

    def writeData(self, data):
        try:
            self.writeconn.ping()
        except:
            self.writeconn = self._getMysql("write")
            self.writeData(data)
        else:
            try:
                logging.debug(f"{self.writeconn.get_host_info()} 正在写入 {self.table} 表 {self.save} 天前的数据...")
                with self.writeconn.cursor() as cur:
                    for dt in data:
                        dt = list(dt)
                        dt[8] = str(dt[8])
                        sql = f"insert into {self.table}(`id`, `domain`, `aid`, `ldy_type`, `band`, `os`, `ip`, `ip_number`, `ctime`, `invite_code`, `referer`, `detail`)" \
                              f"value{tuple(dt)};"
                        cur.execute(sql)
                    self.writeconn.commit()
                    return True
            except Exception as e:
                logging.error(e)
                return False

    def deleteData(self):
        try:
            self.readconn.ping()
        except:
            self.readconn = self._getMysql("read")
            self.getData()
        else:
            try:
                with self.readconn.cursor() as cur:
                    logging.debug(f"{self.readconn.get_host_info()} 正砸删除 {self.table} 表 {self.actionData} 前的数据...")
                    sql = f"delete from {self.table} where ctime<='{self.actionData}';"
                    cur.execute(sql)
                    self.readconn.commit()
                    return True
            except Exception as e:
                logging.error(e)
                return False

    def _getMysql(self,db):
        if db == 'read':
            return pymysql.connect(host="172.19.0.12", user="root", password="wvqhthpbd!Wv$da4",
                                  port=3306, db="db_yy", connect_timeout=10, write_timeout=10)
        elif db == 'write':
            return pymysql.connect(host="127.0.0.1", user="root", password="1q2w3e4r..A",
                                  port=3306, db="db_yy", connect_timeout=10, write_timeout=10)

    def __del__(self):
        self.readconn.close()
        self.writeconn.close()


if __name__ == '__main__':
    Split(save=7, table="t_domain_statistical_ip_open")
