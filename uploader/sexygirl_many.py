# -*- coding: utf-8 -*-
import logging
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import pymysql
import os
import re
import random
import subprocess

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


class App:
    def __init__(self):
        pass

    def action(self):
        filedir = '/Users/mrvg/Desktop/yp2'
        try:
            for gid in os.listdir(filedir):
                if not gid.startswith('.'):
                    for media in os.listdir(f"{filedir}/{gid}"):
                        if str(media).endswith("jpg") or str(media).endswith("jpeg") or str(media).endswith("png"):
                            self.setlog(f"获取到 小姐ID: {gid}, 小姐文件类型是图片:{media}")
                            sfile = f"{filedir}/{gid}/{media}"
                            mtype = re.split('\.', media)[-1]
                            dfile = f'tmp/{gid}.{mtype}'
                            if self.enctyptImg(gid, sfile, dfile):
                                upres = self.uploadact(gid, dfile, 'image')
                                if upres:
                                    if self.savebase(gid, upres):
                                        self.setlog(f"照片上传成功.")
                                else:
                                    self.setlog(f"照片上传失败!")
                        elif str(media).endswith("mp4"):
                            self.setlog(f"获取到 小姐ID: {gid}, 小姐文件类型是视频:{media}")
                            sfile = f"{filedir}/{gid}/{media}"
                            if self.splitVod(gid, sfile):
                                upres = self.uploadact(gid, f'tmp/{gid}.m3u8', 'video')
                                if upres:
                                    if self.savebase(gid, upres):
                                        self.setlog(f"视频上传成功.")
                                else:
                                    self.setlog(f"视频上传失败!")
        except Exception as e:
            self.setlog(e)

    def enctyptImg(self, gid, sfile, dfile):
        try:
            self.setlog(f"{gid} 加密照片...")
            if not os.path.exists(sfile):
                self.setlog(f'{sfile} 文件不存在')
                return False
            if not os.path.isdir('tmp'):
                os.mkdir('tmp')
            data = open(sfile, 'rb')
            key = os.urandom(8)
            with open(dfile, 'wb') as enc:
                enc.write(key)
                enc.write(data.read())
            data.close()
            return True
        except Exception as e:
            self.setlog(e)
            return False

    def splitVod(self, gid, sfile):
        if os.path.exists("./ffmpeg"):
            self.setlog(f"{gid} 视频切片")
            command = f"./ffmpeg -y -i '{sfile}' -hls_time 6 -hls_list_size 0 -hls_segment_filename tmp/{gid}-%05d.ts -hls_key_info_file enc.keyinfo tmp/{gid}.m3u8"
            ret = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            while True:
                if ret.poll() is None:
                    # 切片详细日志
                    runlog = ret.stdout.readline()
                    continue
                else:
                    if ret.wait() != 0:
                        self.setlog('视频切片失败!')
                        spres = False
                        break
                    else:
                        break
            return True
        else:
            self.setlog("ffmpeg程序文件不存在")
            return False

    def uploadact(self, gid, sfile, mtype):
        try:
            rst = self.ranstr(8)
            if mtype == 'image':
                self.setlog(f"{gid} 上传照片...")
                filetype = re.split('\.', sfile)[-1]
                if self.uploadfile(sfile, f'/sexygirls/{gid}/image-{rst}.{filetype}'):
                    return f'/sexygirls/{gid}/image-{rst}.{filetype}'
            elif mtype == 'video':
                self.setlog(f"{gid} 上传视频...")
                m3u8 = open(sfile, 'r')
                for ts in m3u8.readlines():
                    if not ts.startswith('#'):
                        if not self.uploadfile(f'tmp/{ts.strip()}', f"/sexygirls/{gid}/video-{rst}/{ts.strip()}"):
                            return False
                m3u8.close()
                if self.uploadfile(sfile, f"/sexygirls/{gid}/video-{rst}/{gid}.m3u8"):
                    return f"/sexygirls/{gid}/video-{rst}/{gid}.m3u8"
            else:
                return False
        except Exception as e:
            self.setlog(e)
            return False

    def uploadfile(self, sfile, uri):
        try:
            secret_id = ''
            secret_key = ''
            region = 'ap-hongkong'
            client = CosS3Client(CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key))
            cos_bucket = 'sourcefile-1304080031'
            client.upload_file(
                Bucket=cos_bucket,
                LocalFilePath=sfile,
                Key=uri,
                PartSize=1,
                MAXThread=10,
                EnableMD5=False
            )
            os.remove(sfile)
            return True
        except Exception as e:
            self.setlog(e)
            return False

    def ranstr(self, num):
        H = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        salt = ''
        for i in range(num):
            salt += random.choice(H)
        return salt

    def savebase(self, gid, uri):
        try:
            connection = pymysql.connect(host="hk-cdb-aumsfh1d.sql.tencentcdb.com", user="root",
                                         password="wvqhthpbd!Wv$da4", port=63734, db="db_yy", connect_timeout=10,
                                         write_timeout=10)
            # connection = pymysql.connect(host="101.32.202.66", user="root", password="1q2w3e4r..A", port=3306,
            #                              db="db_yy_1", connect_timeout=10, write_timeout=10)
            with connection.cursor() as cur:
                sql = f"insert into t_sexy_girls_photo(`girls_id`, `url`, `order`) value({gid}, '{uri}', 0)"
                cur.execute(sql)
                connection.commit()
            connection.close()

            connection = pymysql.connect(host="hk-cdb-2y01dfu3.sql.tencentcdb.com", user="root",
                                         password="C7x9i0RhmqRPCk6swXQH", port=63569, db="db_yy", connect_timeout=10,
                                         write_timeout=10)
            # connection = pymysql.connect(host="101.32.202.66", user="root", password="1q2w3e4r..A", port=3306,
            #                              db="db_yy_1", connect_timeout=10, write_timeout=10)
            with connection.cursor() as cur:
                sql = f"insert into t_sexy_girls_photo(`girls_id`, `url`, `order`) value({gid}, '{uri}', 0)"
                cur.execute(sql)
                connection.commit()
            connection.close()

            connection = pymysql.connect(host="101.32.202.66", user="root", password="1q2w3e4r..A", port=3306,
                                         db="db_yy_1", connect_timeout=10, write_timeout=10)
            with connection.cursor() as cur:
                sql = f"insert into t_sexy_girls_photo(`girls_id`, `url`, `order`) value({gid}, '{uri}', 0)"
                cur.execute(sql)
                connection.commit()
            connection.close()

            return True
        except Exception as e:
            self.setlog(e)
            return False

    def setlog(self, logs):
        logging.info(logs)


if __name__ == '__main__':
    ins = App()
    ins.action()
