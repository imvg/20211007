# -*- coding: utf-8 -*-
from tkinter import Tk
from tkinter import Label
from tkinter import LabelFrame
from tkinter import StringVar
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import oss2
import pymysql
import threading


class App:
    def __init__(self):
        self.root = Tk()
        self.root.title("曲径通幽处")
        self.root.maxsize(500, 500)
        self.root.minsize(500, 500)
        self.settingZone()
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
        setfra = LabelFrame(self.root, text="设定", width=480, height=280, font="宋体")

        Label(setfra, text="IPA文件", font="宋体").place(x=10, y=50)
        self.imgen = ttk.Entry(setfra, width=32, state="disabled")
        self.imgen.place(x=65, y=49)
        self.selectbu = ttk.Button(setfra, text="选择", command=self.selectimg)
        self.selectbu.place(x=365, y=49)

        self.table = StringVar()
        self.kucun = ttk.Radiobutton(setfra, text="撸呗视频", variable=self.table, value="lubei")
        self.long = ttk.Radiobutton(setfra, text="91撸视频", variable=self.table, value="91lu")
        self.table.set("lubei")
        self.kucun.place(x=130, y=100)
        self.long.place(x=230, y=100)

        self.upload = ttk.Button(setfra, text="上传", command=self.queren)
        self.upload.place(x=190, y=150)

        setfra.place(x=10, y=10)

    def selectimg(self):
        self.coverPath = filedialog.askopenfilename(title=u'选择文件', filetypes=[("IPA文件", "*.ipa")])
        self.imgen.config(state='normal')
        self.imgen.delete(0, "end")
        self.imgen.insert(0, self.coverPath)
        self.imgen.config(state='disabled')

    def queren(self):
        askback = messagebox.askokcancel('温馨提示', '确认IPA文件和对应商户没没问题，继续执行？')
        if askback == True:
            self.click()

    def click(self):
        threading.Thread(target=self.action).start()

    def action(self):
        self.selectbu.config(state='disabled')
        self.kucun.config(state='disabled')
        self.long.config(state='disabled')
        self.upload.config(text='上传中..')
        self.upload.config(state='disabled')
        try:
            if self.table.get() == 'lubei':
                if self.uploadipa('LTAI5tKiSoiUJAcq3YogMVeo', '6y0p8UivebogEokmmvbVtQSz115Yuc', 'lbipa', self.imgen.get(), 'lubei.ipa'):
                    messagebox.showinfo('提示', '撸呗IPA文件更新成功')
            elif self.table.get() == '91lu':
                if self.uploadipa('LTAI5tDdKhFEdpVGTGUXsQep', 'BknC4YsgBALzxLwIC8Jy5sAZ91Fcx9', '91ipa', self.imgen.get(), '91lu.ipa'):
                    messagebox.showinfo('提示', '91撸IPA文件更新成功')
        except Exception as e:
            messagebox.showerror(e)
        finally:
            self.selectbu.config(state='normal')
            self.kucun.config(state='normal')
            self.long.config(state='normal')
            self.upload.config(state='normal')
            self.upload.config(text='上传')

    def uploadipa(self, key, secret, bucket, spath, dpath):
        try:
            # 阿里云账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM用户进行API访问或日常运维，请登录RAM控制台创建RAM用户。
            auth = oss2.Auth(key, secret)
            # yourEndpoint填写Bucket所在地域对应的Endpoint。以华东1（杭州）为例，Endpoint填写为https://oss-cn-hangzhou.aliyuncs.com。
            # 填写Bucket名称。
            bucket = oss2.Bucket(auth, 'https://oss-accelerate.aliyuncs.com', bucket)
            bucket.put_object_from_file(dpath, spath)
            return True
        except Exception as e:
            messagebox.showerror("错误", f"封面加密上传失败, 请截图给vg\n{e}")
            return False


if __name__ == '__main__':
    App()
