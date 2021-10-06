#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import *

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def root():
    return "你干啥", 200


@app.route('/test', methods=['POST', 'GET'])
def preview():
    return str(request.headers), 200


if __name__ == '__main__':
    try:
        # from werkzeug.debug import DebuggedApplication
        # dapp = DebuggedApplication(app, evalex=True)
        app.debug = True
        app.run('0.0.0.0', 8890)
    except Exception as e:
        app.logger.error(e)
