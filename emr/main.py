#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys
import requests
import os
import time
import subprocess
import pymysql
import cv2
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from pyspark.sql import SparkSession
import logging

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


def encryptImage(filepath, vnum):
    try:
        logging.info(f"Encrypt Cover: {filepath}")
        if not os.path.exists(filepath):
            logging.error(f"Cover File Not Found {filepath}")
            return False
        data = open(filepath, 'rb').read()
        key = os.urandom(8)
        type = re.split('\.', filepath)[-1]
        save_dir = '/data/tmp'
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        with open(f'{save_dir}/{vnum}.{type}', 'wb') as enc:
            enc.write(key)
            enc.write(data)
        return f'{save_dir}/{vnum}.{type}'
    except Exception as e:
        logging.error(f"encryptImage Function Error {filepath} {e}")
        return False


def getVideoResolution(vodpath):
    logging.info(f"Get Resolution {vodpath}")
    if not os.path.exists(vodpath):
        logging.info(f"Video File Not Found {vodpath}")
        return False
    try:
        cap = cv2.VideoCapture(vodpath)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return f"{width}x{height}"
    except Exception as e:
        logging.info(f"getVideoResolution Function Error {vodpath} {e}")
        return False


def getVideoTime(vodpath):
    logging.info(f"Get Video Long Time {vodpath}")
    if not os.path.exists(vodpath):
        logging.info(f"Video File Not Found {vodpath}")
        return False
    try:
        cap = cv2.VideoCapture(vodpath)
        if cap.isOpened():
            rate = cap.get(5)
            FrameNumber = cap.get(7)
            duration = FrameNumber / rate * 1000
            return int(duration)
        else:
            logging.info(f"{vodpath} Video File Error, Can Not Get Long Time")
            return False
    except Exception as e:
        logging.info(f"getVideoTime Function Error {vodpath} {e}")
        return False


def splitVideo(filepath, fanhao):
    try:
        logging.info(f"Split Video: {filepath}")
        vodname = re.split('/', filepath)[-1]
        spdir = '/data/tmp'
        keypath = '/data/enc.keyinfo'
        splitCommand = f"ffmpeg -y -i {filepath} -hls_time 6 -hls_list_size 0 -hls_segment_filename {spdir}/{fanhao}-%05d.ts -hls_key_info_file {keypath} {spdir}/{fanhao}.m3u8"
        ret = subprocess.Popen(splitCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if not os.path.exists(spdir):
            os.mkdir(spdir)
        spres = f"{spdir}/{fanhao}.m3u8"
        while True:
            if ret.poll() is None:
                runlog = ret.stdout.readline().decode()
                logging.info(f"Split Logs: {vodname}: {runlog}")
                continue
            else:
                if ret.wait() != 0:
                    logging.info(f"Split Error")
                    logging.info(splitCommand)
                    spres = False
                    break
                else:
                    break
        return spres
    except Exception as e:
        logging.error(f"splitVideo Function Error {filepath} {e}")
        return False


def downloadFile(bucketUri):
    try:
        logging.info(f"Download File {bucketUri}")
        filename = re.split('/', bucketUri)[-1]
        downloadDir = '/data/dwfiles'
        if not os.path.exists(downloadDir):
            os.mkdir(downloadDir)
        if os.path.exists(f"{downloadDir}/{filename}"):
            os.remove(f"{downloadDir}/{filename}")
        data = requests.get(f"https://srcfiles-1304147283.cos.accelerate.myqcloud.com/{bucketUri}")
        if str(data.status_code).startswith('20') or str(data.status_code).startswith('30'):
            with open(f"{downloadDir}/{filename}", 'wb') as f:
                f.write(data.content)
            return f"{downloadDir}/{filename}"
        else:
            logging.info(f"Download File Failed {data.status_code} {data.text}")
            return False
    except Exception as e:
        logging.error(f"Download Function Error {e}")
        return False


def sendMessage(message):
    logging.info(f"Send Message")
    data = {'chat_id': '-1001398844049', 'text': message}
    try:
        res = requests.post(
            url='https://api.telegram.org/bot1590534238:AAFYL23LSVWZdZi4H_Q_Fy7v1ivggD7UBs9/sendMessage', data=data)
        if res.status_code != 200:
            logging.error(res)
    except Exception as err:
        logging.error(err)


def upload(cover, video, saveUri, vnum):
    try:
        secret_id = 'AKIDc084lCWN1SeaFnp2NSFnWy81fm2EF4pK'
        secret_key = 'NAiAST3RovlMbZIl2yZu87pJ7i3C7wiF'
        region = 'ap-hongkong'
        domain = 'sourcefile-1304080031.cos.accelerate.myqcloud.com'
        client = CosS3Client(CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Domain=domain))
        cos_bucket = 'sourcefile-1304080031'
        coverType = re.split('\.', cover)[-1]
        upcover = uploadAction(client, cos_bucket, cover, f"{saveUri}/{vnum}/{vnum}.{coverType}")
        tsDir = re.split(re.split('/', video)[-1], video)[0]
        upvideo = uploadAction(client, cos_bucket, video, f"{saveUri}/{vnum}/{vnum}.m3u8")
        if upcover and upvideo:
            tslist = open(video, 'r')
            for ts in tslist.readlines():
                ts = ts.strip()
                if not ts.startswith('#'):
                    if not uploadAction(client, cos_bucket, f"{tsDir}/{ts}", f"{saveUri}/{vnum}/{ts}"):
                        logging.error(f"ts File Upload Failed {ts}")
                        tslist.close()
                        return False
                    os.remove(f"{tsDir}/{ts}")
            os.remove(cover)
            os.remove(video)
            tslist.close()
            return True
        else:
            logging.error(f"Video Upload Filed")
            return False
    except Exception as e:
        logging.error(f"upload Function Error {e}")


def uploadAction(client, bucket, sfile, dfile):
    try:
        logging.info(f"{sfile} -> {dfile} Uploading...")
        client.upload_file(
            Bucket=bucket,
            LocalFilePath=sfile,
            Key=dfile,
            PartSize=1,
            MAXThread=10,
            EnableMD5=False
        )
        return True
    except Exception as e:
        logging.error(f"Upload Error {e}")
        return False


def saveBase(data):
    try:
        # connection = pymysql.connect(host="hk-cdb-aumsfh1d.sql.tencentcdb.com", user="root", password="wvqhthpbd!Wv$da4", port=63734, db="db_yy")
        connection = pymysql.connect(host="101.32.202.66", user="root", password="1q2w3e4r..A", port=3306, db="db_yy_1", connect_timeout=10, write_timeout=10)
    except Exception as e:
        logging.info(f"Connect Mysql Failed {e}")
        return False
    else:
        try:
            title = data['title']
            cover_type = re.split('\.', data['cover'])[-1]
            cover_uri = "/" + data['file_save'] + "/" + data['fanhao'] + "/" + data['fanhao'] + "." + cover_type
            vod_url = "/" + data['file_save'] + "/" + data['fanhao'] + "/" + data['fanhao'] + ".m3u8"
            district = data['videotype']
            vnum = str(data['fanhao'])
            status = "1"
            videotype = "1"
            videocode = data['videocode']
            ctime = int(time.time())
            resolution = data['vodreso']
            duration = data['vodduration']
            name = data['name']
            ch_name = data['chinaname']
            with connection.cursor() as cursor:
                sql = f"insert into t_video_stock(`title`,`cover_uri`,`video_uri`,`district`,`vnum`,`video_type`,`video_code`,`description`,`resolution`,`duration`,`md5`,`name`,`ch_name`,`ctime`,`status`)" \
                      f" value('{title}','{cover_uri}','{vod_url}','{district}','{vnum}','{videotype}','{videocode}','','{resolution}','{duration}','','{name}','{ch_name}','{ctime}','{status}')"
                cursor.execute(sql)
                connection.commit()
        except Exception as e:
            logging.info(f"Video Save Base Failed {e}")
            connection.close()
            return False
        else:
            logging.info(f"Video Save Base Successfull")
            connection.close()
            return True


def delBucketFile(uri):
    try:
        logging.info(f"Remove Source File {uri}")
        secret_id = 'AKIDFH2Ypw3QSDhwwhufmhNn24uXv26vOvzp'
        secret_key = 'ocBbnmVyEExSlsiKfmxrU5RWNM8hz2oN'
        region = 'ap-hongkong'
        domain = 'srcfiles-1304147283.cos.accelerate.myqcloud.com'
        client = CosS3Client(CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Domain=domain))
        client.delete_object(
            Bucket='srcfiles-1304147283',
            Key=uri
        )
        return True
    except Exception as e:
        logging.error(f"delBucketFile Function Error {uri} {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        logging.error("Usage: VodSpliter <ConfigFile>")
        exit(-1)
    spark = SparkSession.builder.enableHiveSupport().appName("VodSpliter").getOrCreate()
    sc = spark.sparkContext
    appid = sc.applicationId
    logging.info(f"ApplicationId: {appid}")
    try:
        logging.info("Task Starting...")
        config = eval(sys.argv[1])
        needValue = ['vnum', 'saveas', 'title', 'videotype', 'videocode', 'voduri', 'coveruri', 'realname', 'chname']
        for v in needValue:
            if v not in config.keys():
                logging.error(f"Need Value {v}")
                exit(-1)

        vnum = config['vnum']
        saveas = config['saveas']
        title = config['title']
        videotype = config['videotype']  # Zone
        videocode = config['videocode']  # 1y 2n 3unknow
        vodpath = downloadFile(config['voduri'])
        coverpath = downloadFile(config['coveruri'])
        if vodpath and coverpath:
            vodrso = getVideoResolution(vodpath)
            vodtime = getVideoTime(vodpath)
            realname = config['realname']
            chname = config['chname']
            encres = encryptImage(coverpath, vnum)
            spres = splitVideo(vodpath, vnum)
            if spres and encres:
                logging.info(f"Split Success，Uploading...")
                upres = upload(encres, spres, saveas, vnum)
                if upres:
                    os.remove(vodpath)
                    os.remove(coverpath)
                    logging.info(f"Upload Successfull")
                    savedata = {"title": title,
                                "cover": encres,
                                "file_save": saveas,
                                "fanhao": vnum,
                                "videotype": videotype,
                                "videocode": videocode,
                                "ctime": int(time.time()),
                                "vodreso": vodrso,
                                "vodduration": vodtime,
                                "name": realname,
                                "chinaname": chname}
                    baseres = saveBase(savedata)
                    if baseres:
                        delBucketFile(config['voduri'])
                        delBucketFile(config['coveruri'])
                        logging.info(f"Save Base Successfull, Task Finish")
                        sendMessage(f"EMR Split Video Sucessfull {vnum}")
                        exit(0)
                    else:
                        logging.error(f"Save base Falied {savedata}")
                        sendMessage(f"EMR Save Base Failed {appid}")
            else:
                logging.error(f"Split and Encrypt Error {vodpath}")
                sendMessage(f"EMR Split Video Failed {appid}")
                exit(-1)
        else:
            logging.error(f"Video File Not Found {config['voduri']}")
            sendMessage(f"EMR Video File Not Found {appid}")
            exit(-1)
    except Exception as e:
        logging.error(f"Global Error {e}")
        sendMessage(f"EMR Global Error {appid}")
        exit(-1)
    finally:
        logging.info("Task Finish")
        spark.stop()
        exit(0)
