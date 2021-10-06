#!/bin/python3
# -*- coding: utf-8 -*-
import logging
import time
import datetime
import json
import pymysql
from requests import session
from requests import exceptions
from requests.adapters import HTTPAdapter

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


class report:
    def __init__(self):
        self.req = session()
        self.req.mount('http://', HTTPAdapter(max_retries=3))
        self.token = "1af86032f84bd87f325a9f4be783d7af"
        self.ttime = int(time.mktime(datetime.date.today().timetuple()))
        self.ftime = self.ttime - 86400
        self.header = {
            "Host": "kjgsbzhgs.com",
            "Connection": "keep-alive",
            "Content-Length": "230",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "http://kjgsbzhgs.com",
            "Referer": "http://kjgsbzhgs.com/admin.html",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cookie": f"token={self.token}; acw_tc=ac11000116297383026032374e49532a529e9ac125921ed1940c30468d66e9",
        }

        self.connection = self._connMysql()

    def getUserList(self):
        try:
            logging.info("获取用户列表数据...")
            url = "http://kjgsbzhgs.com/user/pf_list_with_game"
            postdata = f"channel_id=" \
                       "&open_channel_id=" \
                       "&id=" \
                       "&game_user_id=" \
                       "&is_bind=" \
                       "&nickname=" \
                       "&is_online=" \
                       "&reg_ip=" \
                       "&is_recharge=" \
                       "&device_type=" \
                       "&mobile=" \
                       "&apns_code=" \
                       f"&begin_time={self.ftime}" \
                       f"&end_time={self.ttime}" \
                       "&page_size=99999999999" \
                       "&page=1" \
                       f"&token={self.token}"
            data = self.sendRequests(url, postdata)
            if data.status_code == 200:
                if len(json.loads(data.text)['result']) > 0:
                    logging.info(f"用户列表获取到 {len(json.loads(data.text)['result'])} 条数据")
                    return json.loads(data.text)['result']
                else:
                    raise RuntimeError(f"接口 {url} 返回状态码 {data.status_code}")
        except Exception as e:
            logging.error(f"获取用户列表异常 {e}")
            raise RuntimeError(e)

    def getCashData(self):
        try:
            logging.info(f"获取绑定列表数据...")
            page = 1
            url = "http://kjgsbzhgs.com/pp_user_payway/list"
            res = []
            while True:
                postdata = "channel_i=0" \
                           "&channel_ii=0" \
                           "&user_id=" \
                           "&pay_type=" \
                           "&bank_card=" \
                           "&bank_account_name=" \
                           "&is_black=" \
                           f"&page={page}" \
                           "&page_size=20" \
                           f"&token={self.token}"
                data = self.sendRequests(url, postdata)
                if len(json.loads(data.text)['result']) > 0:
                    for cashInfo in json.loads(data.text)['result']:
                        res.append(cashInfo)
                    page += 1
                    # break
                    continue
                else:
                    break
            logging.info(f"绑定列表获取到 {len(res)} 条数据")
            return res
        except Exception as e:
            logging.error(f"获取银行卡绑定异常 {e}")
            raise RuntimeError(e)

    def getGameData(self, userId):
        try:
            url = "http://kjgsbzhgs.com/user/get_user_game_data"
            postdata = f"user_id={userId}&token={self.token}"
            data = self.sendRequests(url, postdata)
            if len(json.loads(data.text)['result']) == 0:
                lostdata = {
                    'avatar': 'none',
                    'money': 0,
                    'apns_code': 'none',
                    'is_freeze': 0,
                    'delete_time': 0,
                    'device_type': 'none',
                    'actor_rooms': '',
                    'trade': 0,
                    'money_tg': 0,
                    'star': 0,
                    'last_pingpong': 0,
                    'my_icode': 0,
                    'is_game_black': 0,
                    'flag': 0,
                    'create_time': 0,
                    'app_user_id': '0',
                    'parent_id': 'none',
                    'app_id': 'none',
                    'online_time': 0,
                    'mobile': 'none',
                    'last_login': 'none',
                    'vip_expire_time': 0,
                    'tree_path': '',
                    'nickname': '用户不存在',
                    'fs_level': 0,
                    'total_recharge': 0,
                    'total_cash': 0,
                    'id': 0,
                    'is_game_online': '0'
                }
                return lostdata
            else:
                return json.loads(data.text)['result'][0]
        except Exception as e:
            logging.error(f"获取用户游戏数据异常 {userId} {e}")
            raise RuntimeError(e)

    def getGameOrder(self):
        try:
            logging.info(f"获取游戏日志...")
            url = "http://kjgsbzhgs.com/pp_game_log/pf_list"
            postdata = "channel_id=" \
                       "&open_channel_id=" \
                       "&pid=" \
                       "&game_type=" \
                       "&user_id=" \
                       "&transfer_id=" \
                       f"&begin_time={self.ftime}" \
                       f"&end_time={self.ttime}" \
                       "&page_size=999999999" \
                       "&page=1" \
                       "&channel_i=" \
                       "&channel_ii=" \
                       f"&token={self.token}"
            data = self.sendRequests(url, postdata)
            logging.info(f"游戏日志获取到 {len(json.loads(data.text)['result'])} 条数据")
            if len(json.loads(data.text)['result']) > 0:
                return json.loads(data.text)['result']
        except Exception as e:
            logging.error(f"获取游戏日志异常 {e}")
            raise RuntimeError(e)

    def getPaymentMethodList(self):
        try:
            logging.info("获取接口方式列表...")
            url = "http://kjgsbzhgs.com/payment_class/pf_list"
            paymentMethodList = []
            postdata = "name=" \
                       "&pay_type=" \
                       "&is_effect=" \
                       "&sort_field=create_time" \
                       "&sort_type=desc" \
                       f"&page=1" \
                       "&page_size=999999999" \
                       "&channel_id=" \
                       f"&token={self.token}"
            data = self.sendRequests(url, postdata)
            if len(json.loads(data.text)['result']) > 0:
                logging.info(f"支付接口列表获取到 {len(json.loads(data.text)['result'])} 条数据")
                for paymentMethod in json.loads(data.text)['result']:
                    paymentMethodList.append(paymentMethod)
            return paymentMethodList
        except Exception as e:
            logging.error(f"获取支付方式列表异常 {e}")
            raise RuntimeError(e)

    def getGameList(self):
        try:
            logging.info("获取游戏列表...")
            url = "http://kjgsbzhgs.com/pp_game_list/pf_list"
            postdata = "channel_id=hb" \
                       "&pid=" \
                       "&name=" \
                       "&game_type=" \
                       "&page=1" \
                       "&page_size=999999999" \
                       "&order_by=id%20asc" \
                       f"&token={self.token}"
            req = self.sendRequests(url, postdata)
            if "result" in json.loads(req.text).keys():
                logging.info(f"游戏列表共获取到 {len(json.loads(req.text)['result'])} 条数据")
                return json.loads(req.text)['result']
        except Exception as e:
            logging.error(f"获取游戏列表异常 {e}")
            raise RuntimeError(e)

    def getMoneyLog(self):
        try:
            logging.info("获取金钱日志...")
            page = 1
            url = "http://kjgsbzhgs.com/pp_game_money_log/pf_list"
            res = []
            while True:
                postdata = "channel_id=" \
                           "&open_channel_id=" \
                           "&oper_type2=" \
                           "&oper_type=" \
                           "&pid=" \
                           "&game_id=" \
                           "&user_id=" \
                           "&mobile=" \
                           f"&begin_time={self.ftime}" \
                           f"&end_time={self.ttime}" \
                           "&page_size=20" \
                           f"&page={page}" \
                           "&channel_i=" \
                           "&channel_ii=" \
                           f"&token={self.token}"
                req = self.sendRequests(url, postdata)
                for data in json.loads(req.text)['result']:
                    res.append(data)
                logging.debug(f"游戏金钱日志第 {page} 页获取到 {len(json.loads(req.text)['result'])} 条数据 {json.loads(req.text)['result']}")
                if len(json.loads(req.text)['result']) > 0:
                    page += 1
                    continue
                    # break
                else:
                    break
            logging.info(f"金钱日志获取到 {len(res)} 条数据")
            return res
        except Exception as e:
            logging.error(f"生成金钱日志 {e}")
            raise RuntimeError(e)

    def makeUserInfo(self, cashList, gameOrder, userList):
        try:
            num = 1
            logging.info(f"生成用户信息, 共 {len(userList)} 条数据...")
            for userInfo in userList:
                gameData = ins.getGameData(userInfo['id'])
                userRealName = "-"
                userBankCard = ""
                userBankName = ""
                for realInfo in cashList:
                    if gameData['id'] == realInfo['user_id']:
                        userRealName = realInfo['bank_account_name']
                        userBankCard = realInfo['bank_card']
                        userBankName = realInfo['bank_name']
                userCashTotal = 0
                userLostWin = 0
                for userCash in gameOrder:
                    if gameData['id'] == userCash['user_id']:
                        userCashTotal += float(str(userCash['bet']).replace('-', ''))
                        userLostWin += userCash['win'] - float(str(userCash['bet']).replace('-', ''))
                userData = {
                    "用户id": userInfo['id'],
                    "游戏id": gameData['id'],
                    "昵称": userInfo['nickname'],
                    "真实姓名": userRealName,
                    "所属代理": userInfo['open_channel_id'],
                    "余额": gameData['money'],
                    "充值金额": gameData['total_recharge'],
                    "提现金额": gameData['total_cash'],
                    "投注金额": userCashTotal,
                    "输赢": userLostWin,
                    "消费钻石": userInfo['use_diamond'],
                    "剩余钻石": userInfo['diamond'],
                    "最后登录ip/地区": userInfo['last_ip'] + "/" + userInfo['pre_ip_adress'],
                    "注册时间": str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(userInfo['create_time']))),
                    "最后登录时间": str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(userInfo['last_login']))),
                    "设备类型": userInfo['device_type'],
                    "银行卡号": userBankCard,
                    "银行名称": userBankName
                }
                self.saveBase('t_broadcast_report_user', userData)
                num += 1
        except Exception as e:
            logging.error(f"用户列表信息统计异常 {e}")
            raise RuntimeError(e)

    def makeRechargeDetails(self):
        try:
            logging.info("生成充值明细...")
            url = 'http://kjgsbzhgs.com/payment_log/list_payment_log'
            paymentMethodList = self.getPaymentMethodList()
            postdata = "page_size=999999999" \
                       "&page=1" \
                       "&channel_id=" \
                       "&open_channel_id=" \
                       "&is_pay=" \
                       "&send_item_time=" \
                       f"&begin_time={self.ftime}" \
                       f"&end_time={self.ttime}" \
                       "&is_first_recharge=0" \
                       "&payment_class_id=" \
                       "&nickname=" \
                       "&order_id=" \
                       "&out_order_id=" \
                       "&money_type=1" \
                       "&oper_user=" \
                       "&content=" \
                       "&content2=" \
                       "&content_list=" \
                       "&min_money=" \
                       "&max_money=" \
                       "&user_id=" \
                       f"&token={self.token}"
            data = self.sendRequests(url, postdata)
            if len(json.loads(data.text)['result']) > 0:
                logging.info(f"充值明细接口获取到 {len(json.loads(data.text)['result'])} 条数据")
                for orderInfo in json.loads(data.text)['result']:
                    for method in paymentMethodList:
                        if orderInfo['payment_class_id'] == method['id']:
                            orderInfo['payment_class_id'] = method['firm_name']
                    # logging.debug(f"{num} 获取到充值订单 {orderInfo['order_id']}")
                    self.saveBase('t_broadcast_recharge_details', orderInfo)
        except Exception as e:
            logging.error(f"生成充值明细异常 {e}")
            raise RuntimeError(e)

    def makeWithdrawalDetails(self):
        try:
            logging.info("生成提现明细...")
            url = "http://kjgsbzhgs.com/pp_cash/pf_list"
            postdata = "channel_i=" \
                       "&channel_ii=" \
                       "&user_id=" \
                       "&nickname=" \
                       "&order_id=" \
                       "&status=" \
                       f"&begin_time={self.ftime}" \
                       f"&end_time={self.ttime}" \
                       "&send_status=" \
                       "&page=1" \
                       "&page_size=999999999" \
                       "&is_manual=" \
                       "&op_user_id=" \
                       "&bank_account_name=" \
                       "&min_money=" \
                       "&max_money=" \
                       "&cash_class_id=" \
                       f"&token={self.token}"
            data = self.sendRequests(url, postdata)
            if len(json.loads(data.text)['result']) > 0:
                logging.info(f"提现管理接口获取到 {len(json.loads(data.text)['result'])} 条数据")
                for orderInfo in json.loads(data.text)['result']:
                    self.saveBase('t_broadcast_withdrawal_details', orderInfo)
        except Exception as e:
            logging.error(f"生成提款明细异常 {e}")
            raise RuntimeError(e)

    def makeGameLog(self, data):
        try:
            gameList = self.getGameList()
            logging.info(f"生成游戏日志数据, 共 {len(data)} 条数据")
            for gameOrder in data:
                gameCode = gameOrder['game_type']
                gameOrder['game_type'] = "未取到"
                for gameName in gameList:
                    if gameCode == gameName['params']:
                        gameOrder['game_type'] = gameName['name']
                self.saveBase("t_broadcast_game_log", gameOrder)
        except Exception as e:
            logging.error(f"生成游戏日志异常 {e}")
            raise RuntimeError(e)

    def makeOperationTable(self):
        try:
            url1 = "http://kjgsbzhgs.com/data_statistics/pf_list"
            url2 = "http://kjgsbzhgs.com/pp_service/pf_game_overview"
            postdata1 = "channel_id=" \
                        "&device_type=" \
                        f"&begin_time={self.ftime}" \
                        f"&end_time={self.ttime}" \
                        "&open_channel_id=" \
                        f"&token={self.token}"
            postdata2 = "channel_id=" \
                        "&device_type=" \
                        f"&begin_time={self.ftime}" \
                        f"&end_time={self.ttime}" \
                        "&open_channel_id=" \
                        f"&token={self.token}"
            logging.info(f"获取运营报表数据")
            req1 = self.sendRequests(url1, postdata1)
            req2 = self.sendRequests(url2, postdata2)
            reqdata = {**json.loads(req1.text)['data'], **json.loads(req2.text)['result'][0]}
            self.saveBase("t_broadcast_operation_table", reqdata)
        except Exception as e:
            logging.error(f"生成数据总表异常 {e}")
            raise RuntimeError(e)

    def makeMoneyLog(self, data):
        try:
            gameList = self.getGameList()
            oper_type = {
                1: "充值加钱",
                2: "提现扣钱",
                12: "提现预扣",
                13: "提现返还",
                19: "充值活动返利",
                23: "兑换钻石",
                25: "公司入款充值",
                28: "游戏上分",
                29: "游戏上分失败",
                52: "游戏赢",
                53: "游戏输",
                54: "押注",
                55: "开奖"
            }
            oper_type2 = {
                1: "收入",
                2: "支出",
                3: "充值",
                4: "提现"
            }
            logging.info(f"生成金钱日志, 共 {len(data)} 条数据")
            for res in data:
                if res['oper_type'] in oper_type.keys():
                    res['oper_type'] = oper_type[res['oper_type']]
                if res['oper_type2'] in oper_type2.keys():
                    res['oper_type2'] = oper_type2[res['oper_type2']]
                gameCode = res['game_id']
                res['game_id'] = "-"
                for gameName in gameList:
                    if gameCode == gameName['params']:
                        res['game_id'] = gameName['name']
                    if gameCode == "0":
                        res['game_id'] = "系统"
                        res['pid'] = "系统"
                self.saveBase("t_broadcast_money_log", res)
        except Exception as e:
            logging.error(f"生成金钱日志异常 {e} {data}")
            raise RuntimeError(e)

    def sendRequests(self, url, postdata):
        try:
            data = self.req.post(url, data=postdata, headers=self.header, timeout=60)
            if data.status_code == 200:
                if "result" in json.loads(data.text).keys() or "data" in json.loads(data.text).keys():
                    if "url" == "http://kjgsbzhgs.com/user/get_user_game_data":
                        time.sleep(0.1)
                        return data
                    else:
                        return data
                elif json.loads(data.text)['msg'] == "timeout":
                    logging.error(f"接口 {url} 返回 {json.loads(data.text)}, 等待30秒重试...")
                    time.sleep(30)
                    return self.sendRequests(url, postdata)
                else:
                    raise RuntimeError(f"接口 {url} 返回数据不存在result")
            elif data.status_code == 429:
                after = data.headers['Retry-After']
                logging.debug(f"请求频繁，等待 {after} 秒")
                time.sleep(int(after)+1)
                return self.sendRequests(url, postdata)
            elif data.status_code >= 500:
                logging.debug(f"接口返回状态码 {data.status_code}, 疑似Cloudflare拦截, 等待20秒重试")
                time.sleep(20)
                return self.sendRequests(url, postdata)
            else:
                logging.error(f"状态码异常 {url} {data.status_code} {data.text}")
                raise RuntimeError(f"状态码异常 {url} {data.status_code} {data.text}")
        except exceptions.Timeout as e:
            logging.warning(f"接口 {url} {e}, 十秒后重试..")
            time.sleep(10)
            return self.sendRequests(url, postdata)
        except Exception as e:
            raise RuntimeError(e)

    def saveBase(self, table, data):
        try:
            self.connection.ping()
        except:
            self.connection = self._connMysql()
            self.saveBase(table, data)
        else:
            date = str(time.strftime("%Y-%m-%d", time.localtime(self.ftime)))
            sql = None
            if table == "t_broadcast_report_user":
                sql = f"insert into t_broadcast_report_user(`date`, `uid`, `gid`, `nickname`, `realname`, `aid`, `coin`, `pay`, `cash`, `bet`, `profit`, `cost`, `diamond`, `ip_area`, `ctime`, `ltime`, `device`, `bankcard`, `bankcard_name`)" \
                      f"value('{date}', {data['用户id']}, {data['游戏id']}, '{data['昵称']}', '{data['真实姓名']}', '{data['所属代理']}', {data['余额']}, {data['充值金额']}, {data['提现金额']}, {data['投注金额']}, {data['输赢']}, {data['消费钻石']}, {data['剩余钻石']}, '{data['最后登录ip/地区']}', '{data['注册时间']}', '{(data['最后登录时间'])}', '{data['设备类型']}', '{data['银行卡号']}', '{data['银行名称']}')"
            elif table == "t_broadcast_recharge_details":
                maketime = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data['create_time'])))
                paytime = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data['pay_time'])))
                if data['send_item_time'] != 0:
                    sendtime = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data['send_item_time'])))
                else:
                    sendtime = paytime
                sql = f"insert into t_broadcast_recharge_details(`date`, `user`, `nickname`, `device`, `paymethod`, `amount`, `Internalorder`, `externalorder`, `maketime`, `paytime`, `shiptime`, `remark`, `operator`)" \
                      f"value('{date}', {data['user_id']}, '{data['nickname']}', '{data['device_type']}', '{data['payment_class_id']}', {float(data['money'])}, '{data['order_id']}', '{data['cp_order_id']}', '{maketime}', '{paytime}', '{sendtime}', '{data['content']}', '{data['oper_user']}')"
            elif table == "t_broadcast_withdrawal_details":
                if "send_time" in data.keys():
                    send_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data['send_time'])))
                else:
                    send_time = "2020-01-01 00:00:00"
                if "bank_card" in data.keys():
                    channel = "银行卡"
                else:
                    channel = "None"
                create_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data['create_time'])))
                sql = f"insert into t_broadcast_withdrawal_details(`date`, `order`, `initiatetime`, `arrivetime`, `gid`, `nickname`, `amount`, `channel`, `status`, `transfer`, `optiontype`, `operator`, `remark`)" \
                      f"value('{date}', '{data['order_id']}', '{create_time}', '{send_time}', {data['user_id']}, '{data['nickname']}', {data['money']}, '{channel}', {data['status']}, {data['send_status']}, {data['is_manual']}, '{data['op_user_id']}', '{data['cash_content']}')"
            elif table == "t_broadcast_game_log":
                operationtime = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data['game_time'])))
                sql = f"insert into t_broadcast_game_log(`date`, `numberid`, `gid`, `platform`, `ordernumber`, `gamename`, `operationtime`, `betamount`, `winamount`, `effectbet`, `tip`, `cancelbet`)" \
                      f"value('{date}', {data['id']}, {data['user_id']}, '{data['pid']}', '{data['transfer_id']}', '{data['game_type']}', '{operationtime}', {data['bet']}, {data['win']}, {data['available_bet']}, {data['tip']}, 'None')"
            elif table == "t_broadcast_operation_table":
                ks = data['recharge_money'] - data['cash_money'] - data['recharge_value']
                yxsy = 0
                sql = f"insert into t_broadcast_operation_table(`date`, `loginusers`, `regisusers`, `bindusers`, `rechargeusers`, `rechargeorder`, `rechargeamount`, `withdrawalusers`, `withdrawalamount`, `firstrechargeusers`, `firstrechargeamount`, `onlinerechargeamount`, `backrechargeamount`, `kdrechargeamount`, `cprechargeamount`, `dmexchangeusers`, `dmexchangeamount`, `dmexchangecount`, `firstexchangeusers`, `firstexchangeamount`, `firstexchangecount`, `betusers`, `efbet`, `userloss`, `gamewinloss`, `promotiongift`, `userordergift`, `brokerageusers`, `brokerageamount`, `anchorlotteryshare`)" \
                      f"value('{date}', {data['huoyue_online']}, {data['reg_count']}, {data['bind_count']}, {int(data['recharge_role'])}, {int(data['recharge_times'])}, {data['recharge_money']}, {int(data['cash_role'])}, {data['cash_money']}, {int(data['first_recharge_role'])}, {data['first_recharge_money']}, {data['online_recharge']}, {data['pf_recharge_money']}, {data['kedan_recharge']}, {data['gs_recharge']}, {data['recharge_user_count']}, {data['recharge_value']}, {data['recharge_diamond']}, {data['first_recharge_count']}, {data['first_recharge_value']}, {data['first_recharge_diamond']}, {int(data['bet_role'])}, {data['available_bet_sum']}, {ks}, {yxsy}, {data['activity_money']}, {data['gift_cost']}, {data['give_tg_role']}, {data['give_tg_money']}, {data['ticket_for_podcast']})"
                logging.debug(sql)
            elif table == "t_broadcast_money_log":
                dtime = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data['time'])))
                sql = f"insert into t_broadcast_money_log(`date`, `order`, `gid`, `nickname`, `mobile`, `time`, `platform`, `gamename`, `type`, `specitype`, `amount`, `balance`)" \
                      f"value('{date}', {data['id']}, {data['user_id']}, '{data['nickname']}', '{data['mobile']}', '{dtime}', '{data['pid']}', '{data['game_id']}', '{data['oper_type2']}', '{data['oper_type']}', {data['money']}, {data['new_val']})"
            try:
                with self.connection.cursor() as cur:
                    cur.execute(sql)
                    self.connection.commit()
                    return True
            except Exception as e:
                logging.error(f"写入数据库失败 {e} {data}")
                logging.error(sql)
                raise RuntimeError(e)

    def _connMysql(self):
        return pymysql.connect(host="hk-cdb-aumsfh1d.sql.tencentcdb.com", user="root", password="wvqhthpbd!Wv$da4", port=63734,db="db_yy")
        # return pymysql.connect(host="101.32.202.66", user="root", password="1q2w3e4r..A", port=3306, db="db_yy_1",
        #                        connect_timeout=10, write_timeout=10)

    def _sendMessage(self, msg):
        data = {'chat_id': '-1001175029636', 'text': msg}
        token = '1590534238:AAFYL23LSVWZdZi4H_Q_Fy7v1ivggD7UBs8'
        try:
            self.req.post(url=f'https://api.telegram.org/bot{token}/sendMessage', data=data)
        except Exception as err:
            logging.error(f'消息发送失败 {err}')
            raise RuntimeError(f'消息发送失败 {err}')

    def __del__(self):
        self.connection.close()


if __name__ == '__main__':
    ins = report()
    try:
        logging.debug(f'查询开始时间 {str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ins.ftime)))}')
        logging.debug(f'查询结束时间 {str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ins.ttime)))}')
        ins._sendMessage(f'花瓣报表开始取数据 {str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))}')

        # userList = ins.getUserList()
        # cashList = ins.getCashData()
        gameOrder = ins.getGameOrder()
        moneyLogs = ins.getMoneyLog()
        # ins.makeUserInfo(cashList, gameOrder, userList)
        ins.makeRechargeDetails()
        ins.makeWithdrawalDetails()
        ins.makeGameLog(gameOrder)
        ins.makeOperationTable()
        ins.makeMoneyLog(moneyLogs)

        ins._sendMessage(f'花瓣报表数据取完了 {str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))}')
    except Exception as e:
        ins._sendMessage(f"报表获取数据异常 {e}")
        logging.error(f"全局异常 {e}")

        exit(-1)
