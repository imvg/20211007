# -*- coding: utf-8 -*-
import logging
import re
import requests
from boto3.session import Session
from botocore.exceptions import ClientError
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from multiprocessing import Pool
from threading import BoundedSemaphore
import os

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)

s3_id = "AKIA3NIGOUTKFVLQMCFB"
s3_key = "g2lvpP6H9Fm5D4jovk1OvQd8RVmGjkCJmCTwlk+L"
session = Session(s3_id, s3_key, region_name='ap-east-1')
s3_client = session.client('s3')
s3_bucket = "vodbackup"

cos_id = ''
cos_key = ''
region = 'ap-hongkong'
cos_domain = 'sourcefile-1304080031.cos.accelerate.myqcloud.com'
cos_client = CosS3Client(CosConfig(Region=region, SecretId=cos_id, SecretKey=cos_key))
cos_bucket = 'sourcefile-1304080031'


def controler(key):
    try:
        if not checkExist(key):
            dwres = downloadFile(key)
            if dwres:
                upres = uploadFile(dwres, key)
                if upres:
                    delFile(dwres)
                    logging.info(f"处理完成 {key}")
        return True
    except Exception as e:
        logging.error(e)
        return False


def downloadFile(key):
    try:
        filename = re.split('/', key)[-1]
        data = requests.get(f"http://{cos_domain}/{key}")
        with open(f'tmp/{filename}', 'wb') as f:
            f.write(data.content)
        return f'tmp/{filename}'
    except Exception as e:
        logging.error(f"文件下载异常 {e}")
        return False


def checkExist(key):
    try:
        s3_client.head_object(Bucket=s3_bucket, Key=key)
        return True
    except ClientError:
        return False
    except Exception as e:
        logging.error(f"ChekcExist Error {e}")
        return False


def uploadFile(file, key):
    try:
        if os.path.exists(file):
            s3_client.upload_file(Filename=file, Bucket=s3_bucket, Key=key, ExtraArgs={'ACL': 'public-read'})
            return True
        else:
            logging.debug(f"本地文件不存在, 无法上传")
            return False
    except Exception as e:
        logging.error(f"S3上传失败 {e}")
        return False


def delFile(file):
    if os.path.exists(file):
        os.remove(file)


class TaskManager(object):
    def __init__(self, process_num, queue_size):
        self.pool = Pool(processes=process_num, maxtasksperchild=2)
        self.workers = BoundedSemaphore(queue_size)

    def new_task(self, function, arguments):
        """Start a new task, blocks if queue is full."""
        self.workers.acquire()
        self.pool.apply_async(function, args=arguments, callback=self.task_done)

    def task_done(self, *args, **kwargs):
        """Called once task is done, releases the queue is blocked."""
        self.workers.release()

    def join(self):
        self.pool.close()
        self.pool.join()


if __name__ == '__main__':
    try:
        Marker = ""
        maxnum = 100

        if not os.path.exists('tmp'):
            os.mkdir('tmp')

        queue_size = 240
        p = TaskManager(process_num=8, queue_size=queue_size)
        while True:
            response = cos_client.list_objects(
                Bucket=cos_bucket,
                Marker=Marker,
                MaxKeys=maxnum,
                EncodingType='url'
            )
            for keys in response['Contents']:
                key = keys['Key']
                if not str(key).endswith('/'):
                    p.new_task(controler, (key,))
            if response['IsTruncated'] == 'false':
                break
            Marker = response['NextMarker']
        p.join()
    except Exception as e:
        logging.error(f"全局异常 {e}")
