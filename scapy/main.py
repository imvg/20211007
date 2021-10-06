#!/usr/bin/env python
# -*- coding: utf-8 -*-
from requests import session
import logging


logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)

session = session()

header = {"X-Real-IP": "1.1.1.1", "HTTP_X_FORWARDED_FOR": "1.1.1.1"}

res = session.get("http://v2api.cs0147.com/apicheck", headers=header)
logging.info(res.text)
