#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import pymysql
import logging

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)


class DataBase:
    def __init__(self):
        self.conn = self._getMysql()
        pass

    def getDomainList(self):
        try:
            try:
                self.conn.ping()
            except:
                self.conn = self._getMysql()
                return self.getDomainList()
            else:
                resList = []
                with self.conn.cursor() as cur:
                    sql = "select id,detail,domain from t_warn_domain_config;"
                    cur.execute(sql)
                    res = cur.fetchall()
                    for data in res:
                        resList.append({'id': data[0], 'tips': data[1], 'domain':data[2]})
                    return resList
        except Exception as e:
            logging.error(f"获取域名列表失败 {e}")

    def _getMysql(self):
        return pymysql.connect(host="hk-cdbrg-6rvyx957.sql.tencentcdb.com", user="root", password="wvqhthpbd!Wv$da4", port=63591, db="db_yy", connect_timeout=10, write_timeout=10)


if __name__ == '__main__':
    ins = DataBase()
    res = ins.getDomainList()
    print(res)
