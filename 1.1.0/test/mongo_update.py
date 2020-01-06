

import pymongo
import json

ip_list = ['192.168.1.73', '192.168.1.81', '192.168.1.102']
client_sc = pymongo.MongoClient(ip_list, port=27017)
# client_41 = pymongo.MongoClient(host='172.22.69.41', port=20000)
# client_35 = pymongo.MongoClient(host='172.22.69.35', port=20000)
# client_localhost = pymongo.MongoClient(host='localhost', port=27017)

# datasc = client_sc['spider_data']
# collection_sc = datasc['WECHAT'] # 华夏银行-信用卡微博

codes = ['XYK_WB_GFYH',	'XYK_WB_HXYH','XYK_WB_JTYH',
         'XYK_WB_PAYH','XYK_WB_PFYH','XYK_WB_XYYH','XYK_WB_ZASYH',
         'XYK_WB_ZGGDYH','XYK_WB_ZGJSYH','XYK_WB_ZGMSYH','XYK_WB_ZGNYYH','XYK_WB_ZGYH','XYK_WB_ZXYH']

urls = {

}

data_old = client_sc['spider_data_old']
data = client_sc['spider_data']
for k,v in urls.items():
    if 'ZX_HYBG' in v:
        c_old = data_old['ZX_HYBG']
        c = data['ZX_HYBG']
    elif 'ZX_CJXW_GJJRJG' in v:
        c_old = data_old['ZX_CJXW_GJJRJG']
        c = data['ZX_CJXW_GJJRJG']
    elif 'ZX_CJXW_ZYCJ' in v:
        c_old = data_old['ZX_CJXW_ZYCJ']
        c = data['ZX_CJXW_ZYCJ']
    else:
        c_old = data_old['ZX_CJXW_ZYCJ']
        c = data['ZX_CJXW_ZYCJ']
    result = c_old.find({'URL_': k})
    dataee = result.next()
    del dataee['_id']
    print(dataee)
    # collection.update({'ENTITY_NAME_': r}, {'$set': {'ENTITY_NAME_': r.replace('-','')}})
    c.insert_one(dataee)
