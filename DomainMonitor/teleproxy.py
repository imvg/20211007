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
            print(f'{datetime.datetime.now()} 消息发送成功 {Message}')
            return 'Success', 200
        except Exception as e:
            print(f'{datetime.datetime.now()} 消息发送失败 {e}')
            return 'Failure', 200
    except Exception as e:
        print(f'{datetime.datetime.now()} 异常 {e}')
        return 'Error', 200


if __name__ == '__main__':
    app.debug = True
    server = pywsgi.WSGIServer(('0.0.0.0', 8899), app)
    server.serve_forever()
