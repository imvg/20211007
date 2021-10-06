# -*- coding: utf-8 -*-
import re
import os
import logging
import CloudFlare
from CloudFlare.exceptions import CloudFlareAPIError

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


def pars(data):
    try:
        cf = CloudFlare.CloudFlare(token='8eeybQaW6g1oviXe9tSiO-S4prvuFBBSRgCXp3pV')
        for domain in data:
            zone_name = domain["domain"]
            logging.info(f"获取域名ID {zone_name}")
            try:
                info = cf.zones.get(params={'name': zone_name})
            except CloudFlareAPIError as e:
                logging.error(f"Zones ID 获取异常 {e}")
            except Exception as e:
                logging.error(f"Zones ID 获取异常 {e}")
            else:
                zone_id = info[0]['id']
                # DNS records to create
                dns_records = domain["data"]
                for record in dns_records:
                    logging.info(f"解析 {zone_name} {record['name']} <-{record['type']}-> {record['content']}")
                    try:
                        # res = cf.zones.dns_records.get(zone_id, data=record)
                        # if len(res) > 0:
                        #     logging.info(f"{zone_name} {record['name']} 记录已存在, 跳过")
                        #     break
                        cf.zones.dns_records.post(zone_id, data=record)
                    except CloudFlareAPIError as e:
                        logging.error(f"域名 {zone_name} 解析 {record['name']} 异常 {e}")
    except Exception as e:
        logging.error(f"异常 {e}")


if __name__ == '__main__':
    data = [
        {"domain": "91lu2017.com", "data": [
            {"name": "@", "type": "CNAME", "content": "91cname301.dpagesource.com"},
            {"name": "*", "type": "CNAME", "content": "91cname301.dpagesource.com"},
        ]},
        {"domain": "91lu2018.com", "data": [
            {"name": "@", "type": "CNAME", "content": "91cname301.dpagesource.com"},
            {"name": "*", "type": "CNAME", "content": "91cname301.dpagesource.com"},
        ]},
        {"domain": "91lu2019.com", "data": [
            {"name": "@", "type": "CNAME", "content": "91cname301.dpagesource.com"},
            {"name": "*", "type": "CNAME", "content": "91cname301.dpagesource.com"}
        ]}
    ]
    pars(data)
