#!/usr/bin/python
# coding:utf-8
import requests
import re
import threading
import time
import json
import tkinter
from tkinter import ttk
import os
import sys
from bs4 import BeautifulSoup
def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):  # 判断是否得到绑定资源
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
LOGO_PATH = get_resource_path(os.path.join("resources", "test.ico"))  # LGO文件路径
IMAGE_PATH=get_resource_path(os.path.join("resources","hire.png"))
aut=''#定义口令
search='' #定义查询语句
File_name=''#定义保存文件名
thread_list = []
now_page = 1
flag = True
class Main_Class:  # 定义窗体类
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title('火箭-Zoomeye   --by culin')
        self.root.iconbitmap(LOGO_PATH)
        self.root.geometry("800x655")
        self.root.resizable(width=0,height=0)
        self.root['background']='LightSlateGray'
        self.admin_text = tkinter.Text(self.root, width=20, height=1, font=("微软雅黑", 10),relief="ridge")
        self.label_text = tkinter.Label(self.root, text="账户名: ", width=5, height=1,font=("微软雅黑", 10))
        self.label_text.grid(row=0,column=0)
        self.admin_text.grid(row=0, column=1)
        self.label_text2 = tkinter.Label(self.root, text="密码:  ", width=5, height=1,font=("微软雅黑", 10))
        self.label_text2.grid(row=1,column=0)
        self.pass_text = tkinter.Text(self.root, width=20, height=1, font=("微软雅黑", 10))
        self.pass_text.grid(row=1, column=1)
        self.label_text3 = tkinter.Label(self.root, text="查询页数: ", width=7, height=1, font=("微软雅黑", 10))
        self.label_text3.grid(row=0, column=2)
        #定义页数
        self.pageNum=ttk.Combobox(self.root,values=['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39','40'])
        self.pageNum.grid(row=0,column=3)
        self.label_text4 = tkinter.Label(self.root, text="线程数量: ", width=7, height=1, font=("微软雅黑", 10))
        self.label_text4.grid(row=1, column=2)
        self.threads_text=ttk.Combobox(self.root,values=['1','2','3','4','5','6','7','8','9','10'])
        self.threads_text.grid(row=1,column=3)
        self.label_text5 = tkinter.Label(self.root,text="文件名",width=7,height=1,font=("微软雅黑",10))
        self.label_text5.grid(row=0,column=4)
        self.file_text=tkinter.Text(self.root,width=20, height=1, font=("微软雅黑", 10))
        self.file_text.grid(row=0,column=5)
        self.label_text6 = tkinter.Label(self.root,text="搜索语句",width=7,height=1,font=("微软雅黑",10))
        self.label_text6.grid(row=1,column=4)
        self.EXEC_text=tkinter.Text(self.root,width=20,height=1,font=("微软雅黑",10))
        self.EXEC_text.grid(row=1,column=5)
        self.button=tkinter.Button(self.root,text="查询",width=10,font=("微软雅黑",16))
        self.button.bind("<Button-1>",self.Main_Search)
        self.button.place(x=663,y=0)
        self.Show_page()
        photo1=tkinter.PhotoImage(file=IMAGE_PATH)
        self.photo=tkinter.Label(self.root,image=photo1)
        self.photo.place(x=-230,y=277)
        self.root.mainloop()
    def Main_Search(self,username):
        self.get_access_token()
        self.MainForm()
        self.Change_page()
    def Show_page(self):
        self.treeview=tkinter.ttk.Treeview(self.root,column=("Ip","Port"))
        self.treeview.heading(column="Ip",text="IP")
        self.treeview.heading(column="Port",text="Port")
        self.treeview.column('Ip',width=300,anchor=tkinter.W)
        self.treeview.column('Port',width=300,anchor=tkinter.W)
        self.treeview.place(x=0,y=50)
    def Change_page(self):
        global File_name
        num=0
        with open(File_name,'r+') as file:
            for line in file.readlines():
                num+=1
                things=str(num)
                curLine = line.strip().split(":")
                ip=curLine[0]
                port=curLine[1]
                self.treeview.insert(parent="", index=tkinter.END, text=things,value=(ip,port))
    def MainForm(self):
        global max_page
        global File_name
        global thread_nums
        global search
        search = self.EXEC_text.get("0.0","end").strip()
        max_page = self.pageNum.get().strip()
        max_page = int(max_page)
        File_name = self.file_text.get("0.0","end").strip()
        thread_nums = self.threads_text.get()
        thread_nums=int(thread_nums.strip())
        print("***",thread_nums)
        thread_nums = int(thread_nums)
        print("thread_nums:",thread_nums," File_name:",File_name," max_page:",max_page," EXEC:",search)
        for i in range(thread_nums+1):
            thread = MyThreads(str(i))
            thread.start()
            thread_list.append(thread)
        for thread in thread_list:
            thread.join()
    def get_access_token(self):
        global aut
        username=self.admin_text.get("0.0","end").strip()
        print("username",username)
        password=self.pass_text.get("0.0","end").strip()
        url = "https://api.zoomeye.org/user/login"
        data = json.dumps({'username': username, 'password': password})
        access_key = requests.post(url=url, data=data)
        # 使用正则获取access_token具体的值
        access_token = re.findall(r': "(.*?)"}', access_key.text)
        aut = "JWT " + access_token[0]
def Spider_Search_Page(i):
    global aut
    global File_name
    global search
    headers = {
        "Authorization": aut
    }
    url = "https://api.zoomeye.org/host/search?query='" + search + "'&page=" + str(i) + "&facet=app,os"
    info = requests.get(url=url, headers=headers)
    r_decoded = json.loads(info.text)
    for line in r_decoded['matches']:
        with open(File_name, "a+") as f:
            f.write(line['ip'] + ':' + str(line['portinfo']['port']) + ':'+line['timestamp']+'\n')
class MyThreads(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
    def run(self):
        global max_page
        global now_page
        global flag
        while now_page <= max_page and flag == True:
            i = now_page
            now_page += 1
            try:
                Spider_Search_Page(i)
            except:
                flag = False
                return
        return
Main_Class()



