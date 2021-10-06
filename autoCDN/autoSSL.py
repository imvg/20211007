# -*- coding: utf-8 -*-
import logging
import re
import os

import simple_acme_dns

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


class letsEncrypt:
    def __init__(self):
        pass

    def setDomain(self, domainList: list):
        logging.info(f"初始化ACME对象... {domainList}")
        self.client = simple_acme_dns.ACMEClient(
            domains=domainList,
            email="vgwork001@gmail.com",
            directory="https://acme-v02.api.letsencrypt.org/directory",
            nameservers=["8.8.8.8", "1.1.1.1"],
            new_account=True,
            generate_csr=True
        )
        self.client.new_account()
        self.client.generate_private_key_and_csr(key_type='rsa2048')

    def getToken(self):
        try:
            tokenList = self.client.request_verification_tokens()
            prasList = []
            for Token in tokenList:
                prasList.append({"host": Token[0], "value": Token[1]})
            return prasList
        except Exception as e:
            logging.error(f"获取域名TXT Token异常 {e}")
            return False

    def authPars(self):
        try:
            logging.info(f"发起Letsencrypt所有权验证...")
            if self.client.check_dns_propagation(timeout=300):
                self.client.request_certificate()
                ssl = {"csr": self.client.certificate.decode(),
                       "key": self.client.private_key.decode()}
                for domainSSL in self.client.domains:
                    logging.info(ssl)
                    if len(re.split('\.', domainSSL)) == 2:
                        if not os.path.exists('certificate'):
                            os.mkdir('certificate')
                        with open(f'certificate/{domainSSL}.crt', 'w') as csr:
                           csr.write(ssl['csr'])
                        with open(f'certificate/{domainSSL}.key', 'w') as key:
                           key.write(ssl['key'])
                return ssl
            else:
                self.client.deactivate_account()
                logging.warning(f"无法验证该域名的TXT记录 {self.client.domains}")
                return False
        except Exception as e:
            logging.error(f"验证域名TXT异常 {e}")
            return False


