

import pymongo
client = pymongo.MongoClient(host="172.22.69.41", port=20000)
data_base = client["spider_data"]
collection = data_base['XYK_YJBG']


def my_requests(url):
    import requests
    data = {}
    left_url = '/'.join(url.split('/')[:-1])
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36'}
    res = requests.get(url=url, headers=headers).content.decode('UTF-8')
    from scrapy.selector import Selector

    res = Selector(text=res)

    data['PDF_URL_'] = left_url + '/' + str(res.xpath('//*[@class="copyCenter"]/a/@href').extract_first().split('./')[-1])
    data['PDF_NAME_'] = res.xpath('//*[@class="copyCenter"]/text()').extract_first().strip()
    return data


def con_mongo():
    result = collection.find({'ENTITY_CODE_': 'XYK_YJBG_NYYH'})
    for i in range(90):
        data = result.next()
        try:
            url = data['URL_']
            r = my_requests(url)
            collection.update({"_id": data["_id"]}, {"$set": r})
            print(i)
        except:
            print(data['URL_'])
            url = data['URL_'].replace('/am/','/mm/')
            try:
                r = my_requests(url)
                r['URL_'] = url
                collection.update({"_id": data["_id"]}, {"$set": r})
                print(i)
            except:
                print(data['URL_'])
                url = data['URL_'].replace('/am/', '/qm/')
                try:
                    r = my_requests(url)
                    r['URL_'] = url
                    collection.update({"_id": data["_id"]}, {"$set": r})
                    print(i)
                except:
                    continue



if __name__ == '__main__':
    con_mongo()