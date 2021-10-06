#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging
import os

from gevent import monkey, pywsgi
monkey.patch_all()
from flask import *

app = Flask(__name__)


@app.route('/', methods=['POST','GET'])
def root():
    return "你干啥", 200


@app.route('/split', methods=['POST','GET'])
def send():
    if request.method == "GET":
        return "你干啥", 200
    try:
        needValue = ['vnum', 'saveas', 'title', 'videotype', 'videocode', 'voduri', 'coveruri', 'realname', 'chname']
        for config in json.loads(request.get_data())['videos']:
            for n in needValue:
                if n not in config.keys():
                    app.logger.info(f"Need Value {n}")
                    return '{"code":1,"msg":"Need Value %s","data":{}}' % n, 200
    except Exception as e:
        app.logger.error(e)
        return '{"code":1,"msg":"Value Check Failed","data":{}}', 200
    else:
        try:
            for config in json.loads(request.get_data())['videos']:
                app.logger.info(config)
                data = {"voduri":config['voduri'],
                        "coveruri":config['coveruri'],
                        "vnum":config['vnum'],
                        "saveas":config['saveas'],
                        "title":config['title'].encode("unicode_escape").decode(encoding="GBK"),
                        "videotype": config['videotype'].encode("unicode_escape").decode(encoding="GBK"),
                        "videocode": config['videocode'],
                        "realname":config['realname'].encode("unicode_escape").decode(encoding="GBK"),
                        "chname":config['chname'].encode("unicode_escape").decode(encoding="GBK")}

                command = f'/usr/local/service/spark/bin/spark-submit \
                --master yarn \
                --deploy-mode cluster \
                --driver-memory=2g \
                --executor-memory 2g \
                --executor-cores 1 \
                --num-executors 6 \
                --total-executor-cores 6 \
                --conf spark.yarn.submit.waitAppCompletion=false \
                --conf spark.yarn.maxAppAttempts=6 \
                /home/hadoop/vodspliter.py "{data}" >/dev/null 2>>/data/tasklog/task.log'
                os.popen(command)
            return '{"code":0,"msg":"","data":{}}', 200
        except Exception as e:
            app.logger.error(e)
            return '{"code":1,"msg":"%s","data":{}}' % e


if __name__ == '__main__':
    try:
        # from werkzeug.debug import DebuggedApplication
        # dapp = DebuggedApplication(app, evalex=True)
        app.debug = True
        server = pywsgi.WSGIServer(('0.0.0.0', 8899), app)
        server.serve_forever()
    except Exception as e:
        app.logger.error(e)
