#!/bin/python3
# -*- coding: utf-8 -*-
import json
import argparse
import logging
import requests
from multiprocessing import Pool
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.billing.v20180709 import billing_client, models
from aliyunsdkcore.client import AcsClient
from aliyunsdkbssopenapi.request.v20171214.QueryAccountBalanceRequest import QueryAccountBalanceRequest
from configparser import ConfigParser
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


def CheckTencent(secretId, secretKey, account, limit, ChannelId, BotToken):
    try:
        cred = credential.Credential(secretId, secretKey)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "billing.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = billing_client.BillingClient(cred, "", clientProfile)
        req = models.DescribeAccountBalanceRequest()
        params = {}
        req.from_json_string(json.dumps(params))
        resp = eval(str(client.DescribeAccountBalance(req)).replace('false', '"false"'))
        Balance = resp["Balance"]
        if '-' in str(Balance):
            Balance = '-' + str(int(str(Balance).replace('-', '')) / 100)
        else:
            Balance = Balance / 100
        if float(Balance) <= limit:
            sendMessage(ChannelId, BotToken, f'<腾讯云> 账户余额不足, {account} 仅剩 {Balance} 元')
            logging.warning(f'<腾讯云> 账户余额不足, {account} 仅剩 {Balance} 元')
        else:
            logging.info(f'<腾讯云> 账户余额充足, {account} 剩余 {Balance} 元')
    except Exception as err:
        logging.error(f"CheckTencent {err}")


def CheckAliyun(secretId, secretKey, zone, account, limit, ChannelId, BotToken):
    try:
        client = AcsClient(secretId, secretKey, zone, timeout=60)
        request = QueryAccountBalanceRequest()
        request.set_accept_format('json')
        response = client.do_action_with_exception(request)
        Balance = eval(str(response, encoding='utf-8').replace('true', '"true"'))['Data']['AvailableAmount']
        if ',' in Balance:
            Balance = str(Balance).replace(',', '')
        if float(Balance) <= limit:
            sendMessage(ChannelId,BotToken,f'<阿里云> 账户余额不足, {account} 仅剩 {Balance} 元')
            logging.warning(f'<阿里云> 账户余额不足, {account} 仅剩 {Balance} 元')
        else:
            logging.info(f'<阿里云> 账户余额充足, {account} 剩余 {Balance} 元')
    except Exception as err:
        logging.error(f"CheckAliyun {err}")


def sendMessage(chat, token, msg):
    data = {'chat_id': str(chat).replace('\'', ''), 'text': msg}
    token = str(token).replace("\'","")
    try:
        res = requests.post(url=f'https://api.telegram.org/bot{token}/sendMessage', data=data)
        if res.status_code != 200:
            logging.error(f'消息发送失败, 接口返回值: {res}')
    except Exception as err:
        logging.error(f'消息发送失败 {err}')


def CheckParser(myconfig):
    if not myconfig.has_section("Telegram"):
        logging.error('没有设置 Telegram 区域')
    elif not myconfig.has_option("Telegram", "BotToken") or len(myconfig.get("Telegram", "BotToken")) <= 2:
        logging.error('没有设置 BotToken 参数')
    elif not myconfig.has_option("Telegram", "ChannelId") or len(myconfig.get("Telegram", "ChannelId")) <= 2:
        logging.error('没有设置 ChannelId 参数')
    elif not myconfig.has_section("Aliyun") or not myconfig.has_section("Tencent"):
        logging.error('没有设置 云账号 区域')
    elif not myconfig.has_option("Aliyun", "AccountList") or not myconfig.get("Tencent", "AccountList"):
        logging.error('没有设置 AccountList 参数')
    elif len(myconfig.get("Aliyun", "AccountList")) <= 2 or len(myconfig.get("Tencent", "AccountList")) <= 2:
        logging.error('AccountList 参数为空')
    else:
        return True
    return False


if __name__ == '__main__':
    p = Pool(2)
    try:
        config = ConfigParser()
        configSetting = argparse.ArgumentParser()
        configSetting.add_argument('-c', dest='configfile', type=str)
        configFile = configSetting.parse_args().configfile
        config.read(configFile)
        if CheckParser(config):
            try:
                AliAccount = config.get("Aliyun", "AccountList").replace('\n','')
                for aliAccount in eval(AliAccount):
                    p.apply_async(CheckAliyun, args=(aliAccount['secretId'],
                                                     aliAccount['secretKey'],
                                                     aliAccount['zone'],
                                                     aliAccount['account'],
                                                     aliAccount['limit'],
                                                     config.get('Telegram', 'ChannelId'),
                                                     config.get('Telegram', 'BotToken')))
                TenAccount = config.get("Tencent", "AccountList").replace('\n','')
                for tenAccount in eval(TenAccount):
                    p.apply_async(CheckTencent, args=(tenAccount['secretId'],
                                                      tenAccount['secretKey'],
                                                      tenAccount['account'],
                                                      tenAccount['limit'],
                                                      config.get('Telegram', 'ChannelId'),
                                                      config.get('Telegram', 'BotToken')))
            except Exception as e:
                logging.error(e)
    except Exception as e:
        try:
            logging.error(e)
        except:
            print(e)
    p.close()
    p.join()