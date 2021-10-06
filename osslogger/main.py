# -*- coding: utf-8 -*-
from aliyun.log import LogClient, PutLogsRequest, LogItem, GetLogsRequest, IndexConfig
import time
import datetime
import re


def qzh7537():
    accessKeyId = "LTAI5tMehJDuCAnhM1ZaoQbx"
    accessKey = "tjgPDMNH1xffnzRFk1ANuULPvcZPm9"
    endpoint = "cn-guangzhou.log.aliyuncs.com"
    client = LogClient(endpoint, accessKeyId, accessKey)
    project_name = "oss-log-1214875359147985-cn-guangzhou"
    logstore_name = "oss-log-store"
    query = f"*| select time,client_ip,host,object,referer from {logstore_name} where bucket like 'lubeiinstall%' limit 999999"
    from_time = int(time.time()) - 86400
    to_time = time.time()
    request = GetLogsRequest(project_name, logstore_name, from_time, to_time, query=query)
    response = client.get_logs(request)
    if not response.get_logs():
        return False
    n = 1
    res = {}
    for log in response.get_logs():
        n += 1
        for k, v in log.contents.items():
            if k == "referer":
                if v not in res.keys():
                    res[v] = 1
                else:
                    res[v] += 1
    data = sorted(res.items(), key=lambda kv: (kv[1], kv[0]))
    for d in data:
        print(f"{d[1]}  {d[0]}")
    print(f"共获取到 {n} 条数据")
    return True


def miliaccount():
    accessKeyId = "LTAI5tKiSoiUJAcq3YogMVeo"
    accessKey = "6y0p8UivebogEokmmvbVtQSz115Yuc"
    endpoint = "cn-guangzhou.log.aliyuncs.com"
    client = LogClient(endpoint, accessKeyId, accessKey)
    project_name = "oss-log-1939026247751717-cn-guangzhou"
    logstore_name = "oss-log-store"
    query = f"*| select time,client_ip,host,object,referer from {logstore_name} where bucket like 'lbapk%' limit 999999"
    from_time = int(time.time()) - 3600
    to_time = time.time()
    request = GetLogsRequest(project_name, logstore_name, from_time, to_time, query=query)
    response = client.get_logs(request)
    if not response.get_logs():
        return False
    n = 1
    res = {}
    for log in response.get_logs():
        n += 1
        for k, v in log.contents.items():
            if k == "referer":
                if v not in res.keys():
                    res[v] = 1
                else:
                    res[v] += 1
    data = sorted(res.items(), key=lambda kv: (kv[1], kv[0]))
    for d in data:
        print(f"{d[1]}: {d[0]}")
    print(f"共获取到 {n} 条数据")
    return True


if __name__ == '__main__':
    # 通过SQL查询日志。
    # while True:
    #     if qzh7537():
    #         break
    #     time.sleep(1)
    qzh7537()
