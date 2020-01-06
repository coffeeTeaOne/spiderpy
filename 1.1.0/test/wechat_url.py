# encoding: utf-8
import base64
import ssl
import os, sys

curPath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(curPath[:-24])

from scrapy.selector import Selector
from ICrawlerSpiders.useragent import user_agent_list
from OperateDB.conn_redis import RedisClient
from SpiderTools.tool import get_base64
from SpiderTools.tool import Download
from SpiderTools.tool import platform_system
from Env.parse_yaml import FileConfigParser
from OperateDB.conn_mongodb import Op_MongoDB
from staticparm import root_path
import requests
import time
import random
import json
import re

ssl._create_default_https_context = ssl._create_unverified_context


class WechatSpider:
    name = 'wechat'

    def query_code(self, code, entity_code, entity_name):
        '''
        通过微信号来查询数据
        :param code: 微信号
        :return:
        '''
        img_dir = FileConfigParser().get_path(server=platform_system(), key='wechatimg')
        img_dir = root_path + img_dir
        conn = Op_MongoDB().conn_mongo()
        op = Op_MongoDB(db='spider_data', coll='WECHAT', key='TITLE_', conn=conn)
        op_title = Op_MongoDB(db='spider_data', coll='WECHAT_TITLE_', key='TITLE_', conn=conn)
        headers = {}
        headers['User-Agent'] = random.choice(user_agent_list)

        # 处理内容
        con_data = {}
        title_data = {}
        cookies = {}
        session = requests.session()
        # con_data['TITLE_'] = article_data['new_article_title']

        a_all = op_title.S_Mongodb(collection='WECHAT_TITLE_', output='TITLE_')

        con_data['SOURCE'] = '微信'
        # 发布时间
        # con_data['PERIOD_CODE_'] = time.strftime("%Y-%m-%d", time.localtime(int(article_data['pubdate'])))
        bank_list = {
            "中国农业银行顺德分行": "ABCSHUNDWECHAT",
            "中国农业银行广东南海分行": "ABCGUANGDWECHAT",
            "中国银行广东分行": "BOCGUANGDWECHAT",
            "建设银行佛山市分行": "CCBFOSWECHAT",
            "中国光大银行广州分行": "CEBGUANGZWECHAT",
            "广发银行佛山分行零售金融": "CGBFOSWECHAT",
            "兴业银行广州分行": "CIBGUANGZWECHAT",
            "招商银行佛山分行": "CMBFOSWECHAT",
            "民生银行佛山分行": "CMBCFOSWECHAT",
            "中信银行信用卡佛山": "ECITICXINGYKWECHAT",
            "中信银行佛山分行": "ECITIFOSWECHAT",
            "工商银行佛山分行": "ICBCFOSWECHAT",
            "南海农商银行": "NRCBNANHWECHAT",
            "南海农商银行零售金融": "NRCBLINGSWECHAT",
            "南海农商银行微刊": "NRCBWEIKWECHAT",
            "平安银行佛山分行": "PABFOSWECHAT",
            "顺德农商银行": "SRCBSHUNDWECHAT",
            "顺德农商银便利社区": "SRCBBIANLWECHAT",
            "顺德农商银行零售银行": "SRCBLINGSWECHAT",
            "顺德农商银行恩平支行": "SRCBENPWECHAT",
            "顺德农商银行英德支行": "SRCBYINGDWECHAT",
            "顺德农商银行金融市场": "SRCBJINGRWECHAT",
            "顺德农商银行微生活": "SRCBWEISHWECHAT",
            "顺德农商银行公司金融": "SRCBGONGSWECHAT",
            "招商银行石家庄分行": "CMBSJZWECHAT",  # CMBSJZWECHAT
            "中信银行石家庄分行": "ECITICSJZWECHAT",  # ECITICSJZWECHAT
            "工行河北": "GHHBWECHAT",  # GHHBWECHAT
            "浦发银行信用卡石家庄": "PFYHWECHAT",  # PFYHWECHAT
            "中国农业银行石家庄分行": "ABCSJZWECHAT",  # ABCSJZWECHAT
            "中国农业银行河北分行": "ABCHBFYWECHAT",  # ABCHBFYWECHAT
            "交通银行河北省分行": "COMMHBWECHAT",  # COMMHBWECHAT
            "渤海银行石家庄分行": "BOHAIBSJZWECHAT",  # BOHAIBSJZWECHAT
            "建设银行石家庄河北师大分理处": "CCBSJZHBSDWECHAT",  # CCBSJZHBSDWECHAT
            "中国光大银行石家庄分行": "CEBSJZWECHAT",  # CEBSJZWECHAT
            # "": "",

        }
        import os
        import xlrd
        # 遍历文件夹
        # path = os.path.dirname(os.path.dirname(__file__)) + '/File/excel/'
        path = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + '/File/excel/'
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                # 读取excel文件
                file = os.path.join(root, name)
                wb = xlrd.open_workbook(filename=file)  # 打开文件
                print(file)
                sheet_names = wb.sheet_names()
                # code = sheet_names # 公众号编码
                for key in sheet_names:
                    excel_data = wb.sheet_by_name(key)
                    entity_name = key  # 公众号名称
                    entity_code = bank_list.get(key)  # 公众号实体编码
                    row = excel_data.nrows  # 总行数
                    code = excel_data.row_values(0)[-1]
                    print('sheet_name{key}, 共{row}行')
                    for i in range(1, row):
                        rowdate = excel_data.row_values(i)  # i行的list
                        url = rowdate[0]

                        period_code = '-'.join([str(_) for _ in xlrd.xldate_as_tuple(rowdate[1], 0)[:3]])
                        if url == '':
                            continue
                        try:
                            headers['User-Agent'] = random.choice(user_agent_list)
                            time.sleep(random.randint(1, 3))
                            try:
                                content_data = requests.get(url=f'{url}', headers=headers, timeout=10, ).text
                                if not content_data:
                                    print('请求数据出错', url)
                            except:
                                print('请求错误', url, 'sheet_name{key}, 第{i}行')
                            html = Selector(text=content_data)
                            con_data['TITLE_'] = html.xpath(
                                '//*[@id="activity-name"]/text()').extract_first().strip() if html.xpath(
                                '//*[@id="activity-name"]').extract() else ''
                            if con_data['TITLE_'] in a_all:
                                continue
                            print('sheet_name{key}, 第{i}行请求成功')
                            for c_ in html.xpath('//img/@data-src').extract():
                                img_name = c_.split('/')[-1].replace('?', '').replace('#', '').replace('=', '.')
                                Download(c_, img_dir, img_name)
                                img_base64 = get_base64(img_dir, img_name)
                                old = 'data-src="%s"' % c_
                                new = 'data-src="%s" src="data:image/png;base64,%s"' % (c_, img_base64)
                                content_data = content_data.replace(old, new)

                            con_data['BANK_NAME_'] = name.replace('.xlsx', '')
                            con_data['CONTENT_TYPE_'] = 'html'
                            con_data['ENTITY_CODE_'] = entity_code
                            con_data['WECHAT_'] = code
                            con_data['PERIOD_CODE_'] = str(period_code)
                            con_data['ENTITY_NAME_'] = entity_name
                            deal_time = time.time()
                            time_local = time.localtime(deal_time)
                            dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
                            con_data['DEALTIME_'] = deal_time
                            con_data['DATETIME_'] = str(dt)
                            # 存储标题，为去重
                            # op_title.I_Mongodb(con_data)
                            con_data['CONTENT_'] = content_data
                            op.I_Mongodb(con_data)
                            # print('内容存储完成!')
                            # 标题需要的数据
                            title_data['ENTITY_CODE_'] = entity_code
                            title_data['TITLE_'] = con_data['TITLE_']
                            title_data['SOURCE'] = con_data['SOURCE']
                            title_data['BANK_NAME_'] = con_data['BANK_NAME_']
                            title_data['CONTENT_TYPE_'] = con_data['CONTENT_TYPE_']
                            title_data['PERIOD_CODE_'] = str(period_code)
                            title_data['WECHAT_'] = con_data['WECHAT_']
                            title_data['ENTITY_NAME_'] = con_data['ENTITY_NAME_']
                            title_data['DEALTIME_'] = con_data['DEALTIME_']
                            title_data['DATETIME_'] = con_data['DATETIME_']
                            op_title.I_Mongodb(title_data)
                            op_title.conn.close()
                            # print('标题完成')
                            # return False
                        except:
                            # conn.close()
                            # return False
                            continue

        conn.close()
        return False

    def ip_proxy(self):
        try:
            ip = RedisClient().get()
            proxies = {
                'http': 'http://' + ip,
                'https': 'https://' + ip,
            }
            return proxies
        except Exception as e:
            print(6)
            # print('adsfasdf')
            return False


if __name__ == '__main__':
    #  code, entity_code, entity_name
    WechatSpider().query_code('sdds', 'SDEJRSCWECHAT', '顺德农商银行金融市场')
    # import os
    # for root, dirs, files in os.walk(r'C:/Users/xiaozhi/Desktop/all_bank/', topdown=False):
    #     for name in files:
    #         # 读取excel文件
    #         file = os.path.join(root, name)
    #         print(file)
    # print(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    # print(os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + '\\File\\excel\\',)
