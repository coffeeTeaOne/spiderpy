# encoding: utf-8
from urllib import request
import ssl
import requests
import urllib.parse
import base64
import json
import jsonpath


def __get_token():
    url = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials' \
          '&client_id=b8SkhpH0iaTqVDYDGWIyGF5g&client_secret=CkKsDoIHAZH64a2x2zI0HW4TYLkv0RnG'
    header = {'Content-Type': 'application/json; charset=UTF-8'}
    content = requests.get(url=url, headers=header)
    content = content.text
    if (content):
        content = json.loads(content)
        return content['access_token']


def ocr(dir, name):
    url = 'https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic'
    with open("%s%s" % (dir, name), "rb") as f:
        # b64encode是编码，b64decode是解码
        base64_data = base64.b64encode(f.read())
        # base64.b64decode(base64data)
        # print(base64_data)

    ssl._create_default_https_context = ssl._create_unverified_context  # 取消全局验证

    access_token = __get_token()

    postdata = urllib.parse.urlencode({
        "access_token": access_token,
        "image": base64_data
    }).encode('utf-8')  # 将数据使用urlencode编码处理后，使用encode()设置为utf-8编码

    req = urllib.request.Request(url, postdata)

    req.add_header('Content-Type', 'application/x-www-form-urlencoded')

    data = urllib.request.urlopen(req).read().decode('utf-8', 'ignore')
    data = json.loads(data)

    # if data['error_code'] == 17 or data['error_code'] == 18:

    data = jsonpath.jsonpath(data, '$.words_result[?(@.words)].words')
    if not data:
        # print('OCR没有返回值或者OCR额度已用完')
        # print('请求图片为%s' %name)
        # return None, None
        data = []
    return str(base64_data, encoding='utf-8'), '|'.join(data)
