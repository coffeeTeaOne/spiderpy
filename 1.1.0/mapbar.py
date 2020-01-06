import requests
import time

from OperateDB import conn_mysql
from OperateDB.conn_mongodb import Op_MongoDB


def mpfrun(code=None):
    opmysql = conn_mysql.Op_Mysql()
    addr_output = opmysql.Select_Query(tablename='spi_scra_addr', where='ENTITY_CODE_="%s"' % code)
    print(addr_output)
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
    }
    # url = 'https://poi.mapbar.com/beijing/A20/'
    re = requests.get(url=addr_output[0]['PATH_'], headers=header).content.decode('utf-8')
    # re = requests.get(url=url, headers=header).content.decode('utf-8')
    print(re)
    from scrapy.selector import Selector
    conn = Op_MongoDB().conn_mongo()
    op_fix = Op_MongoDB(db='spider_url_fixed', coll=code, key='URL_',conn=conn)
    op_temp = Op_MongoDB(db='spider_url_temp', coll=code, key='URL_',conn=conn)
    con_data = {}

    r = Selector(text=re)
    for m in range(18):
        BTYPE_ = r.xpath('//div[@class="sortRow"]/h3[{}]/text()[2]'.format(m + 1)).extract()[0]
        ALL = r.xpath('//div[@class="sortRow"]/div[{}]/a'.format(m + 1)).extract()
        for t in ALL:
            print(t)
            param = []
            for i in ['ID', 'TYPE_', 'url', 'BTYPE_']:
                data = dict()
                data['code'] = i
                if i == 'ID':
                    data['value'] = Selector(text=t).xpath('//a/@id').extract()[0]
                elif i == 'TYPE_':
                    data['value'] = Selector(text=t).xpath('//a/@title').extract()[0]
                elif i == 'url':
                    data['value'] = Selector(text=t).xpath('//a/@href').extract()[0]
                else:
                    data['value'] = BTYPE_
                param.append(data)
            deal_time = time.time()
            time_local = time.localtime(deal_time)
            dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
            con_data['DEALTIME_'] = deal_time
            con_data['DATETIME_'] = str(dt)
            con_data['ENTITY_NAME_'] = '图吧'
            con_data['ENTITY_CODE_'] = code
            con_data['URL_'] = param[2]['value']
            con_data['STATUS_'] = '1'
            con_data['LOCKTIME_'] = ''
            con_data['PARAM_'] = param
            print(con_data)
            op_fix.I_Mongodb(con_data)
            op_temp.I_Mongodb(con_data)

    return True
if __name__ == '__main__':
    mpfrun()