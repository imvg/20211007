# -*- coding: utf-8 -*-
from tkinter import Tk
from tkinter import END
from tkinter import Label
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import threading
import os
import re


class App:
    def __init__(self):
        self.root = Tk()
        self.root.title("图片加密")
        self.root.maxsize(300, 200)
        self.root.minsize(300, 200)
        self.body()
        self.filecount = 0
        self.root.mainloop()

    def body(self):
        Label(self.root, text="选择图片").place(x=10, y=15)
        self.files = ttk.Entry(self.root, width=20, state='disabled')
        self.files.place(x=10, y=60)
        self.select = ttk.Button(self.root, text="选择", width=3, command=self.getFiles)
        self.select.place(x=210,y=60)
        self.click = ttk.Button(self.root, text="加密", command=self.process)
        self.click.place(x=110, y=120)

    def getFiles(self):
        self.filePath = filedialog.askopenfilenames(title=u'选择文件', filetypes=[("视频文件", "*.jpg"),
                                                                              ("视频文件", "*.jpeg"),
                                                                              ("视频文件", "*.png"),
                                                                              ("视频文件", "*.webp"),
                                                                              ("视频文件", "*.js"),
                                                                              ("视频文件", "*.gif")])
        self.files.config(state='normal')
        self.files.delete(0, END)
        self.files.insert(0, f'已选择 {len(self.filePath)} 个文件')
        self.files.config(state='disabled')
        self.filecount = len(self.filePath)

    def process(self):
        threading.Thread(target=self.encrypt).start()

    def encrypt(self):
        try:
            if self.filecount >= 1:
                self.select.config(state='disabled')
                self.click.config(state='disabled')
                try:
                    if not os.path.exists('tmp'):
                        os.mkdir('tmp')
                    for file in self.filePath:
                        if not os.path.exists(file):
                            messagebox.showerror("错误", f"{file}\n该文件不存在")
                            return False
                        data = open(file, 'rb').read()
                        key = os.urandom(8)
                        filename = re.split('/', file)[-1]
                        dfile = f'tmp/{filename}'
                        if os.path.exists(dfile):
                            os.remove(dfile)
                        with open(dfile, 'wb') as enc:
                            enc.write(key)
                            enc.write(data)
                    messagebox.showinfo("提示", "图片加密完成")
                except Exception as e:
                    messagebox.showerror("错误", f"处理异常\n{e}")
                finally:
                    self.select.config(state='normal')
                    self.click.config(state='normal')
            else:
                messagebox.showinfo("提示", "未选择任何图片")
        except Exception as e:
            messagebox.showerror("异常", e)


if __name__ == '__main__':
    App()
