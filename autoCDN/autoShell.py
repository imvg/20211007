# -*- coding: utf-8 -*-
import logging
import re
import os
import subprocess


logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)


class AutoShell:
    def __init__(self):
        self.dumphost = {"撸呗视频": "47.75.122.229", "花瓣直播": "47.75.122.229", "91撸视频": "47.75.97.129"}
        self.dwpageHostList = {
            'lubei': ["8.212.25.228", "8.212.31.196", "47.57.228.71", "8.212.30.153"],
            'huaban': ["47.75.117.112", "47.75.120.131"],
            '91lu': ["47.75.97.13", "47.75.110.112"],
            'xhy': ["47.75.125.80", "47.75.106.17"]
        }
        self.configDir = "/usr/local/nginx/conf/vhost/autoConfig"
        self.sslDir = "/usr/local/nginx/conf/ssl"
        if not os.path.exists('tmp'):
            os.mkdir('tmp')
        pass

    def runShell(self, command):
        runlog = []
        runStatus = 0
        logging.info(f"执行命令: {command}")
        runRes = subprocess.Popen(command,
                                  shell=True,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  encoding='utf-8',
                                  env={'LANG': 'zh_CN.UTF-8'})
        while True:
            if runRes.poll() is None:
                # 详细日志
                logs = runRes.stdout.readline()
                logging.debug(f"命令执行输出: {logs.strip()}")
                if logs.strip() != '':
                    runlog.append(logs.strip())
                continue
            else:
                runStatus = runRes.wait()
                if runRes.wait() != 0:
                    logging.error(f"命令执行失败 {command}")
                break
        resData = {'status': runStatus, 'runlog': runlog}
        return resData

    def setDump(self, ssl, src, dst, merchant):
        logging.info(f"检测域名配置是否存在...")
        if not self.checkExist(self.dumphost[merchant], src):
            logging.info(f"发送域名证书...")
            if self.setCertificate(self.dumphost[merchant], src, ssl):
                if '/' in dst:
                    dst = re.split('/', dst)[2]
                domainFormat = re.split('\.', src)
                configString = "server\n" \
                               "    {\n" \
                               "        listen 80;\n" \
                               "        listen 443 ssl;\n" \
                               f"        server_name {src};\n" \
                               "        default_type text/html;\n" \
                               f"        ssl_certificate /usr/local/nginx/conf/ssl/{src}.crt;\n" \
                               f"        ssl_certificate_key /usr/local/nginx/conf/ssl/{src}.key;\n" \
                               "        proxy_set_header X-Real-IP $proxy_protocol_addr;\n" \
                               "        proxy_set_header X-Forwarded-For $proxy_protocol_addr;\n" \
                               f"        return 301 https://{dst}$request_uri;\n" \
                               "    }\n" \
                               "server\n" \
                               "    {\n" \
                               "        listen 80;\n" \
                               "        listen 443 ssl;\n" \
                               f"        server_name ~^(?<subdomain>.+)\.{domainFormat[0]}\.{domainFormat[1]};\n" \
                               "        default_type text/html;\n" \
                               f"        ssl_certificate /usr/local/nginx/conf/ssl/{src}.crt;\n" \
                               f"        ssl_certificate_key /usr/local/nginx/conf/ssl/{src}.key;\n" \
                               "        proxy_set_header X-Real-IP $proxy_protocol_addr;\n" \
                               "        proxy_set_header X-Forwarded-For $proxy_protocol_addr;\n" \
                               f"        return 301 https://$subdomain.{dst}$request_uri;\n" \
                               "    }\n"
                logging.info(f"发送配置文件...")
                if self.sendFile(f"{src}.conf", configString, self.dumphost[merchant], self.configDir):
                    logging.info(f"检测Nginx配置...")
                    checkCommand = f"ssh root@{self.dumphost[merchant]} 'nginx -t'"
                    checkRes = self.runShell(checkCommand)
                    if checkRes['status'] == 0 and len(checkRes['runlog']) == 2:
                        logging.debug(f"Nginx配置文件检查成功")
                        logging.info(f"重载Nginx配置")
                        reloadCommand = f"ssh root@{self.dumphost[merchant]} 'nginx -s reload'"
                        reloadRes = self.runShell(reloadCommand)
                        if reloadRes['status'] == 0 and len(reloadRes['runlog']) == 0:
                            logging.debug(f"Nginx配置重载成功")
                            logging.info(f"配置完成")
                            return True
        return False

    def bindDwpage(self, ssl, domain, merchant):
        dwpageServers = self.dwpageHostList[merchant]
        configString = "server\n" \
                       "    {\n" \
                       "        listen 80;\n" \
                       "        listen 443;\n" \
                       f"        server_name {domain} *.{domain};\n" \
                       f"        ssl_certificate /usr/local/nginx/conf/ssl/{domain}.crt;\n" \
                       f"        ssl_certificate_key /usr/local/nginx/conf/ssl/{domain}.key;\n" \
                       "        index index.html index.htm;\n" \
                       "        root  /home/wwwroot/dwpage;\n" \
                       "        location ~ .*\.(gif|jpg|jpeg|png|js|css)$ {expires 1d;}\n" \
                       "    }\n"
        for host in dwpageServers:
            if not self.checkExist(host, domain):
                if self.setCertificate(host, domain, ssl[domain]):
                    if self.sendFile(f"{domain}.conf", configString, host, self.configDir):
                        checkCommand = f"ssh root@{host} 'nginx -t'"
                        checkRes = self.runShell(checkCommand)
                        if checkRes['status'] == 0 and len(checkRes['runlog']) == 2:
                            logging.info(f"Nginx配置文件检查成功")
                            reloadCommand = f"ssh root@{host} 'nginx -s reload'"
                            reloadRes = self.runShell(reloadCommand)
                            if reloadRes['status'] == 0 and len(reloadRes['runlog']) == 0:
                                logging.info(f"Nginx配置重载成功")

    def checkExist(self, host, domain):
        domainFormat = re.split('\.', domain)
        check1 = f"ssh root@{host} " + f"\"find /usr/local/nginx/conf/vhost -name *.conf | xargs grep {domain} | " + "awk '{print $1}'\""
        check2 = f"ssh root@{host} " + f"\"find /usr/local/nginx/conf/vhost -name *.conf | xargs grep subdomain.{domainFormat[0]}.{domainFormat[1]} | " + "awk '{print $1}'\""
        res1 = self.runShell(check1)
        res2 = self.runShell(check2)
        if len(res1['runlog']) >= 1 or len(res2['runlog']) >= 1:
            logging.info(f"域名的Nginx配置已存在 {host} {domain}")
            return True
        else:
            logging.debug(f"域名未再Nginx配置 {host} {domain}")
            return False

    def setCertificate(self, host, domain, ssl):
        csr = ssl['csr']
        key = ssl['key']
        sendCsrRes = self.sendFile(f"{domain}.crt", csr, host, self.sslDir)
        sendKeyRes = self.sendFile(f"{domain}.key", key, host, self.sslDir)
        if sendCsrRes and sendKeyRes:
            logging.info(f"Nginx 证书发送成功")
            return True
        else:
            logging.warning(f"Nginx 证书发送失败")
            return False

    def sendFile(self, filename, filedata, host, despath):
        with open(f'tmp/{filename}', 'w') as f:
            f.write(filedata)
        sendCommand = f"scp tmp/{filename} root@{host}:{despath}"
        sendRes = self.runShell(sendCommand)
        os.remove(f'tmp/{filename}')
        if sendRes['status'] == 0:
            logging.debug(f"文件传输成功 {filename} -> {host}")
            return True
        else:
            for log in sendRes['runlog']:
                logging.warning(f"文件传输失败 {log}")
            return False

