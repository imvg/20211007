# -*- coding: utf-8 -*-
import OpenSSL
import autoDNS
import autoSSL
import autoCDN
import autoShell
import autoDB
import logging
import time
import re
import os
from datetime import datetime

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


class AutoMain:
    def __init__(self, access_key, secret_key):
        self.dns = autoDNS.DNSpod()
        self.ssl = autoSSL.letsEncrypt()
        self.shell = autoShell.AutoShell()
        self.db = autoDB.DataBase()
        self.access_key = access_key
        self.secret_key = secret_key
        self.dumpCname = {
            '撸呗视频': 'cname301.dpagesource.com',
            '91撸视频': '91cname301.dpagesource.com',
            '小黄鸭': 'xhy301.dpagesource.com',
        }

    def autoAdd(self, domainList: list, source1: str, source2: str, tips: str, merchant: str):
        try:
            ssl = self.getSSL(domainList)
            if ssl:
                for dm in domainList:
                    self.setCDN(domain=dm, ssl=ssl[dm], source1=source1, source2=source2, tips=tips)
                    logging.info(f"正在绑定域名{dm}到落地页服务器...")
                    self.shell.bindDwpage(ssl, dm, merchant)
            else:
                return False
            return True
        except Exception as e:
            logging.error(f"全局异常 {e}")
            return False

    def getSSL(self, domainList):
        try:
            haveList = {}
            for domain in domainList:
                if self.sslCheckExist(domain):
                    csr = open(f'certificate/{domain}.crt', 'r')
                    key = open(f'certificate/{domain}.key', 'r')
                    haveList[domain] = {'csr': csr.read(), 'key': key.read()}
                    csr.close()
                    key.close()
            if len(domainList) == len(haveList.keys()):
                return haveList
            else:
                getList = []
                for d in domainList:
                    if d not in haveList:
                        getList.append(d)
                        getList.append(f'*.{d}')
                self.ssl.setDomain(getList)
                logging.debug(f"正在申请Token验证...")
                token = self.ssl.getToken()
                logging.debug(f"获取到申请证书所需TXT: {token}")
                parsRes = True
                for pars in token:
                    logging.debug(f"开始自动解析TXT用于申请证书验证: {pars['host']} -> {pars['value']}")
                    parsDomain = ".".join(re.split("\.", pars['host'])[-2:])
                    parsHost = re.split("\.", pars['host'])[0]
                    if not self.dns.pars(parsDomain, parsHost, "TXT", pars['value']):
                        parsRes = False
                        break
                if parsRes:
                    logging.debug(f"DNS自动解析完成, 发起LetsEncrypt验证...")
                    ssl = self.ssl.authPars()
                    if ssl:
                        logging.info(f"验证成功, 证书到手:")
                        for domain in getList:
                            haveList[domain] = {'csr': ssl['csr'], 'key': ssl['key']}
                        return haveList
                    else:
                        return False
                else:
                    logging.warning(f"DNS解析失败")
                    return False
        except Exception as e:
            logging.error(f"获取证书异常 {e}")
            return False

    def sslCheckExist(self, domain: str):
        try:
            cert_file_path = f'certificate/{domain}.crt'
            key_file_path = f'certificate/{domain}.key'
            if os.path.exists(cert_file_path) and os.path.exists(key_file_path):
                with open(cert_file_path, 'rb') as cert:
                    certification = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert.read())
                    valid_start_time = certification.get_notBefore()  # 有效期起始时间
                    valid_end_time = certification.get_notAfter()  # 有效期结束时间
                    expireDate = datetime.strptime(valid_end_time.decode()[0:-1], '%Y%m%d%H%M%S') #证书过期日期
                    expire = time.strptime(valid_end_time.decode()[0:-1], '%Y%m%d%H%M%S')
                    expireTimeStemp = int(time.mktime(expire))
                    logging.info(f"检查到现有域名证书 {domain} 有效期截止到:{expireDate}")
                    if expireTimeStemp > (int(time.time())+259200):
                        return True
                    else:
                        return False
            else:
                return False
        except Exception as e:
            logging.error(f"sslCheckExist 证书检查异常 {e}")
            return False

    def getCertExpire(self, certfile):
        try:
            if not os.path.exists(certfile):
                logging.warning(f"证书文件不存在 {certfile}")
                return False
            with open(certfile, 'rb') as cert:
                certification = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert.read())
                valid_start_time = certification.get_notBefore()  # 有效期起始时间
                valid_end_time = certification.get_notAfter()  # 有效期结束时间
                expireDate = time.strptime(valid_end_time.decode()[0:-1], '%Y%m%d%H%M%S')  # 证书过期日期

                return time.strftime("%Y-%m-%d %H:%M:%S", expireDate)
        except Exception as e:
            logging.error(f"查询证书过期时间异常 {e}")

    def setCDN(self, domain: str, ssl: dict, source1: str, source2: str, tips: str):
        try:
            txtToken = autoCDN.AliCDN.verification(access_key=self.access_key, secret_key=self.secret_key,
                                                   domain=domain)
            if self.dns.pars(domain, "verification", "TXT", txtToken):
                autoCDN.AliCDN.checkVerification(access_key=self.access_key, secret_key=self.secret_key,
                                                 domain=domain)
                if not autoCDN.AliCDN.checkExist(access_key=self.access_key, secret_key=self.secret_key, domain=domain):
                    autoCDN.AliCDN.add(access_key=self.access_key, secret_key=self.secret_key, domain=domain, source1=source1, source2=source2)
                    autoCDN.AliCDN.add(access_key=self.access_key, secret_key=self.secret_key, domain=f"*.{domain}", source1=source1, source2=source2)
                    self.dns.pars(domain, "@", "CNAME", f"{domain}.w.cdngslb.com")
                    self.dns.pars(domain, "*", "CNAME", f"all.{domain}.w.cdngslb.com")
                    self.dns.setTips(domain, tips)
                autoCDN.AliCDN.setssl(access_key=self.access_key, secret_key=self.secret_key, domain=domain, csr=ssl['csr'], key=ssl['key'])
                autoCDN.AliCDN.setssl(access_key=self.access_key, secret_key=self.secret_key, domain=f"*.{domain}", csr=ssl['csr'], key=ssl['key'])
                autoCDN.AliCDN.optimization(access_key=self.access_key, secret_key=self.secret_key, domain=domain)
                autoCDN.AliCDN.optimization(access_key=self.access_key, secret_key=self.secret_key, domain=f"*.{domain}")
            return True

        except Exception as e:
            logging.error(e)
            return False

    def setDump(self, ssl, sdomain, ddomain, merchant):
        try:
            logging.info(f"开始配置301服务器Nginx...")
            if self.shell.setDump(ssl, sdomain, ddomain, merchant):
                self.dns.modify(sdomain, '@', 'CNAME', self.dumpCname[merchant])
                self.dns.modify(sdomain, '*', 'CNAME', self.dumpCname[merchant])
                return True
            else:
                return False
        except Exception as e:
            logging.error(f"域名设置跳转失败 {e}")
            return False

    def getDomainList(self):
        try:
            res = self.db.getDomainList()
            return res
        except Exception as e:
            logging.error(f"域名列表获取异常 {e}")
            return False


if __name__ == '__main__':
    domainlist = ['qhwjgh.com']
    access_key = 'LTAI5tPsrzyNWW4U7XYs5ufd'
    secret_key = 'rfkX7m8PeDOQhdgUZoiGdovGrWN6Z4'
    ins = AutoMain(access_key, secret_key)
    if ins.autoAdd(domainList=domainlist, source1='source7.dpagesource.com', source2='source8.dpagesource.com', tips='xhy落地页', merchant='xhy'):
        logging.info(f"配置成功")
    else:
        logging.error(f"配置失败")
