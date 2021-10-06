# -*- coding: utf-8 -*-
import logging
import os
import re
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)


def encrypt(sfile, dfile):
    try:
        data = open(sfile, 'rb').read()
        key = os.urandom(8)
        if os.path.exists(dfile):
            os.remove(dfile)
        with open(dfile, 'wb') as enc:
            enc.write(key)
            enc.write(data)
        logging.debug(f"{sfile} -> Encrypt -> {dfile}")
        return True
    except Exception as e:
        logging.error(e)

if __name__ == '__main__':
    filedir = ""
    for file in os.listdir(filedir):
        logging.debug(file)
