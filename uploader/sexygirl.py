# -*- coding: utf-8 -*-
import logging
from tkinter import Tk
from tkinter import END
from tkinter import Label
from tkinter import LabelFrame
from tkinter import StringVar
from tkinter import Radiobutton
from tkinter import filedialog
from tkinter import scrolledtext
from tkinter import ttk
from tkinter import messagebox
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import requests
import pymysql
import threading
import time
import os
import re
import random
import subprocess


class App:
    def __init__(self):
        self.root = Tk()
        self.root.title("曲径通幽处")
        self.root.maxsize(500, 500)
        self.root.minsize(500, 500)
        self.settingZone()
        self.logZone()
        self.root.protocol('WM_DELETE_WINDOW', self.close)
        self.root.mainloop()

    def close(self):
        ans = messagebox.askyesno("提示", "真的要关闭吗")
        if ans:
            self.root.destroy()

    def settingZone(self):
        setfra = LabelFrame(self.root, text="设定", width=480, height=280, font=("宋体"))
        Label(setfra, text="girlsId", font=("宋体")).place(x=10, y=10)
        self.giden = ttk.Entry(setfra, width=10, font=("宋体"))
        self.giden.place(x=65, y=9)

        Label(setfra, text="照片/视频", font=("宋体")).place(x=10, y=50)
        self.imgen = ttk.Entry(setfra, width=30, state="disabled")
        self.imgen.place(x=75, y=49)
        self.selectbu = ttk.Button(setfra, text="选择", command=self.selectmedia)
        self.selectbu.place(x=365, y=49)

        self.upload = ttk.Button(setfra, text="上传", command=self.click)
        self.upload.place(x=190, y=230)

        setfra.place(x=10, y=10)

    def logZone(self):
        logfra = LabelFrame(self.root, text="记录", width=480, height=180, font=("宋体"))
        self.log = scrolledtext.ScrolledText(logfra, width=55, height=8, font=("宋体"))
        self.log.insert(END, f'{time.strftime("%H:%M:%S", time.localtime())}: 准备就绪')
        self.log.config(state="disabled")
        self.log.place(x=10, y=5)
        logfra.place(x=10, y=300)

    def setlog(self, log):
        self.log.config(state="normal")
        self.log.insert(END, f'\n{time.strftime("%H:%M:%S", time.localtime())}: {log}')
        self.log.see(END)
        self.log.config(state="disabled")

    def selectmedia(self):
        self.coverPath = filedialog.askopenfilename(title=u'选择文件',
                                                    filetypes=[("图片文件", "*.jpg"), ("图片文件", "*.jpeg"), ("图片文件", "*.png"),
                                                               ("视频文件", "*.mp4")])
        self.imgen.config(state='normal')
        self.imgen.delete(0, "end")
        self.imgen.insert(0, self.coverPath)
        self.imgen.config(state='disabled')

    def lock(self, type):
        if type == "lock":
            self.giden.config(state="disabled")
            self.selectbu.config(state="disabled")
            self.upload.config(state="disabled")
        elif type == "unlock":
            self.giden.config(state="normal")
            self.selectbu.config(state="normal")
            self.upload.config(state="normal")

    def click(self):
        threading.Thread(target=self.action).start()

    def action(self):
        try:
            gid = self.giden.get()
            media = self.imgen.get()
            if str(media).endswith("jpg") or str(media).endswith("jpeg") or str(media).endswith("png"):
                mtype = re.split('/', media)[-1]
                dfile = f'tmp/{gid}.{mtype}'
                if self.enctyptImg(gid, media, dfile):
                    upres = self.uploadact(gid, dfile, 'image')
                    if upres:
                        if self.savebase(gid, upres):
                            self.setlog(f"照片上传成功.")
                    else:
                        self.setlog(f"照片上传失败!")
            elif str(media).endswith("mp4"):
                if self.splitVod(gid, media):
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
            command = f"./ffmpeg -y -i {sfile} -hls_time 6 -hls_list_size 0 -hls_segment_filename tmp/{gid}-%05d.ts -hls_key_info_file enc.keyinfo tmp/{gid}.m3u8"
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
            return True
        except Exception as e:
            self.setlog(e)
            return False


if __name__ == '__main__':
    App()
