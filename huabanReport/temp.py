import requests

def _sendMessage(msg):
    data = {'chat_id': '-1001398844049', 'text': msg}
    token = '1590534238:AAFYL23LSVWZdZi4H_Q_Fy7v1ivggD7UBs8'
    try:
        requests.post(url=f'https://api.telegram.org/bot{token}/sendMessage', data=data)
    except Exception as err:
        raise RuntimeError(f'消息发送失败 {err}')

_sendMessage("123123")