#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

from flask import *
from gevent import monkey, pywsgi
import pymysql

monkey.patch_all()

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def root():
    return "你干啥", 200


@app.route('/preview/123.m3u8', methods=['POST', 'GET'])
def preview():
    start = request.args.get('start')
    end = request.args.get('end')
    data = getData(123, int(start), int(end))
    print(f"起始时间 {start}")
    print(f"结束时间 {end}")
    return data, 200


def getData(vid, start, end):
    try:
        res = ""
        line = 0
        totalTime = 0
        startLine = 0
        console = False
        console2 = False
        console3 = False
        data = open('./data.m3u8', 'r')
        filedata = data.readlines()
        for ts in filedata:
            line += 1
            if '.ts' in ts:
                ts = "http://vod.huafengmaoyi.com/movie/cn/YZ/SUB-014/"+ts
            if console:
                res += ts
            if 'EXTINF' in ts:
                if not console3:
                    startLine = line
                    console3 = True
                longtime = float(re.split(':', ts)[-1].replace(',', ''))
                totalTime += longtime
                if totalTime >= start and not console2:
                    res += ts
                    console = True
                    console2 = True
                if totalTime >= end and console:
                    if '.ts' in filedata[line]:
                        filedata[line] = "http://vod.huafengmaoyi.com/movie/cn/YZ/SUB-014/" + filedata[line]
                    res += filedata[line]
                    console = False
        titleData = ""
        for title in filedata[:startLine-1]:
            titleData += title
        res = titleData + res
        res += filedata[-1]
        data.close()
        return res
    except Exception as e:
        return e


if __name__ == '__main__':
    # try:
    #     # from werkzeug.debug import DebuggedApplication
    #     # dapp = DebuggedApplication(app, evalex=True)
    #     app.debug = True
    #     server = pywsgi.WSGIServer(('0.0.0.0', 8899), app)
    #     server.serve_forever()
    # except Exception as e:
    #     app.logger.error(e)
    res = getData(1, 1, 30)
    print(res)
