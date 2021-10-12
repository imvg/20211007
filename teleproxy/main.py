#!/usr/bin/python3
# -*- coding: utf-8 -*-
from gevent import monkey, pywsgi

monkey.patch_all()
from flask import *
import requests
import datetime

app = Flask(__name__)


@app.route('/send', methods=['POST'])
def send():
    try:
        BotToken = request.form['BotToken']
        ChannelId = request.form['ChannelId']
        Message = request.form['Message']
        try:
            data = {'chat_id': str(ChannelId).replace('\'', ''), 'text': Message}
            requests.post(url=f'https://api.telegram.org/bot{BotToken}/sendMessage', data=data)
            app.logger.info(f'{datetime.datetime.now()} 消息发送成功 {Message}')
            return 'Success', 200
        except Exception as e:
            app.logger.error(f'{datetime.datetime.now()} 消息发送失败 {e}')
            return 'Failure', 200
    except Exception as e:
        app.logger.error(f'{datetime.datetime.now()} 异常 {e}')
        return 'Error', 200

@app.route('/cdbwarn', methods=['POST'])
def cdbWarning():
    try:
        warningData = request.get_data().decode()
        try:
            warningData = json.loads(warningData)
            alarmStatus = warningData['alarmStatus']
            policyName = warningData['alarmPolicyInfo']['policyName']
            policyCnName = warningData['alarmPolicyInfo']['policyTypeCName']
            insName = warningData['alarmObjInfo']['namespace']
            insId = warningData['alarmObjInfo']['dimensions']['objName']
            warningName = warningData['alarmPolicyInfo']['conditions']['metricName']
            calcType = warningData['alarmPolicyInfo']['conditions']['calcType']
            calcValue = warningData['alarmPolicyInfo']['conditions']['calcValue']
            currentValue = warningData['alarmPolicyInfo']['conditions']['currentValue']
            unit = warningData['alarmPolicyInfo']['conditions']['unit']

            warningType = ""
            if alarmStatus == "1":
                warningType = "触发告警‼️"
            elif alarmStatus == "0":
                warningType = "告警恢复✅"
            Message = f"腾讯云 {warningType}\n" \
                      f"产品:{insName}, 策略:{policyName}({policyCnName})\n" \
                      f"实例: {insId}, 触发告警策略值: {warningName} {calcType} {calcValue}{unit}\n" \
                      f"当前告警值: {currentValue}{unit}"
            BotToken = "1590534238:AAFYL23LSVWZdZi4H_Q_Fy7v1ivggD7UBs9"
            ChannelId = "-1001398844049"
            data = {'chat_id': str(ChannelId).replace('\'', ''), 'text': Message}
            requests.post(url=f'https://api.telegram.org/bot{BotToken}/sendMessage', data=data)
            app.logger.info(f'{datetime.datetime.now()} 腾讯云告警消息发送成功 {warningName} {currentValue}{unit}')
        except Exception as e:
            app.logger.error(f'{datetime.datetime.now()} 腾讯云告警消息发送失败 {e}')
            app.logger.error(warningData)
    except Exception as e:
        app.logger.error(f'{datetime.datetime.now()} 腾讯云告警异常 {e}')
    finally:
        return 'ok', 200


if __name__ == '__main__':
    app.debug = True
    server = pywsgi.WSGIServer(('0.0.0.0', 8899), app)
    server.serve_forever()
