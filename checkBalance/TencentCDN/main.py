#!/bin/python3
# -*- coding: utf-8 -*-
import logging
import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cdn.v20180606 import cdn_client, models


logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


try:
    cred = credential.Credential("AKIDud7LJ1SdXAcplPnvmNincARSCfrnTs0s", "dz4sReZDagV3KK5aolRqypQlob7MJ2Vh")
    httpProfile = HttpProfile()
    httpProfile.endpoint = "cdn.tencentcloudapi.com"

    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    client = cdn_client.CdnClient(cred, "", clientProfile)

    req = models.DescribeTrafficPackagesRequest()
    params = {

    }
    req.from_json_string(json.dumps(params))

    resp = client.DescribeTrafficPackages(req)
    packageData = resp.to_json_string()
    for package in json.loads(packageData)['TrafficPackages']:
        logging.info(package)

except TencentCloudSDKException as err:
    logging.error(err)