# -*- coding: utf-8 -*-
import logging
import json
import re
import time
from alibabacloud_cdn20180510.client import Client as Cdn20180510Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_cdn20180510 import models as cdn_20180510_models

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


class AliCDN:
    def __init__(self):
        pass

    @staticmethod
    def create_client(access_key_id: str, access_key_secret: str):
        config = open_api_models.Config(
            # 您的AccessKey ID,
            access_key_id=access_key_id,
            # 您的AccessKey Secret,
            access_key_secret=access_key_secret
        )
        config.endpoint = 'cdn.aliyuncs.com'
        return Cdn20180510Client(config)

    @staticmethod
    def verification(domain: str, access_key, secret_key):
        client = AliCDN.create_client(access_key, secret_key)
        describe_verify_content_request = cdn_20180510_models.DescribeVerifyContentRequest(
            domain_name=domain
        )
        # 复制代码运行请自行打印 API 的返回值
        res = client.describe_verify_content(describe_verify_content_request)
        return res.body.content

    @staticmethod
    def checkVerification(
            access_key, secret_key,
            domain: str,
    ) -> None:
        client = AliCDN.create_client(access_key, secret_key)
        verify_domain_owner_request = cdn_20180510_models.VerifyDomainOwnerRequest(
            domain_name=domain,
            verify_type='dnsCheck'
        )
        # 复制代码运行请自行打印 API 的返回值
        while True:
            try:
                res = client.verify_domain_owner(verify_domain_owner_request)
            except Exception as e:
                logging.info(f"验证未通过, 2秒后重试 {e}")
                time.sleep(2)
                continue
            else:
                logging.info(f"域名 {domain} TXT验证成功")
                return res.body

    @staticmethod
    def checkExist(domain: str, access_key, secret_key):
        client = AliCDN.create_client(access_key, secret_key)
        domain = domain.replace("*", "")
        describe_cdn_domain_configs_request = cdn_20180510_models.DescribeCdnDomainConfigsRequest(
            domain_name=domain
        )
        # 复制代码运行请自行打印 API 的返回值
        try:
            client.describe_cdn_domain_configs(describe_cdn_domain_configs_request)
        except Exception as e:
            logging.info(f"该域名不存在，可以添加 {e}")
            return False
        else:
            logging.info(f"域名已存在于阿里CDN，跳过")
            return True

    @staticmethod
    def add(domain: str, access_key, secret_key, source1, source2):
        client = AliCDN.create_client(access_key, secret_key)
        domain = domain.replace("*", "")
        source = [
            {"content": source1, "type": "domain", "priority": "20", "port": 80, "weight": "15"},
            {"content": source2, "type": "domain", "priority": "20", "port": 80, "weight": "15"}
        ]
        batch_add_cdn_domain_request = cdn_20180510_models.BatchAddCdnDomainRequest(
            cdn_type='web',
            domain_name=domain,
            sources=str(source),
            scope='global'
        )
        # 复制代码运行请自行打印 API 的返回值
        res = client.batch_add_cdn_domain(batch_add_cdn_domain_request)
        logging.info(f"CDN域名添加成功 {res.body}")

    @staticmethod
    def setssl(
            access_key, secret_key,
            domain: str,
            csr: str,
            key: str
    ) -> None:
        domain = domain.replace("*", "")
        client = AliCDN.create_client(access_key, secret_key)
        set_domain_server_certificate_request = cdn_20180510_models.SetDomainServerCertificateRequest(
            domain_name=domain,
            server_certificate_status='on',
            server_certificate=csr,
            private_key=key
        )
        # 复制代码运行请自行打印 API 的返回值
        client.set_domain_server_certificate(set_domain_server_certificate_request)

    @staticmethod
    def optimization(
            access_key, secret_key,
            domain: str
    ) -> None:
        client = AliCDN.create_client(access_key, secret_key, )
        domain = domain.replace("*", "")
        configList = [
            {"functionName": "path_based_ttl_set", "functionArgs": [
                {"argName": "path", "argValue": "/"},
                {"argName": "ttl", "argValue": "3600"}
            ]},
            {"functionName": "gzip", "functionArgs": [
                {"argName": "enable", "argValue": "on"}
            ]},
            {"functionName": "https_tls_version", "functionArgs": [
                {"argName": "tls13", "argValue": "on"}
            ]},
            {"functionName": "tesla", "functionArgs": [
                {"argName": "enable", "argValue": "on"},
                {"argName": "trim_js", "argValue": "on"},
                {"argName": "trim_css", "argValue": "on"}
            ]}
        ]
        batch_set_cdn_domain_config_request = cdn_20180510_models.BatchSetCdnDomainConfigRequest(
            domain_names=domain,
            functions=str(configList)
        )
        # 复制代码运行请自行打印 API 的返回值
        res = client.batch_set_cdn_domain_config(batch_set_cdn_domain_config_request)
        logging.info(f"CDN域名配置完成 {domain} {res}")
