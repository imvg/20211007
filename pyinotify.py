# -*- coding: utf-8 -*-
import pyinotify
import logging
import sys
import os

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)

class ProcessTransientFile(pyinotify.ProcessEvent):
    def process_IN_MODIFY(self, event):
        line = file.readline()
        if line:
            logging.info(f"New log: {line}")


if __name__ == '__main__':
    try:
        log_file = sys.argv[1]
        if not os.path.isfile(log_file):
            logging.error(f"{log_file} File Not Found!")
            exit(1)
        file = open(log_file, 'r')
        res = os.stat(log_file)
        size = res[6]
        file.seek(size)

        ins = pyinotify.WatchManager()
        notifier = pyinotify.Notifier(ins)
        ins.watch_transient_file(log_file, pyinotify.IN_MODIFY, ProcessTransientFile)
        notifier.loop()
    except Exception as e:
        logging.error(e)
        logging.error('全局异常')

