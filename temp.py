# -*- coding: utf-8 -*-
import re
import os
import logging
import subprocess

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)

apkdir = "/Users/mobile/.jenkins/workspace/vod-android-release-latest/release"
apkServer = "47.57.228.71"

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
        logging.info('安卓自动打包上传完成')
        return True
    except Exception as e:
        logging.info(f"安卓APK上传失败 {e}", chat_id='-1001398844049')
        logging.error(e)
        return False

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
    upload()
