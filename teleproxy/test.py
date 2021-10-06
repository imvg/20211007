import requests
import json


data = {
       "sessionId": "xxxxxxxx",
       "alarmStatus": "0",
       "alarmType":"metric",
       "alarmObjInfo": {
            "region": "gz",
            "namespace": "qce/cvm",
            "dimensions": {
                "unInstanceId": "ins-o9p3rg3m",
                "objId":"xxxxxxxxxxxx"
            }
       },
       "alarmPolicyInfo": {
                "policyId": "policy-n4exeh88",
                "policyType": "cvm_device",
                "policyName": "test",
                "policyTypeCName": "云服务器-基础监控",
                "conditions": {
                    "metricName": "cpu_usage",
                    "metricShowName": "CPU 利用率",
                    "calcType": ">",
                    "calcValue": "90",
                    "currentValue": "100",
                    "unit": "%",
                    "period": "60",
                    "periodNum": "1",
                    "alarmNotifyType": "continuousAlarm",
                    "alarmNotifyPeriod": 300
                }
        },
        "firstOccurTime": "2017-03-09 07:00:00",
        "durationTime": 500,
        "recoverTime": "0"
}

res = requests.post('http://telegram.zlyc.net/cdbwarn', data=json.dumps(data))
print(res)
