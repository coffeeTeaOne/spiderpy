import random

import requests
import ssl

import time

ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings()

url = 'http://www.jsbchina.cn/CN/kjjr/jrxx/jzcg/xygg/index.html?flag=1'
headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
    'Cookie': 'FSSBBIl1UgzbN7N80S=fnfH9rL.eSXqYssqhTXDgwJn2Y5OfQjyxzTT.mB5PeBx4PlPUdrVdkiiiPLuFx_h; Hm_lvt_2d4a8bd774e28e48ea5416a200b25a30=1577429620; Hm_lpvt_2d4a8bd774e28e48ea5416a200b25a30=1577433287; FSSBBIl1UgzbN7N80T=4ug440xJu25scjcyh06dM4M3TLsv3T.ppnzxfhMJeuWfUJnm.F1E406wEbdQO2.k4zXkC7IJSIZyhk6RksWck4t9rlO5NuIvh_LwB6FWoPgtci7zPvgi5GAjRzEu9UWkFDAi.ulNhJqDPHP0xdqqozlPYaPBOJHvO7zEE1iZvF2Z5NJcr9QZ6cEpZ0HRXcDpzXRFO7oW0nOb42HFPB44JNSCH30tXfL8oZQpYd4OBfvaUWTmniBWy8AUubN4AVJ8CPLzRirmzF9kmCtATBY4sUwibma5W_OmXg9lsrlt.p6HF1DHBouzYwb5f84ZfCX3u_7YHFm4G0wdviVoC0_SvBk8Kioel_r4c_H9azm1eOkos6FwatmYhrBaM0VIqLga561E'
            # 'Referer': 'https://ibuy.ccb.com/cms/channel/ccbbidzbgg/index.htm',
        }

data = {'pageNo': '1',
        # 'keyword':'',
        # 'region':'',
        # 'beginDate':'',
        # 'endDate':''
}
# session = requests.Session()
# res = session.get(url=burl, headers=headers, verify=False,allow_redirects=False)
res = requests.request(method='GET', url=url,headers=headers, verify=False, allow_redirects=False)

print(res.content.decode('utf-8'))