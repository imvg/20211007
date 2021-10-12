#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import *
import threading
import subprocess
import requests
import re
import os

app = Flask(__name__)
app.logger.setLevel("INFO")


@app.route('/', methods=['POST', 'GET'])
def root():
    return "你干啥", 200


@app.route('/pack/<merchant>/<agent>', methods=['POST', 'GET'])
def pack(merchant, agent):
    data = buildAction(merchant, agent)
    return data, 200


def buildAction(merchant, agent):
    dic = {
        "lubei": {"projectDir": "/root/mobile-android", "apkHost": "47.57.228.71"},
        "lu91": {"projectDir": "/root/mobile-android", "apkHost": "47.75.97.13"},
        "duck": {"projectDir": "/root/mobile-android", "apkHost": "47.75.122.198"}
    }
    if merchant not in dic.keys():
        return 'Merchant Not Found'

    threading.Thread(target=buildWorker,
                     args=(merchant,
                           agent,
                           dic[merchant]['projectDir'],
                           dic[merchant]['apkHost'])
                     ).start()
    return 'okay'


def buildWorker(merchant, agent, projectDir, apkHost):
    command = f"cd {projectDir} && pwd && ./packageChannel2.sh {merchant} release {agent}"
    ishave = os.popen(f"ls -lh {projectDir}/release | grep {agent} | grep {merchant} | awk " + "'{print $9}'").read().strip()
    if ishave:
        app.logger.info(f"渠道包已存在 删除 {ishave}")
        os.remove(f"{projectDir}/release/{ishave}")
    if build(command):
        channelPackage = os.popen(f"ls -lh {projectDir}/release | grep {agent} | grep {merchant} | awk " + "'{print $9}'").read().strip()
        reSign(projectDir, channelPackage, '/root/sign.txt')
        spath = f"{projectDir}/release/{channelPackage}"
        if upload(spath, apkHost, f'/home/wwwroot/apks/android/{agent}.apk'):
            app.logger.info(f"APK上传成功")
            sendMessage(f"<{merchant}> 渠道包打包完成 {agent}")
        else:
            sendMessage(f"<{merchant}> !!渠道包打包失败 {agent}")


def build(command):
    try:
        ret = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        app.logger.info(f"打包APK {command}")
        spres = True
        while True:
            if ret.poll() is None:
                # 切片详细日志
                runlog = ret.stdout.readline()
                app.logger.info(f"打包日志: {runlog.decode().strip()}")
                continue
            else:
                if ret.wait() != 0:
                    app.logger.error('打包失败')
                    spres = False
                    break
                else:
                    break
        return spres
    except Exception as e:
        app.logger.error(f"打包失败 {e}")


def upload(spath, host, dpath):
    try:
        command = f"scp {spath} root@{host}:{dpath}"
        app.logger.info(f"APK上传 {command}")
        ret = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        upres = True
        while True:
            if ret.poll() is None:
                runlog = ret.stdout.readline()
                continue
            else:
                if ret.wait() != 0:
                    app.logger.error('上传失败')
                    upres = False
                break
        return upres
    except Exception as e:
        app.logger.error(f"上传失败 {e}")


def reSign(projectDir, channelPackage, signFile):
    try:
        channelSign = re.split('=', re.split(' ', os.popen(f"{projectDir}/packageInfo.sh {projectDir}/release/{channelPackage}").readlines()[0].strip())[-1])[0]
        app.logger.info(f"New Sign {channelSign}")
        with open(signFile, 'r') as f:
            signData = json.loads(f.read())
            nowSign = signData['packageNames']
            nowUrl = signData['url']
        newSign = nowSign + [channelSign]
        newUrl = nowUrl + ['mili']
        saveCount = 1000
        if len(newSign) > saveCount:
            cut = len(newSign) - saveCount
            newSign = newSign[cut:]
            newUrl = newUrl[cut:]
        if len(newSign) == len(newUrl):
            newPackageNamesData = ','.join(newSign)
            newUrlData = ','.join(newUrl)
            flushurl = f"http://518.config.lng11.com/set.php?packageNames={newPackageNamesData}&url={newUrlData}&download=http://lubei.tv"
            requests.get(flushurl, timeout=20)
            with open(signFile, 'w') as f:
                saveData = {'packageNames': newSign, 'url': newUrl}
                f.write(json.dumps(saveData))
            app.logger.info("Sign Finnish")
        else:
            app.logger.error(f"Sing和Url的数量不一致")
    except Exception as e:
        app.logger.error(f"提交签名失败 {e}")


def sendMessage(msg):
    data = {'chat_id': '-1001175029636', 'text': msg}
    token = '1590534238:AAFYL23LSVWZdZi4H_Q_Fy7v1ivggD7UBs9'
    try:
        requests.post(url=f'https://api.telegram.org/bot{token}/sendMessage', data=data)
        return True
    except Exception as err:
        app.logger.error(f'消息发送失败 {err}')
        return False


if __name__ == '__main__':
    try:
        # from werkzeug.debug import DebuggedApplication
        # dapp = DebuggedApplication(app, evalex=True)

        app.debug = False
        # server = pywsgi.WSGIServer(('0.0.0.0', 8899), app)
        app.run('0.0.0.0', 80)
    except Exception as e:
        print(e)
