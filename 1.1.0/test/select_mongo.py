

import pymongo
import json

client = pymongo.MongoClient(host="172.22.69.35", port=20000)
# client = pymongo.MongoClient(host="172.22.69.41", port=20000)
# client = pymongo.MongoClient(host="localhost", port=27017)

datasc = client["spider_data"]
collection_sc = datasc['GOV_ZX_GDS']


# c_insert = client_35["spider_data"]
# collection= c_insert['HBNXS']




result = list(collection_sc.find({'ENTITY_CODE_':'GDSZ_MMS_SWJ_SWXW'}))

for i in result:

    fj = dict()
    a_url = str(i['URL_'])
    fj_url = i['FJ1_URL_']
    fj_name = i['FJ1_NAME_']
    # print(fj_url)
    # if 'http://www.bShare.cn/javascript:void(0);' in fj_url:
    #     fj_url = fj_url.replace('http://www.bShare.cn/javascript:void(0);','')
    # else:
    #     continue
    # print(fj_url)
    # fj['FJ1_URL_'] = fj_url
    # fj['FJ1_NAME_'] = str(fj_name).replace('|分享到','')
    # collection_sc.update({'URL_': i['URL_']}, {'$set': fj})
    # print(6)

    domain_url = '/'.join(str(a_url).split('/')[:3])
    print(domain_url)
    if 'http' in fj_url:
        continue
    else:
        fj['FJ1_URL_'] = 'http://mmswj.maoming.gov.cn' + fj_url
    collection_sc.update({'URL_': i['URL_']}, {'$set': fj})
    print(6)
    # new_url = '/'.join(str(a_url).split('/')[:-1])
    # try:
    #     if fj_url == '':
    #         print(1)
    #         continue
    #
    #     elif '|' not in fj_name:
    #     #     url = domain_url + '/' + a_url.split('../')[-1]
    #         if 'http' in fj_url:
    #             continue
    #         else:
    #             fj['FJ1_URL_'] = new_url + '/' + str(fj_url).split('./')[-1]
    #     elif fj_url[:4] == 'http':
    #         url_list = str(fj_url).split('http')[1:]
    #         name_list = str(fj_name).split('|')
    #         for j in range(len(name_list)):
    #             fj[f'FJ{j+1}_URL_'] = 'http' + url_list[j]
    #             fj[f'FJ{j+1}_NAME_'] = name_list[j]
    #     else:
    #         # fj_url = str(fj_url).split('http')[0]
    #         # url_list = str(fj_url).split('./')[1:]
    #         url_list = str(fj_url).split('|')
    #         print(url_list)
    #         name_list = str(fj_name).split('|')
    #         print(name_list)
    #         for j in range(len(name_list)):
    #             fj[f'FJ{j+1}_URL_'] = new_url + '/' + url_list[j]
    #             fj[f'FJ{j+1}_NAME_'] = name_list[j]
    #
    #     collection_sc.update({'URL_': i['URL_']}, {'$set': fj})
    #     print(0)
    # except:
    #     continue

