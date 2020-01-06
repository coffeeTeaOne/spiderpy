import ssl

import requests

from test.js_cookie.js_cookie import GetJsEncryptPage

ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings()

url = 'https://www.spdb.com.cn/was5/web/search'
cookies = GetJsEncryptPage().run(url='https://www.spdb.com.cn/web_query/')
print(cookies)
cookie = {
# '1111':'1567067633857',
# 'firstLoad':'no',
# 'Hm_lvt_e3386c9713baeb4f5230e617a0255dcb':'1567067626',
# 'WASSESSION':'CZ_cj4bzeJtOgPL6MVNsy7uayPHEgwGNMxNmrewdlq0W3SYw8VyH!1727271355',
# 'Hm_lpvt_e3386c9713baeb4f5230e617a0255dcb':'1567068562',
# 'TSPD_101':'08e305e14cab2800ccd38da972081fe96af855a62053f786efd674e4f63c0e68605aed64748d3df948b74976ce805356:',
'TSPD_101':cookies['TSPD_101'],
# 'TS01d02f4c':'01ea722d2af319c0e64b2a70b265ea1808ecfe80e058d075aea55a06f901b57b47f8ae6d0d7837638245dd7cdc462dd612e8d1329b01d8fe09a155bb7a6d0e49d9e83b7177'
}


headers = {
    # 'Host': 'www.spdb.com.cn',
    # 'Origin': 'https://www.spdb.com.cn',
    # 'Referer': 'https://www.spdb.com.cn/web_query/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
    # 'X-Requested-With': 'XMLHttpRequest',
}

data = {
    'metadata': 'deptinfo_orgid|deptinfo_name|deptinfo_address|deptinfo_postcode|deptinfo_telno|deptinfo_longitude|deptinfo_dimensions',
    'channelid': '243263',
    'page': 2,
    'searchword': '((deptinfo_address,deptinfo_name)+=%)*(deptinfo_province=%四川省%)*(deptinfo_city=%%%)',
}
res = requests.post(url=url,headers=headers,data=data,cookies=cookie,verify=False)
print(res.status_code)
print(res.text)