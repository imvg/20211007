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


class App:
    def __init__(self):
        self.root = Tk()
        self.root.title("曲径通幽处")
        self.root.maxsize(500,500)
        self.root.minsize(500,500)
        self.settingZone()
        self.logZone()
        self.root.protocol('WM_DELETE_WINDOW', self.close)
        self.connection = pymysql.connect(host="hk-cdb-aumsfh1d.sql.tencentcdb.com", user="root",
                                     password="wvqhthpbd!Wv$da4", port=63734, db="db_yy", connect_timeout=10,
                                     write_timeout=10)
        self.root.mainloop()

    def close(self):
        ans = messagebox.askyesno("提示", "真的要关闭吗")
        if ans:
            self.root.destroy()

    def settingZone(self):
        setfra = LabelFrame(self.root, text="设定", width=480, height=280, font=("宋体"))
        Label(setfra, text="视频ID", font=("宋体")).place(x=10, y=10)
        self.viden = ttk.Entry(setfra, width=10, font=("宋体"))
        self.viden.place(x=65, y=9)

        Label(setfra, text="封面", font=("宋体")).place(x=10, y=50)
        self.imgen = ttk.Entry(setfra, width=32, state="disabled")
        self.imgen.place(x=65, y=49)
        self.selectbu = ttk.Button(setfra, text="选择", command=self.selectimg)
        self.selectbu.place(x=365, y=49)

        Label(setfra, text="标题", font=("宋体")).place(x=10, y=90)
        self.titleen = ttk.Entry(setfra, width=38)
        self.titleen.place(x=65, y=90)

        Label(setfra, text="供应商ID", font=("宋体")).place(x=10, y=130)
        self.proviceriden = ttk.Entry(setfra, width=10)
        self.proviceriden.insert(END, 1007)
        self.proviceriden.place(x=80, y=130)

        Label(setfra, text="分成比例", font=("宋体")).place(x=220, y=130)
        self.ratioen = ttk.Entry(setfra, width=10)
        self.ratioen.insert(END, 10)
        self.ratioen.place(x=300, y=130)

        self.table = StringVar()
        self.kucun = ttk.Radiobutton(setfra, text="库存列表", variable=self.table, value="t_video_stock")
        self.long = ttk.Radiobutton(setfra, text="长/短 视频列表", variable=self.table, value="t_video")
        self.table.set("t_video_stock")
        self.kucun.place(x=130, y=200)
        self.long.place(x=230, y=200)

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

    def selectimg(self):
        self.coverPath = filedialog.askopenfilename(title=u'选择文件', filetypes=[("图片文件", "*.jpg"), ("图片文件", "*.jpeg"), ("图片文件", "*.png"), ("图片文件", "*.webp")])
        self.imgen.config(state='normal')
        self.imgen.delete(0, "end")
        self.imgen.insert(0, self.coverPath)
        self.imgen.config(state='disabled')

    def lock(self, type):
        if type == "lock":
            self.viden.config(state="disabled")
            self.selectbu.config(state="disabled")
            self.titleen.config(state="disabled")
            self.proviceriden.config(state="disabled")
            self.ratioen.config(state="disabled")
            self.kucun.config(state="disabled")
            self.long.config(state="disabled")
            self.upload.config(state="disabled")
        elif type == "unlock":
            self.viden.config(state="normal")
            self.selectbu.config(state="normal")
            self.titleen.config(state="normal")
            self.proviceriden.config(state="normal")
            self.ratioen.config(state="normal")
            self.kucun.config(state="normal")
            self.long.config(state="normal")
            self.upload.config(state="normal")

    def click(self):
        threading.Thread(target=self.action).start()

    def action(self):
        if self.viden.get() and self.imgen.get() and self.proviceriden.get() and self.ratioen.get():
            self.lock("lock")
            try:
                self.connection.ping()
            except Exception as e:
                self.connection = pymysql.connect(host="hk-cdb-aumsfh1d.sql.tencentcdb.com", user="root",
                                             password="wvqhthpbd!Wv$da4", port=63734, db="db_yy", connect_timeout=10,
                                             write_timeout=10)
                self.action()
            else:
                try:
                    with self.connection.cursor() as cur:
                        sql = f"select cover_uri from {self.table.get()} where vid='{self.viden.get()}'"
                        cur.execute(sql)
                        nowImgPath = cur.fetchall()[0]
                        if len(nowImgPath) >= 1:
                            nowImgPath = nowImgPath[0]
                            imgType = re.split('\.', self.imgen.get())[-1]
                            dpath = re.split('\.', nowImgPath)[0] + '-alison.' + imgType
                            upres = self.enctyptUpload(self.viden.get(), self.imgen.get(), dpath, imgType)
                            if upres:
                                updatesql = f"update {self.table.get()} set cover_uri='{dpath}' where vid={self.viden.get()};"
                                self.setlog(f"{self.viden.get()} 封面入库...")
                                cur.execute(updatesql)
                                self.connection.commit()
                                self.commitSql(updatesql)
                            if self.titleen.get():
                                self.setlog(f"{self.viden.get()} 修改标题...")
                                changetitle = f"update {self.table.get()} set title='{self.titleen.get()}' where vid={self.viden.get()};"
                                cur.execute(changetitle)
                                self.connection.commit()
                                self.commitSql(changetitle)
                            if self.table.get() == 't_video':
                                # self.bindProvider(self.viden.get(), self.proviceriden.get(), self.ratioen.get())
                                self.setlog(f"请手动绑定供应商")
                            self.sendMessage(f"视频处理完成 {self.viden.get()} {self.titleen.get()}\nhttps://sourcefile-1304080031.cos.ap-hongkong.myqcloud.com{dpath}")
                        else:
                            self.setlog(f"表中未查找到该ID的视频")

                except Exception as e:
                    messagebox.showerror("", f"未知异常, 请截图给vg\n{e}")
            finally:
                self.lock("unlock")
                self.connection.close()
                self.setlog("处理完成")
        else:
            messagebox.showerror("错误", "信息不完整")

    def commitSql(self, sql):
        connjiuyi = pymysql.connect(host="hk-cdb-2y01dfu3.sql.tencentcdb.com", user="root",
                                    password="C7x9i0RhmqRPCk6swXQH", port=63569, db="db_yy", connect_timeout=10,
                                    write_timeout=10)
        self.setlog(f"更新91库...")
        with connjiuyi.cursor() as jy:
            jy.execute(sql)
            jy.fetchall()
            connjiuyi.commit()
        return True


    def enctyptUpload(self, vid, spath, dpath, imgtype):
        try:
            self.setlog(f"{vid} 加密封面...")
            if not os.path.exists(spath):
                self.setlog(f'{spath} 封面文件不存在')
                return False
            if not os.path.isdir('tmp'):
                os.mkdir('tmp')
            data = open(spath, 'rb')
            key = os.urandom(8)
            with open(f'tmp/{vid}.{imgtype}', 'wb') as enc:
                enc.write(key)
                enc.write(data.read())
            data.close()

            secret_id = 'AKIDc084lCWN1SeaFnp2NSFnWy81fm2EF4pK'
            secret_key = 'NAiAST3RovlMbZIl2yZu87pJ7i3C7wiF'
            region = 'ap-hongkong'
            client = CosS3Client(CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key))
            cos_bucket = 'sourcefile-1304080031'
            self.setlog(f"{vid} 上传封面...")
            client.upload_file(
                Bucket=cos_bucket,
                LocalFilePath=f'tmp/{vid}.{imgtype}',
                Key=dpath,
                PartSize=1,
                MAXThread=10,
                EnableMD5=False
            )
            os.remove(f'tmp/{vid}.{imgtype}')
            return True
        except Exception as e:
            messagebox.showerror("错误", f"封面加密上传失败, 请截图给vg\n{e}")
            return False

    def bindProvider(self, vid, providerid, ratio):
        self.setlog(f"{vid} 更新供应商信息...")
        try:
            self.connection.ping()
        except:
            self.connection = pymysql.connect(host="hk-cdb-aumsfh1d.sql.tencentcdb.com", user="root",
                                         password="wvqhthpbd!Wv$da4", port=63734, db="db_yy", connect_timeout=10,
                                         write_timeout=10)
            self.bindProvider(vid, providerid, ratio)
        else:
            bindsql = f"update t_video set provider_id = {providerid},provider_ratio={ratio} where  vid = {vid};"
            flashsql = f"update t_provider set video_nums = (select count(*) as num from t_video where provider_id = {providerid} and status>-2) where provider_id = {providerid};"
            deloldsql = f"delete from t_provider_video_deduct where vid = {vid};"
            try:
                with self.connection.cursor() as cur:
                    cur.execute(bindsql)
                    self.connection.commit()
                    cur.execute(flashsql)
                    self.connection.commit()
                    cur.execute(deloldsql)
                    self.connection.commit()
                    return True
            except Exception as e:
                messagebox.showerror(f"绑定供应商失败\n{e}")
                return False
                
    def sendMessage(self, Message):
        self.setlog("发送通知...")
        BotToken = "1590534238:AAFYL23LSVWZdZi4H_Q_Fy7v1ivggD7UBs8"
        ChannelId = "-1001534403340"
        try:
            data = {'chat_id': str(ChannelId).replace('\'', ''), 'text': Message}
            requests.post(url=f'https://api.telegram.org/bot{BotToken}/sendMessage', data=data)
            return True
        except Exception as e:
            messagebox.showerror(f"发送通知失败\n{e}")


if __name__ == '__main__':
    App()
