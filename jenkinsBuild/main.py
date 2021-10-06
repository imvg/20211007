# !/usr/bin/python3
# -*- coding: utf-8 -*-
import jenkins
import logging

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)


jenkins_server_url = 'http://localhost:8080/jenkins/'
user_id = 'admin'
api_token = '11f0d5a1cd320736f3d764a66cc180b0e2'
server = jenkins.Jenkins(jenkins_server_url, username=user_id, password=api_token)
logging.info(server)
name = 'vod-test'
parameters = {'channelCode': '331dacq1'}
server.build_job(name, parameters)
