# -*- coding: utf-8 -*-
import os

import requests, time
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import logging, re
from multiprocessing import Pool

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.WARNING)


secret_id = 'AKIDc084lCWN1SeaFnp2NSFnWy81fm2EF4pK'
secret_key = 'NAiAST3RovlMbZIl2yZu87pJ7i3C7wiF'
region = 'ap-hongkong'
client = CosS3Client(CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key))
cos_bucket = 'sourcefile-1304080031'

des_secret_id = 'AKIDFH2Ypw3QSDhwwhufmhNn24uXv26vOvzp'
des_secret_key = 'ocBbnmVyEExSlsiKfmxrU5RWNM8hz2oN'
des_region = 'ap-hongkong'
des_client = CosS3Client(CosConfig(Region=des_region, SecretId=des_secret_id, SecretKey=des_secret_key))
des_cos_bucket = 'srcfiles-1304147283'


def UploadFiles(url):
    try:
        if not url.endswith('/'):
            filename = re.split('/', url)[-1]
            if os.path.isfile(f'tmp/{filename}'):
                os.remove(f'tmp/{filename}')
            f = open(f'tmp/{filename}', 'wb')
            while True:
                try:
                    body = requests.get(url=f'https://sourcefile-1304080031.cos.ap-hongkong.myqcloud.com/{url}', timeout=50)
                    f.write(body.content)
                except Exception as e:
                    logging.warning(f'{e}, ReConnecting...')
                    time.sleep(3)
                    continue
                break
            f.close()
            des_client.upload_file(
                Bucket=des_cos_bucket,
                LocalFilePath=f'tmp/{filename}',
                Key=url,
                PartSize=1,
                MAXThread=10,
                EnableMD5=False
            )
            logging.warning(f'处理完成 {url}')
            os.remove(f'tmp/{filename}')
    except Exception as e:
        logging.error(f'处理异常 {url} {e}')


if __name__ == '__main__':
    if not os.path.isdir('tmp'):
        os.mkdir('tmp')
    marker = ""
    p = Pool(processes=4)
    while True:
        response = client.list_objects(
            Bucket=cos_bucket,
            Prefix='movie',
            Marker=marker
        )
        for file in response['Contents']:
            p.apply_async(UploadFiles, args=(file['Key'],))
        if response['IsTruncated'] == 'false':
            break
        marker = response['NextMarker']
    p.close()
    p.join()
