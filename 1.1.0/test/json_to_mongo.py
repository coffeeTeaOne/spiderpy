import json

import pymongo
def r_json_data():
    """
    json文件存mongo
    :return:
    """


    # ip_list = ['192.168.1.73', '192.168.1.81', '192.168.1.102']
    # client_sc = pymongo.MongoClient(ip_list, port=27017)
    client_localhost = pymongo.MongoClient(host="localhost", port=27017)

    datalocalhost = client_localhost["spider_data"]
    collection = datalocalhost['WD_JZ_FJ_SH']
    datas = collection.find()
    num = 1
    while True:
        with open("./datas/{}.json".format(num), 'r') as f:
            load_dict = json.load(f)
        collection.insert(load_dict)
        print(num)
        num += 1


def w_json_data():

    """
    mongo数据导出json文件
    :return:
    """


    # ip_list = ['192.168.1.73', '192.168.1.81', '192.168.1.102']
    # client = pymongo.MongoClient(ip_list, port=27017)

    # client = pymongo.MongoClient(host="localhost", port=27017)
    client = pymongo.MongoClient(host="172.22.69.35", port=20000)

    datalocalhost = client["spider_data"]
    collection = datalocalhost['WD_JZ_FJ_SH']
    datas = collection.find({'ENTITY_CODE_':'WD_JZ_FJ_LISPZL_SH','d':-1})
    num = 1
    for i in datas:
        try:
            del i['_id']
            # del i['d']
            # del i['shuffleErro']
        except:
            pass
        if i['ENTITY_CODE_'] == 'WD_JZ_FJ_LISPZL_SH':
            print(i)
            with open("./datas/{}.json".format(num), 'w') as f:
                json.dump(i, f)
            num += 1



def request_test():
    import requests
    import jsonpath
    client = pymongo.MongoClient(host="172.22.69.35", port=20000)

    datalocalhost = client["spider_data"]
    collection = datalocalhost['WD_JZ_FJ_SH']
    datas = collection.find({'ENTITY_CODE_':'WD_JZ_FJ_LISPZL_SH'})
    for i in datas:
        url = i['url']
        try:
            res = requests.get(url=url).json()
            addr = jsonpath.jsonpath(res,'$.data.docs.bizcircleName')
            print(addr)
            collection.update({'URL_': i['URL_']}, {'$set': {'ADDR_': addr[0]}})
        except:
            continue

if __name__ == '__main__':
    # 导出
    # w_json_data()
    # # 导入
    # r_json_data()
    request_test()











