

import pymongo
import json
import requests
import ssl


ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings()


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
}

client_35 = pymongo.MongoClient(host="172.22.69.35", port=20000)
# client_localhost = pymongo.MongoClient(host="localhost", port=27017)

datasc = client_35["spider_address"]
collection_sc = datasc['HBNXS_WD.ADDR']

c_insert = client_35["spider_data"]
collection_insert = c_insert['HBNXS']

result = list(collection_sc.find())


for i in result:
    url = i['URL_']
    res = requests.request(method='GET', url=url, headers=headers, verify=False,allow_redirects=False)
    r = eval(res.text)
    for i in range(len(eval(r['names']))):
        result_dict = {}
        result_dict['points'] = eval(r['points'])[i]
        result_dict['names'] = eval(r['names'])[i]
        result_dict['wdjsjd'] = eval(r['wdjsjd'])[i]
        result_dict['phone'] = eval(r['phone'])[i]
        result_dict['address'] = eval(r['address'])[i]
        result_dict['cityEnglishName'] = eval(r['cityEnglishName'])[i]
        print(result_dict)
        collection_insert.insert(result_dict)

