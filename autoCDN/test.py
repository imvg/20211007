#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from autoMain import AutoMain

domainList = [
    'winxinshop.com',
    'faxiaoit.com',
    'nanhaiqiming.com',
    'hhyjz.com',
    'dglbwl.com',
    'xfdzpld.com',
    'jntongchencnc.com',
]

ins = AutoMain('', '')
for domain in domainList:
    ssl = ins.getSSL(domain)
    print(ssl)
    # configString = "server\n" \
    #                "    {\n" \
    #                "        listen 80;\n" \
    #                "        listen 443;\n" \
    #                f"        server_name {domain} *.{domain};\n" \
    #                f"        ssl_certificate /usr/local/nginx/conf/ssl/{domain}.crt;\n" \
    #                f"        ssl_certificate_key /usr/local/nginx/conf/ssl/{domain}.key;\n" \
    #                "        index index.html index.htm;\n" \
    #                "        root  /home/wwwroot/dwpage;\n" \
    #                "        location ~ .*\.(gif|jpg|jpeg|png|js|css)$ {expires 1d;}\n" \
    #                "    }\n"
    # print(configString)
    # with open(f'domainConfig/{domain}.conf', 'w') as f:
    #     f.write(configString)