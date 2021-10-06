#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
from mitmproxy import ctx


def response(flow):
    url = "https://xxx/handle/execute.jhtml"
    if flow.request.url.startswith(url) :
        text = flow.response.text
        data = json.loads(text)
        print(data)

        result = data.get('result')
        print(result)
        ctx.log.info(str(result))
    else:
        print(flow.request.url)
        print("\n")
        print(flow.request.text)
        print("\n")
        print(flow.response.text)
