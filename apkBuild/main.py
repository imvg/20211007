#!/bin/python3
# -*- coding: utf-8 -*-
import oss2
import logging
import os
import re
import requests
from requests import session
from requests.adapters import HTTPAdapter
import subprocess
import time

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)

# auth = oss2.Auth('LTAI4G5otMb3k5NLpCCbA5B7', 'CL3vfVxc89dzyaaLhtfWa52vmkgUso')  # xyaccount
auth = oss2.Auth('', '')  # qzh7537
bucket = oss2.Bucket(auth, 'http://oss-accelerate.aliyuncs.com', 'lubeiimages')
channelDir = '/root/mobile/android/release/'
backupDir = '/root/backup'
session = session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))


def sendMessage(msg, chat_id='-1001175029636'):
    data = {'chat_id': chat_id, 'text': msg}
    token = '1590534238:AAFYL23LSVWZdZi4H_Q_Fy7v1ivggD7UBs9'
    try:
        res = session.post(url=f'https://api.telegram.org/bot{token}/sendMessage', data=data, timeout=30)
        if res.status_code != 200:
            logging.error(f'消息发送失败, 接口返回值: {res}')
    except Exception as err:
        logging.error(f'消息发送失败 {err}')


def gitPull():
    try:
        command = "cd /root/mobile/android/ && git pull origin master"
        ret = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            if ret.poll() is None:
                runlog = ret.stdout.readline()
                logging.debug(runlog.decode('utf-8').strip())
                continue
            else:
                if ret.wait() != 0:
                    logging.warning("代码拉取失败")
                    sendMessage("代码拉取失败", chat_id='-1001398844049')
                    return False
                else:
                    return True
    except Exception as e:
        logging.error(e)
        return False


def build():
    try:
        os.system(f"rm -f {channelDir}/*")
        command = "cd /root/mobile/android/ && ./packageChannel.sh o147 release build"
        ret = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            if ret.poll() is None:
                runlog = ret.stdout.readline()
                logging.debug(runlog.decode('utf-8').strip())
                continue
            else:
                if ret.wait() != 0:
                    logging.warning("打包失败")
                    sendMessage("安卓APK打包失败", chat_id='-1001398844049')
                    return False
                else:
                    sendMessage("安卓APK打包成功, 上传中...")
                    return True
    except Exception as e:
        logging.error(e)
        return False


def upload():
    try:
        for package in os.listdir(channelDir):
            pkgPath = channelDir + package
            if package != 'output_release.apk':
                if package.startswith('o147_release'):
                    logging.debug(f"上传 {pkgPath} 至 /android/android.apk")
                    bucket.put_object_from_file('android/android.apk', pkgPath)
                else:
                    pkgChannel = re.split('_', package)[1]
                    desName = pkgChannel + '.apk'
                    logging.debug(f"上传 {pkgPath} 至 {desName}")
                    bucket.put_object_from_file('android/' + desName, pkgPath)
        sendMessage("安卓APK自动打包更新完成")
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
            for package in os.listdir(channelDir):
                pkgPath = channelDir + package
                if package != 'output_release.apk':
                    if package.startswith('o147_release'):
                        logging.debug(f"上传 {pkgPath} 至 {str(d) + '/' + 'android_' + str(d) + '.apk'}")
                        bucket.put_object_from_file(str(d) + '/' + 'android.apk', pkgPath)
                    else:
                        pkgChannel = re.split('_', package)[1]
                        desName = pkgChannel + '.apk'
                        logging.debug(f"上传 {pkgPath} 至 {str(d) + '/' + desName}")
                        bucket.put_object_from_file(str(d) + '/' + desName, pkgPath)
        return True
    except Exception as e:
        sendMessage(f"安卓APK上传失败 {e}", chat_id='-1001398844049')
        logging.error(e)
        return False


def reSign():
    try:
        logging.debug("开始提交新sign")
        pkg = os.popen("ls -lh /root/mobile/android/release/ | grep release | grep -v output | awk '{print $9}'").read()
        command = f"/root/mobile/android/packageInfo.sh /root/mobile/android/release/{pkg}"
        res = os.popen(command).read()
        log = re.split('\n', res)[0]
        sign = re.split('=', re.split(':', log)[-1])[0].strip()
        nowdata = open('/root/sign.txt', 'r')
        packageNames = ""
        url = ""
        download = ""
        saveCount = 72
        for d in nowdata.readlines():
            if "packageNames" in d:
                packageNames = re.split("'", d)[3]
                nameCount = re.split(',', packageNames)
                if len(nameCount) >= saveCount:
                    oldSign = ""
                    for s in nameCount[:saveCount - 1]:
                        oldSign += s + ','
                    packageNames = sign + "," + oldSign.strip(',')
                else:
                    packageNames = f"{sign},{packageNames}"
            if "url" in d:
                url = re.split("'", d)[3]
                urlCount = re.split(',', url)
                if len(urlCount) >= saveCount:
                    oldurl = ""
                    for s in urlCount[:saveCount - 1]:
                        oldurl += s + ','
                    url = "mili," + oldurl.strip(',')
                else:
                    url = f"mili,{url}"
            if "download" in d:
                download = re.split("'", d)[3]
        nowdata.close()
        newPackageNames = f"'packageNames' => '{packageNames}',\n"
        newUrl = f"'url' => '{url}',\n"
        newDownload = f"'download' => '{download}'"
        newData = newPackageNames + newUrl + newDownload
        with open('/root/sign.txt', 'w') as f:
            f.write(newData)
        flushurl = f"http://518.config.lng11.com/set.php?\
                    packageNames={packageNames}&\
                    url={url}&\
                    download={download}"
        requests.get(flushurl, timeout=20)
        logging.debug("新sign提交成功")
        logging.debug(f"packageNames: {packageNames}")
        logging.debug(f"url: {url}")
        logging.debug(f"download: {download}")
        return True
    except Exception as e:
        logging.error(e)
        return False


if __name__ == '__main__':
    # gitres = gitPull()
    buildres = build()
    upres = upload()
    bakUpload()
    if upres:
        reSign()
