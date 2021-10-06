#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from autoMain import AutoMain
import json
import logging
import re


logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


class Methods:
    def __init__(self):
        pass

    def makeAction(self,data):
        try:
            try:
                data = json.loads(data)['parms']
            except Exception as e:
                logging.error(f"数据格式化异常 {e}")
                return {"code": 1, "msg": "数据格式化异常", "data": {}}
            else:
                domainList = []
                rootDomain = re.split(',', data['domain'])
                for domain in rootDomain:
                    domainList.append(domain)
                    domainList.append("*." + domain)
                accountList = {
                    'xyaccount': {"access_key": "",
                                  "secret_key": ""},
                    'miliaccount': {"access_key": "",
                                    "secret_key": ""},
                    'beiyong889900': {"access_key": "",
                                      "secret_key": ""},
                    'qzh7537': {"access_key": "",
                                "secret_key": ""},
                    'luzhuanyong001': {"access_key": "",
                                "secret_key": ""}
                }
                sourceDict = {
                    'lubei': ['source1.dpagesource.com', 'source2.dpagesource.com'],
                    'huaban': ['source3.dpagesource.com', 'source4.dpagesource.com'],
                    '91lu': ['source5.dpagesource.com', 'source6.dpagesource.com'],
                }
                source1 = sourceDict[data['merchant']][0]
                source2 = sourceDict[data['merchant']][1]
                tips = data['domainTips']
                optimization = data['optimization']
                access_key = accountList[data['account']]['access_key']
                secret_key = accountList[data['account']]['secret_key']
                ins = AutoMain(access_key, secret_key)
                if ins.autoAdd(domainList=domainList, source1=source1, source2=source2, tips=tips, merchant=data['merchant']):
                    return {"code": 0, "msg": "配置成功", "data": {}}
                else:
                    return {"code": 1, "msg": "配置失败", "data": {}}
        except Exception as e:
            logging.error(f"makeAction 方法异常 {e}")
            return {"code": 1, "msg": "提交的数据异常, 配置失败", "data": {}}

    def getSSL(self, data):
        try:
            try:
                data = json.loads(data)['parms']
            except Exception as e:
                logging.error(f"数据格式化异常 {e}")
                return {"code": 1, "msg": "数据格式化异常", "data": {}}
            else:
                ins = AutoMain('1', '2')
                certs = []
                if ',' in data['domainList']:
                    domainList = re.split(',', data['domainList'])
                else:
                    domainList = [data['domainList']]
                domains = []
                for res in domainList:
                    domains.append(res)
                    domains.append(f"*.{res}")
                ssl = ins.getSSL(domains)
                for domain in domains:
                    if "*" not in domain:
                        expire = ins.getCertExpire(f'certificate/{domain}.crt')
                        certs.append(
                            {'domain': domain, 'expire': expire, 'crt': ssl[domain]['csr'], 'key': ssl[domain]['key']})
                return {"code": 0, "msg": "获取成功", "data": certs}
        except Exception as e:
            logging.error(f"getSSL 方法异常 {e}")
            return {"code": 1, "msg": "获取失败", "data": {}}

    def makeDump(self, data):
        try:
            try:
                data = json.loads(data)['parms']
            except Exception as e:
                logging.error(f"数据格式化异常 {e}")
                return {"code": 1, "msg": "数据格式化异常", "data": {}}
            else:
                ins = AutoMain('', '')
                domainSSL = []
                for domain in data["domainList"]:
                    domainFull = re.split('/', domain['domain'])[2]
                    domainSSL.append(domainFull)
                ssl = ins.getSSL(domainSSL)
                for domain in data["domainList"]:
                    domainFull = re.split('/', domain['domain'])[2]
                    if not ins.setDump(ssl[domainFull], domainFull, data["dumpTo"], domain['merchant']):
                        return {"code": 1, "msg": "配置失败", "data": ""}
                return {"code": 0, "msg": "配置成功", "data": ""}
        except Exception as e:
            logging.error(f"跳转方法全局异常 {e}")
            return {"code": 1, "msg": "程序处理异常", "data": ""}

    def getDomainList(self):
        try:
            ins = AutoMain('', '')
            res = ins.getDomainList()
            return {"code": 0, "msg": "获取成功", "data": res}
        except Exception as e:
            logging.error(f"getDomainList 方法异常 {e}")
            return {"code": 1, "msg": "未知异常", "data": {}}
