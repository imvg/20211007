# -*- coding: utf-8 -*-
import logging
import time
import json
from requests import session
from requests import exceptions
from requests.adapters import HTTPAdapter
import datetime

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)


class Reporter:
    def __init__(self, ):
        self.req = session()
        self.req.mount('http://', HTTPAdapter(max_retries=3))
        self.token = "1af86032f84bd87f325a9f4be783d7af"
        self.ttime = int(time.mktime(datetime.date.today().timetuple()))
        self.ftime = self.ttime - 86400
        self.header = {
            "Host": "kjgsbzhgs.com",
            "Connection": "keep-alive",
            "Content-Length": "230",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "http://kjgsbzhgs.com",
            "Referer": "http://kjgsbzhgs.com/admin.html",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cookie": f"token={self.token}; acw_tc=ac11000116297383026032374e49532a529e9ac125921ed1940c30468d66e9",
        }

    def keepAlive(self):
        try:
            while True:
                url = "http://kjgsbzhgs.com/user/pf_list_with_game"
                postdata = f"channel_id=" \
                           "&open_channel_id=" \
                           "&id=" \
                           "&game_user_id=" \
                           "&is_bind=" \
                           "&nickname=" \
                           "&is_online=" \
                           "&reg_ip=" \
                           "&is_recharge=" \
                           "&device_type=" \
                           "&mobile=" \
                           "&apns_code=" \
                           f"&begin_time={self.ftime}" \
                           f"&end_time={self.ttime}" \
                           "&page_size=20" \
                           "&page=1" \
                           f"&token={self.token}"
                req = self.sendRequests(url, postdata)
                if req:
                    logging.debug(f"KeepAliving... {req.text}")
                time.sleep(30)
        except Exception as e:
            logging.error(e)

    def sendRequests(self, url, postdata):
        try:
            data = self.req.post(url, data=postdata, headers=self.header, timeout=60)
            if data.status_code == 200:
                if "result" in json.loads(data.text).keys() or "data" in json.loads(data.text).keys():
                    if "url" == "http://kjgsbzhgs.com/user/get_user_game_data":
                        time.sleep(0.1)
                        return data
                    else:
                        return data
                elif json.loads(data.text)['msg'] == "timeout":
                    logging.warning(f"接口 {url} 返回 {json.loads(data.text)}, 等待30秒重试...")
                    time.sleep(30)
                    return self.sendRequests(url, postdata)
                else:
                    raise RuntimeError(f"接口 {url} 返回数据不存在result")
            elif data.status_code == 429:
                after = data.headers['Retry-After']
                logging.debug(f"请求频繁，等待 {after} 秒")
                time.sleep(int(after)+1)
                return self.sendRequests(url, postdata)
            elif data.status_code >= 500:
                logging.debug(f"接口返回状态码 {data.status_code}, 疑似Cloudflare拦截, 等待20秒重试")
                time.sleep(20)
                return self.sendRequests(url, postdata)
            else:
                logging.warning(f"状态码异常 {url} {data.status_code} {data.text}")
                raise RuntimeError(f"状态码异常 {url} {data.status_code} {data.text}")
        except exceptions.Timeout as e:
            logging.warning(f"接口 {url} {e}, 十秒后重试..")
            time.sleep(10)
            return self.sendRequests(url, postdata)
        except Exception as e:
            raise RuntimeError(e)


if __name__ == '__main__':
    ins = Reporter()
    ins.keepAlive()
