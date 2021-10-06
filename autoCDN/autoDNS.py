# -*- coding: utf-8 -*-
import logging
import json
import requests
from requests.adapters import HTTPAdapter

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


class DNSpod:
    def __init__(self):
        self.header = {"User-Agent": "Mr Vegit Client/1.0.0(vgwork001@gmail.com)"}
        self.login_token = "254705,9f5d5a2a5b2fb481799eb9f8065f6dfd"
        self.session = requests.session()
        self.session.mount('https://', HTTPAdapter(max_retries=3))

    def getDomainID(self, domain):
        try:
            postdata = {"login_token": self.login_token, "domain": domain, "format": "json"}
            url = "https://dnsapi.cn/Domain.Info"
            req = self.session.post(url, headers=self.header, data=postdata)
            if req.status_code == 200 and json.loads(req.text)['status']['code'] == "1":
                return json.loads(req.text)['domain']['id']
        except Exception as e:
            logging.error(f"DNSpod获取域名ID异常 {e}")

    def getRecordId(self, domain, ptype, sub):
        try:
            postdata = {"login_token": self.login_token, "domain": domain, "format": "json"}
            url = "https://dnsapi.cn/Record.List"
            req = self.session.post(url, headers=self.header, data=postdata)
            res = []
            if req.status_code == 200 and json.loads(req.text)['status']['code'] == "1":
                for record in json.loads(req.text)['records']:
                    if record['type'] == ptype and record['name'] == sub:
                        res.append(record['id'])
            return res
        except Exception as e:
            logging.error(f"DNSpod获取域名ID异常 {e}")

    def pars(self, domain, host, ptype, value):
        try:
            domainID = self.getDomainID(domain)
            if not domainID:
                logging.warning(f"域名不存在 {domain}")
                return False
            else:
                if not self.checkExist(domain, host, ptype, value):
                    postdata = {"login_token": self.login_token,
                                "domain_id": domainID,
                                "format": "json",
                                "sub_domain": host,
                                "record_type": ptype,
                                "record_line": "默认",
                                "value": value}
                    url = "https://dnsapi.cn/Record.Create"
                    req = self.session.post(url, headers=self.header, data=postdata)
                    if req.status_code == 200 and json.loads(req.text)['status']['code'] == "1":
                        logging.info(f"域名{ptype}解析操作完成, DNSpod返回: {json.loads(req.text)}")
                        return True
                    else:
                        logging.warning(f"域名{ptype}解析失败, DNSpod返回: {json.loads(req.text)}")
                        return False
                else:
                    logging.info(f"此域名指定记录已存在, 跳过 {host}.{domain} --> {value}")
                    return True
        except Exception as e:
            logging.error(f"DNSpod解析异常 {e}")
            return False

    def checkExist(self, domain, host, ptype, value):
        try:
            postdata = {"login_token": self.login_token,
                        "domain": domain,
                        "format": "json",
                        "sub_domain": host,
                        "record_type": ptype,
                        "length": 10}
            url = "https://dnsapi.cn/Record.List"
            req = self.session.post(url, headers=self.header, data=postdata)
            if req.status_code == 200 and json.loads(req.text)['status']['code'] == "1":
                have = False
                for record in json.loads(req.text)['records']:
                    if value == record['value']:
                        have = True
                return have
        except Exception as e:
            logging.error(f"DNS检查重复异常 {e}")
            return False

    def checkHostExist(self, domain, host, ptype):
        try:
            postdata = {"login_token": self.login_token,
                        "domain": domain,
                        "format": "json",
                        "sub_domain": host,
                        "record_type": ptype,
                        "length": 10}
            url = "https://dnsapi.cn/Record.List"
            req = self.session.post(url, headers=self.header, data=postdata)
            if req.status_code == 200 and json.loads(req.text)['status']['code'] == "1":
                have = False
                for record in json.loads(req.text)['records']:
                    if ptype == record['type']:
                        have = True
                return have
        except Exception as e:
            logging.error(f"DNS检查重复异常 {e}")
            return False

    def setTips(self, domain, tips):
        try:
            postdata = {"login_token": self.login_token,
                        "domain": domain,
                        "format": "json",
                        "remark": tips}
            url = "https://dnsapi.cn/Domain.Remark"
            req = self.session.post(url, headers=self.header, data=postdata)
            if req.status_code == 200 and json.loads(req.text)['status']['code'] == "1":
                return True
            else:
                logging.warning(f"域名备注设置失败 {req.text}")
                return False
        except Exception as e:
            logging.error(f"DNS备注设置异常 {e}")
            return False

    def modify(self, domain, host, ptype, value):
        try:
            if not self.checkHostExist(domain, host, ptype):
                return self.pars(domain, host, ptype, value)
            else:
                recordID = self.getRecordId(domain, ptype, host)
                url = "https://dnsapi.cn/Record.Modify"
                for recid in recordID:
                    postdata = {"login_token": self.login_token,
                                "domain": domain,
                                "record_id": recid,
                                "format": "json",
                                "sub_domain": host,
                                "record_type": ptype,
                                "record_line": "默认",
                                "value": value}
                    req = self.session.post(url, headers=self.header, data=postdata)
                    if req.status_code == 200 and json.loads(req.text)['status']['code'] == "1":
                        logging.info(f"域名{ptype}解析修改完成, DNSpod返回: {json.loads(req.text)}")
                        return True
                    else:
                        logging.warning(f"域名{ptype}解析修改失败, DNSpod返回: {json.loads(req.text)}")
                        return False
        except Exception as e:
            logging.error(f"DNSpod解析异常 {e}")
            return False


if __name__ == '__main__':
    ins = DNSpod()
    ins.modify('mbbshe.com', '@', 'CNAME', 'baidu.com')

