#!/bin/python3
# -*- coding: utf-8 -*-
import argparse
import json
import logging
import re
import time
import socket
from datetime import datetime
from configparser import ConfigParser
from multiprocessing import Pool

import OpenSSL
import pymysql
import requests
import ssl
from requests import session
from requests.adapters import HTTPAdapter

try:
    session = session()
    session.mount('http://', HTTPAdapter(max_retries=3))
    session.mount('https://', HTTPAdapter(max_retries=3))
    config = ConfigParser()
    configSetting = argparse.ArgumentParser()
    configSetting.add_argument('-c', dest='configfile', type=str)
    configFile = configSetting.parse_args().configfile
    config.read(configFile)
    LogLevel = config.get("global", "LogLevel")
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
    CertExpirationInterval = int(config.get("global", "CertExpirationInterval"))
    DomainExpirationInterval = int(config.get("global", "DomainExpirationInterval"))
    warningUrl = config.get("global", "WarningUrl")
    TelegramToken = config.get("Telegram", "BotToken")
    TelegramChannelId = config.get("Telegram", "ChannelId")
    sendTelegramMessage = config.get("Telegram", "SendMessage")
    ProcessQuantity = int(config.get("global", "ProcessQuantity"))
    dpageServers = re.split(',', config.get("global", "dpageServers"))
except Exception as e:
    logging.fatal(f"???????????????????????? {e}")


def checkDomain(config):
    try:
        try:
            res = session.get(url=config['domain'], timeout=20)
        except requests.ConnectionError as err:
            logging.warning(f"?????????????????? {config['domain']} {err}")
            return {"id": config['id'], "status": 0, "message": f"?????????????????? {config['domain']}"}
        except requests.exceptions.Timeout as timeout:
            logging.warning(f"?????????????????? {config['domain']} {timeout}")
            return {"id": config['id'], "status": 0, "message": f"?????????????????? {config['domain']}"}
        else:
            status = config['status']
            if 'x' in config['status']:
                status = re.split('x', config['status'])[0]
            if str(res.status_code).startswith(status):
                if config['code'] in res.text:
                    if config['domain'].startswith('https'):
                        if not checkSSL(re.split('/', config['domain'])[2]):
                            return {"id": config['id'], "status": 0, "message": f"???????????????????????? {config['domain']}"}
                        else:
                            if not checkDnsLastTime(config):
                                return {"id": config['id'], "status": 0, "message": f"?????????????????????????????? {config['domain']}"}
                            else:
                                domain = re.split('/', config['domain'])[2]
                                if checkIP(domain):
                                    logging.debug(f"?????????????????? {config['domain']}")
                                    return {"id": config['id'], "status": 1, "message": f"?????????????????? {config['domain']}"}
                                else:
                                    logging.warning(f"??????CDN??????, IP?????????????????????????????????")
                                    return {"id": config['id'], "status": 0, "message": f"CDN??????,????????????IP????????????????????? {config['domain']}"}
                    else:
                        if not checkDnsLastTime(config):
                            return {"id": config['id'], "status": 0, "message": f"?????????????????????????????? {config['domain']}"}
                        else:
                            return {"id": config['id'], "status": 1, "message": f"?????????????????? {config['domain']}"}
                else:
                    return {"id": config['id'], "status": 0, "message": f"???????????????????????? {config['domain']}"}
            else:
               return {"id": config['id'], "status": 0, "message": f"???????????????????????? {config['domain']}"}
    except Exception as e:
        logging.error(f"checkDomain Error {config} {e}")
        return {"id": config['id'], "status": 0, "message": f"?????????????????? {config['domain']}"}


def checkDnsLastTime(data):
    try:
        domain = re.split('/', data['domain'])[2]
        if int(time.mktime(time.strptime(data['lastday'], "%Y-%m-%d %H:%M:%S"))) - int(time.time()) <= int(DomainExpirationInterval)*86400:
            logging.warning(f"???????????????????????? {domain} ??????????????????????????? {data['lastday']} ???????????????")
            return False
        else:
            logging.debug(f"???????????????????????? {domain} ??????????????????????????? {data['lastday']}")
            return True
    except Exception as e:
        logging.error(f"checkDnsLastTime???????????? {data} {e}")
        return False


def checkSSL(domain, port=443):
    try:
        cert = ssl.get_server_certificate((domain, port))
        certification = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
        valid_start_time = certification.get_notBefore()  # ?????????????????????
        valid_end_time = certification.get_notAfter()  # ?????????????????????
        expireDate = datetime.strptime(valid_end_time.decode()[0:-1], '%Y%m%d%H%M%S')  # ??????????????????
        expire = time.strptime(valid_end_time.decode()[0:-1], '%Y%m%d%H%M%S')
        expireTimeStemp = int(time.mktime(expire))
        logging.info((domain, f"{expireDate}", expireTimeStemp, int(CertExpirationInterval)*86400 + int(time.time())))
        if expireTimeStemp <= (int(CertExpirationInterval)*86400 + int(time.time())):
            logging.warning(f"???????????????????????? {domain} ???????????????????????? {expireDate} ???????????????")
            return False
        else:
            logging.debug(f"???????????????????????? {domain} ???????????????????????? {expireDate}")
            return True
    except Exception as e:
        logging.error(f"checkSSL???????????? {domain} {e}")
        return False


def checkIP(domain):
    try:
        domainAddr = socket.getaddrinfo(domain, 'https')[0][4][0]
        if domainAddr in dpageServers:
            return False
        else:
            logging.debug(f"?????????????????????, ??????IP??????????????????????????? {domain} -> {domainAddr}")
            return True
    except Exception as e:
        logging.error(f"??????IP???????????? {e}")
        return False


def sendMessage(message):
    try:
        data = {'BotToken': str(TelegramToken).replace("\'", ""), 'ChannelId': str(TelegramChannelId).replace('\'', ''),'Message': message}
        res = session.post(url='http://telegram.cs0147.com/send', data=data, timeout=30)
        if res.text != 'Success':
            logging.error(f'??????????????????, ???????????????: {res.text}')
    except Exception as err:
        logging.error(f'?????????????????? {err}')
    logging.warning(message)


def getDomainList(config):
    try:
        conn = pymysql.connect(host=config['host'], port=int(config['port']), user=config['user'], password=config['password'], db=config['db'], connect_timeout=10)
        domainList = []
        with conn.cursor() as cur:
            sql = f"select id,detail,domain,response_status,response_code,etime from {config['table']} where status=1;"
            cur.execute(sql)
            res = cur.fetchall()
            for data in res:
                domainList.append({'id': data[0], 'domain': data[2], 'status': str(data[3]), 'code': data[4], 'detail': data[1], 'lastday': str(data[5])})
        conn.close()
        return domainList
    except Exception as e:
        logging.error(f"????????????????????? {e}")


def uploadStatus(res):
    try:
        if sendTelegramMessage == "yes":
            for data in res:
                if data['status'] == 0:
                    sendMessage(data['message'])
        updata = []
        for data in res:
            updata.append({"id": data['id'], "status": data['status'], "info": data['message']})
        if len(updata) > 0:
            try:
                postdata = {"detail": updata}
                req = session.post(warningUrl, data=json.dumps(postdata))
                logging.debug(f"API Return: {req.text}")
                if json.loads(req.text)['code'] == 0:
                    return True
                else:
                    return False
            except Exception as e:
                logging.error(f"?????????????????????????????? {e}")
                return False
        pass
    except Exception as e:
        logging.error(f"?????????????????? {e}")
        sendMessage(f"?????????????????? {e}")


if __name__ == '__main__':
    try:
        p = Pool(ProcessQuantity)
        dburl = config.get("Database", "Connect").replace('\n', '')
        dbport = config.get("Database", "Port").replace('\n', '')
        dbname = config.get("Database", "Dbname").replace('\n', '')
        dbtable = config.get("Database", "Table").replace('\n', '')
        dbuser = config.get("Database", "User").replace('\n', '')
        dbpassword = config.get("Database", "Password").replace('\n', '')
        domainList = getDomainList({'host': dburl, 'port': dbport, 'user': dbuser, 'password': dbpassword, 'db': dbname, 'table': dbtable})
        res = []
        for domain in domainList:
            run = p.apply_async(checkDomain, args=(domain,))
            res.append(run.get())
        p.close()
        p.join()
        #logging.debug(f"??????????????????: {res}")
        if uploadStatus(res):
            logging.debug(f"????????????")
        else:
            logging.warning(f"??????????????????")
    except Exception as e:
        logging.fatal(f"???????????? {e}")
        sendMessage(f"???????????? {e}")
