# -*- coding: utf-8 -*-
import requests
import json

url = "http://43.132.180.41:8899/split"
data = {'videos':[
    {"voduri":"/IMG_1588.mp4","coveruri":"/cover.jpg","vnum":"test","saveas":"test","title":"测试视频","videotype": "日韩", "videocode": "0", "realname":"神宫寺ナオ", "chname":"神宫寺奈绪"},
    ]}
res = requests.post(url, data=json.dumps(data))
print(res.content)

# data = "中文"
# command = f'/usr/local/service/spark/bin/spark-submit \
#                 /home/hadoop/vodspliter.py "{data.encode("unicode_escape").decode(encoding="GBK")}" >/dev/null 2>>/data/tasklog/task.log'
# print(command)
