#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import json
from flask import *
from flask_cors import CORS
from ApiMethod import Methods

app = Flask(__name__)
CORS(app)

methodsIns = Methods()


@app.route('/', methods=['POST', 'GET'])
def root():
    return "你干啥", 200


@app.route('/makeCDN', methods=['POST', 'OPTIONS'])
def makeCDN():
    if request.method == 'OPTIONS':
        return '',200
    res = methodsIns.makeAction(request.get_data().decode())
    return json.dumps(res), 200


@app.route('/getSSL', methods=['POST'])
def getssl():
    res = methodsIns.getSSL(request.get_data().decode())
    return json.dumps(res), 200


@app.route('/getDomainList', methods=['POST'])
def getdomains():
    res = methodsIns.getDomainList()
    return json.dumps(res), 200


@app.route('/setDump', methods=['POST'])
def setdump():
    res = methodsIns.makeDump(request.get_data().decode())
    return json.dumps(res), 200


if __name__ == '__main__':
    try:
        app.debug = False
        app.run('0.0.0.0', 9980)
    except Exception as e:
        app.logger.error(e)
