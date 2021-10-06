# -*- coding: utf-8 -*-
from configparser import ConfigParser
import argparse
import logging
import pymysql
import requests
import time
import redis


class monitor:
    def __init__(self):
        self.config = ConfigParser()
        configSetting = argparse.ArgumentParser()
        configSetting.add_argument('-c', dest='configfile', type=str)
        configFile = configSetting.parse_args().configfile
        self.config.read(configFile)
        self.checkConfig()
        LogLevel = self.config.get("Global", "LogLevel").replace('\n', '')
        if LogLevel == 'debug':
            logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)
        elif LogLevel == 'info':
            logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
        elif LogLevel == 'warn':
            logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.WARN)
        elif LogLevel == 'error':
            logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.ERROR)
        elif LogLevel == 'fatal':
            logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.FATAL)
        else:
            logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)

        logging.debug("初始化...")
        self.msqHost = self.config.get("Mysql", "Server").replace('\n', '')
        self.msqUser = self.config.get("Mysql", "User").replace('\n', '')
        self.msqPassword = self.config.get("Mysql", "Password").replace('\n', '')
        self.msqPort = self.config.get("Mysql", "Port").replace('\n', '')
        self.msqDb = self.config.get("Mysql", "DB").replace('\n', '')
        self.connection = pymysql.connect(host=self.msqHost, user=self.msqUser,password=self.msqPassword, port=int(self.msqPort), db=self.msqDb, connect_timeout=10, write_timeout=10)
        rdsHost = self.config.get("Redis", "Server").replace('\n', '')
        rdsPassword = self.config.get("Redis", "Password").replace('\n', '')
        rdsPort = self.config.get("Redis", "Port").replace('\n', '')
        rdsDb = self.config.get("Redis", "DB").replace('\n', '')
        self.rds = redis.Redis(host=rdsHost, port=rdsPort, decode_responses=True, password=rdsPassword, db=rdsDb)

        self.scale = self.config.get("Global", "Scale").replace('\n', '')
        self.ignore = self.config.get("Global", "Ignore").replace('\n', '')
        self.aidList = ()
        self.newUserCountList = []

    def checkConfig(self):
        try:
            configList = [
                self.config.get("Telegram", "BotToken").replace('\n', ''),
                self.config.get("Telegram", "ChannelId").replace('\n', ''),
                self.config.get("Global", "LogLevel").replace('\n', ''),
                self.config.get("Global", "Scale").replace('\n', ''),
                self.config.get("Global", "Ignore").replace('\n', ''),
                self.config.get("Global", "Granularity").replace('\n', ''),
                self.config.get("Global", "EnableAgent").replace('\n', ''),
                self.config.get("Redis", "Server").replace('\n', ''),
                self.config.get("Redis", "Password").replace('\n', ''),
                self.config.get("Redis", "Port").replace('\n', ''),
                self.config.get("Redis", "DB").replace('\n', ''),
                self.config.get("Mysql", "Server").replace('\n', ''),
                self.config.get("Mysql", "User").replace('\n', ''),
                self.config.get("Mysql", "Password").replace('\n', ''),
                self.config.get("Mysql", "port").replace('\n', ''),
                self.config.get("Mysql", "DB").replace('\n', '')
            ]
            for c in configList:
                if not c:
                    logging.error(f"配置文件异常")
                    exit()
        except Exception as e:
            logging.error(f"配置文件异常 {e}")
            exit()

    def getAgentId(self):
        try:
            agentList = eval(self.config.get("Global", "EnableAgent").replace('\n', ''))
            if len(agentList) == 0:
                sql = f"select aid,username,inviteCode from t_agent where status=1;"
            else:
                sql = f"select aid,username,inviteCode from t_agent where status=1 and username in ({str(agentList).strip('[]')});"
            self.aidList = self.commitSql(sql)
            logging.debug(f"代理信息获取成功")
            return True
        except Exception as e:
            logging.error(f"查询代理ID失败 {e}")
            return False

    def countUsers(self):
        try:
            lidu = eval(self.config.get("Global", "Granularity").replace('\n', ''))
            if lidu['unit'] == 'H':
                spd = 3600 * int(lidu['value'])
            elif lidu['unit'] == 'M':
                spd = 60 * int(lidu['value'])
            else:
                spd = 60 * int(lidu['value'])
            now = int(time.time())
            dtime = now - now % spd
            stime = (now - now % spd) - spd
            for s in self.aidList:
                sql = f"select count(uid) from t_user where aid={s[0]} and regtime>={stime} and regtime<={dtime};"
                retdata = {"UserName": s[1], "inviteCode": s[2], "NewUserCount": self.commitSql(sql)[0][0]}
                self.newUserCountList.insert(-1, retdata)
                logging.debug(retdata)
            logging.debug(f"代理新增用户统计完成")
        except Exception as e:
            logging.error(f"统计用户数失败 {e}")
            return False

    def commitSql(self, sql):
        try:
            self.connection.ping()
        except:
            self.connection = pymysql.connect(host=self.msqHost, user=self.msqUser,password=self.msqPassword, port=int(self.msqPort), db=self.msqDb, connect_timeout=10, write_timeout=10)
            self.commitSql(sql)
        else:
            try:
                with self.connection.cursor() as cur:
                    cur.execute(sql)
                ret = cur.fetchall()
                logging.debug(f"SQL执行成功 {sql} Return {ret}")
                return ret
            except Exception as e:
                logging.error(f"执行Sql失败 {e} {sql}")
                return False

    def sendMessage(self, message):
        chat = self.config.get("Telegram", "ChannelId").replace('\n', '')
        token = self.config.get("Telegram", "BotToken").replace('\n', '')
        data = {'chat_id': str(chat).replace('\'', ''), 'text': message}
        token = str(token).replace("\'", "")
        try:
            res = requests.post(url=f'https://api.telegram.org/bot{token}/sendMessage', data=data)
            if res.status_code != 200:
                logging.error(f'消息发送失败, 接口返回值: {res}')
        except Exception as err:
            logging.error(f'消息发送失败 {err}')


if __name__ == '__main__':
    try:
        ins = monitor()
        ins.getAgentId()
        ins.countUsers()
        NewData = ins.newUserCountList
        OldData = ins.rds.get("UserCountList")
        try:
            if not OldData:
                logging.debug("未找到旧数据")
            else:
                for nowData in NewData:
                    if nowData['UserName'] not in OldData:
                        logging.debug(f"代理 {nowData['UserName']} 上次数据未记录")
                    else:
                        for lastData in eval(OldData):
                            if nowData['UserName'] == lastData['UserName']:
                                agent = nowData['UserName']
                                invite = nowData['inviteCode']
                                last = int(lastData['NewUserCount'])
                                now = int(nowData['NewUserCount'])
                                logging.debug(f"代理 {agent}({invite}) 本时段新增:{now} 上时段新增:{last}")
                                if last > now >= int(ins.ignore):
                                    spt = (last - now) / last * 100
                                    if spt >= int(ins.scale):
                                        msg = f"用户新增提示 \n代理{agent}({invite}) \n本时段新增用户:{now} \n上时段新增用户:{last} \n相比减少 {'%.2f'%spt}%"
                                        logging.warning(msg)
                                        ins.sendMessage(msg)
        except Exception as e:
            logging.error(f"统计逻辑异常 {e}")
        finally:
            ins.rds.set('UserCountList', str(NewData))
    except Exception as e:
        logging.error(f"全局异常 {e}")
    finally:
        logging.debug(f"任务结束")

