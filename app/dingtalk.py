import requests
import json


def send_dingtalk(msg):
    url = 'https://oapi.dingtalk.com/robot/send?access_token=35eed9c7faf86d0ad319edd76d860e894b32a69d9d69fe090e11132e179c09c9'
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "text",
        "text": {
            "content": "test: " + msg
        }, "at": {
            "isAtAll": False,
            "atMobiles": [18021541225]
        }
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)
    print(response.text)


if __name__ == '__main__':
    send_dingtalk("xxxxxxxxxxxx")
