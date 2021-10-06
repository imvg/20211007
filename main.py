#!/usr/bin/python3
# -*- coding: utf-8 -*-
import oss2
import logging
import os
import re
import time
import json
import requests
import subprocess

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)


auth = oss2.Auth('LTAI5tDdKhFEdpVGTGUXsQep', 'BknC4YsgBALzxLwIC8Jy5sAZ91Fcx9')  # luzhuanyong001
bucket = oss2.Bucket(auth, 'http://oss-accelerate.aliyuncs.com', '91apk20210901')
projectDir = '/Users/mobile/.jenkins/workspace/vod-android-release-91lu'
apkdir = f'{projectDir}/release'
signFile = '/Users/mobile/Library/resign/mili-sign.txt'
apkServer = '47.75.97.13'


def sendMessage(msg, chat_id='-1001175029636'):
    data = {'chat_id': chat_id, 'text': '<撸呗> '+msg}
    token = '1590534238:AAFYL23LSVWZdZi4H_Q_Fy7v1ivggD7UBs8'
    try:
        res = requests.post(url=f'https://api.telegram.org/bot{token}/sendMessage', data=data, timeout=30)
        if res.status_code != 200:
            logging.error(f'消息发送失败, 接口返回值: {res}')
    except Exception as err:
        logging.error(f'消息发送失败 {err}')


def build():
    try:
        res1 = True
        res2 = True
        os.system(f"rm -f {projectDir}/release/*")
        command1 = f"cd {projectDir} && ./packageMain.sh android 5"
        ret = subprocess.Popen(command1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            if ret.poll() is None:
                runlog = ret.stdout.readline()
                logging.debug(runlog.decode('utf-8').strip())
                continue
            else:
                if ret.wait() != 0:
                    logging.warning("主包打包失败")
                    sendMessage("安卓主包APK打包失败")
                    res1 = False
                else:
                    sendMessage("安卓主包APK打包成功, 上传中...")
                    res1 = True
                break

        command2 = f"cd {projectDir} && ./packageChannel.sh o147 release build"
        ret = subprocess.Popen(command2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            if ret.poll() is None:
                runlog = ret.stdout.readline()
                logging.debug(runlog.decode('utf-8').strip())
                continue
            else:
                if ret.wait() != 0:
                    logging.warning("渠道包打包失败")
                    sendMessage("安卓渠道包APK打包失败")
                    res2 = False
                else:
                    sendMessage("安卓渠道包APK打包成功, 上传中...")
                    res2 = True
            break
        if res1 and res2:
            return True
        else:
            return False
    except Exception as e:
        logging.error(e)
        return False


def upload():
    try:
        for file in os.listdir(apkdir):
            if file.startswith('o147_release'):
                command = f"scp {apkdir}/{file} root@{apkServer}:/home/wwwroot/apks/android/android.apk"
                runShell(command)
            else:
                apkname = re.split('_', file)[1]
                command = f"scp {apkdir}/{file} root@{apkServer}:/home/wwwroot/apks/android/{apkname}.apk"
                runShell(command)
        sendMessage('安卓自动打包上传完成')
        return True
    except Exception as e:
        sendMessage(f"安卓APK上传失败 {e}", chat_id='-1001398844049')
        logging.error(e)
        return False


def bakUpload():
    try:
        nowHour = int(time.mktime(time.strptime(time.strftime("%Y-%m-%d %H", time.localtime()), "%Y-%m-%d %H")))
        nextHour = nowHour + 3600
        lastHour = nowHour + 3600 + 3600
        dirs = [nowHour]
        for d in dirs:
            runShell(f"ssh root@{apkServer} 'mkdir /home/wwwroot/apks/{d}'")
            for file in os.listdir(apkdir):
                if file.startswith('o147_release'):
                    command = f"scp {apkdir}/{file} root@{apkServer}:/home/wwwroot/apks/{d}/android.apk"
                    runShell(command)
                else:
                    apkname = re.split('_', file)[1]
                    command = f"scp {apkdir}/{file} root@{apkServer}:/home/wwwroot/apks/{d}/{apkname}.apk"
                    runShell(command)
        return True
    except Exception as e:
        sendMessage(f"安卓APK上传失败 {e}", chat_id='-1001398844049')
        logging.error(e)
        return False


def reSign():
    try:
        channelPackage = os.popen(f"ls -lh {projectDir}/release | grep o147_release | awk "+"'{print $9}'").read().strip()
        apk1Sign = re.split('=', re.split(' ', os.popen(f"{projectDir}/packageInfo.sh {projectDir}/release/o147_android1_release.apk").readlines()[0].strip())[-1])[0]
        apk2Sign = re.split('=', re.split(' ', os.popen(f"{projectDir}/packageInfo.sh {projectDir}/release/o147_android2_release.apk").readlines()[0].strip())[-1])[0]
        apk3Sign = re.split('=', re.split(' ', os.popen(f"{projectDir}/packageInfo.sh {projectDir}/release/o147_android3_release.apk").readlines()[0].strip())[-1])[0]
        apk4Sign = re.split('=', re.split(' ', os.popen(f"{projectDir}/packageInfo.sh {projectDir}/release/o147_android4_release.apk").readlines()[0].strip())[-1])[0]
        apk5Sign = re.split('=', re.split(' ', os.popen(f"{projectDir}/packageInfo.sh {projectDir}/release/o147_android5_release.apk").readlines()[0].strip())[-1])[0]
        channelSign = re.split('=', re.split(' ', os.popen(f"{projectDir}/packageInfo.sh {projectDir}/release/{channelPackage}").readlines()[0].strip())[-1])[0]

        with open(signFile, 'r') as f:
            signData = json.loads(f.read())
            nowSign = signData['packageNames']
            nowUrl = signData['url']
        newSign = nowSign + [apk1Sign, apk2Sign, apk3Sign, apk4Sign, apk5Sign, channelSign]
        newUrl = nowUrl + ['mili'] * 6
        saveCount = 100
        if len(newSign) > saveCount:
            cut = len(newSign) - saveCount
            newSign = newSign[cut:]
            newUrl = newUrl[cut:]
        if len(newSign) == len(newUrl):
            newPackageNamesData = ','.join(newSign)
            newUrlData = ','.join(newUrl)
            flushurl = f"http://518.config.lng11.com/set.php?packageNames={newPackageNamesData}&url={newUrlData}&download=http://lubei.tv"
            requests.get(flushurl, timeout=20)
            logging.info(newSign)
            logging.info(newUrl)
            logging.info(flushurl)
            with open(signFile, 'w') as f:
                saveData = {'packageNames': newSign, 'url': newUrl}
                f.write(json.dumps(saveData))
        else:
            logging.error(f"Sing和Url的数量不一致")
    except Exception as e:
        logging.error(f"提交签名失败 {e}")


def runShell(command):
    runlog = []
    runStatus = 0
    logging.info(f"执行命令: {command}")
    runRes = subprocess.Popen(command,
                              shell=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              encoding='utf-8',
                              env={'LANG': 'zh_CN.UTF-8'})
    while True:
        if runRes.poll() is None:
            # 详细日志
            logs = runRes.stdout.readline()
            logging.debug(f"命令执行输出: {logs.strip()}")
            if logs.strip() != '':
                runlog.append(logs.strip())
            continue
        else:
            runStatus = runRes.wait()
            if runRes.wait() != 0:
                logging.error(f"命令执行失败 {command}")
            break
    resData = {'status': runStatus, 'runlog': runlog}
    return resData


if __name__ == '__main__':
    buildres = build()
    upres = upload()
    bakUpload()
    if upres:
        reSign()