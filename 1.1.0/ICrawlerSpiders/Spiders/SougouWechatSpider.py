# encoding: utf-8
import base64
import ssl
from scrapy.selector import Selector

from ICrawlerSpiders.useragent import user_agent_list
from OperateDB.conn_redis import RedisClient
from SpiderTools.tool import WeixinVerifiy
from SpiderTools.tool import get_base64
from SpiderTools.tool import Download
from SpiderTools.tool import platform_system
from Env.parse_yaml import FileConfigParser
from OperateDB.conn_mongodb import Op_MongoDB
from staticparm import root_path
from TemplateMiddleware.content_midlewares import Content_Middleware
from SpidersLog.icrwler_log import ICrawlerLog
import requests
import time
import random
ssl._create_default_https_context = ssl._create_unverified_context
"""
NRCWKWECHAT	南海农商银行微刊	nanhainongshang
NRCLSJRWECHAT	南海农商银行零售金融	gh_b540b14de11e 
SDELSWECHAT	顺德农商银行零售银行	SHUNDEnongshang
SDEEPWECHAT	顺德农商银行恩平支行	gh_9e0e73a728eb 
SDEYDWECHAT	顺德农商银行英德支行	gh_88c7e5c3d7c4
SDEJRSCWECHAT	顺德农商银行金融市场	gh_ed09c97107ca
SDEWSHWECHAT	顺德农商银行微生活	gh_33150ac1ea83
SDEJRWECHAT	顺德农商银行公司金融	gh_68213812bb45
"""

class WechatSpider:

    name = 'wechat'

    def query_code(self, code, entity_code, entity_name):
        # entity_code = 'SDEJRWECHAT'
        # entity_name = '顺德农商银行公司金融'
        # code = 'gh_68213812bb45'

        '''
        通过微信号来查询数据
        :param code: 微信号
        :return:
        '''
        log = ICrawlerLog(name='spider').save
        log.info('微信开始运行---')
        img_dir = FileConfigParser().get_path(server=platform_system(), key='wechatimg')
        img_dir = root_path + img_dir
        conn = Op_MongoDB().conn_mongo()
        op = Op_MongoDB(db='spider_data', coll='WECHAT', key='TITLE_', conn=conn)
        op_title = Op_MongoDB(db='spider_data', coll='WECHAT_TITLE_', key='TITLE_', conn=conn)

        midd = Content_Middleware('WeChat.CONTENT').Invoking_Diff()
        log.info('中间件执行成功！（mysql）')
        if midd:
            log.info('{}'.format(midd[0]))
            midd = midd[0]
        else:
            log.info('midd为空')
            return False
        log.info('解析midd')
        url = midd['config']['GRAB'][0]['url'][0]
        parm = midd['config']['GRAB'][0]['parm'][0]
        parm['query'] = code
        header = midd['config']['GRAB'][0]['header']
        header['Referer'] = 'http://weixin.sogou.com/weixin?type=1&s_from=input&query=%s&ie=utf8&_sug_=y&_sug_type_=' % code.strip()
        header['User-Agent'] = random.choice(user_agent_list)

        try:
            session = requests.session()
            log.info('首页请求！')
        except Exception as e:
            log.error('index, 请求错误！' + str(e.args))
            return False
        log.info('首页请求成功！')  #  必须要解决新的 cookies 问题
        info = {}
        info['name'] = entity_name

        info['code'] = code

        if info:
            cookies = {'IPLOC': 'CN5101', 'SUID': 'B05CD1DE4942910A000000005CF76983', 'ABTEST': '4|1559718275|v1',
                       'SNUID': '937FF5FA2321ABDFF5A11A34246B35ED'}
            for _ in range(6):
                log.info('开始循环获取公众最近文章')
                verifiy = WeixinVerifiy()
                article_data = verifiy.main(entity_name)
                if not article_data:
                    log.info('该公众号没有文章更新！')
                    # return False
                    continue
                log.info('成功绕过验证码！')
                if article_data['new_article_url']:
                    headers = {
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': 'zh-CN,zh;q=0.9',
                        'Cache-Control': 'max-age=0',
                        'Connection': 'keep-alive'
                    }

                    # 处理内容
                    con_data = {}
                    title_data = {}

                    con_data['TITLE_'] = article_data['new_article_title']
                    a_all = op_title.S_Mongodb(collection='WECHAT_TITLE_', output='TITLE_')
                    if con_data['TITLE_'] in a_all:
                        log.info('数据库已有该条数据！')
                        return False
                    con_data['SOURCE'] = '微信'
                    # 发布时间
                    con_data['PERIOD_CODE_'] = time.strftime("%Y-%m-%d", time.localtime(int(article_data['pubdate'])))
                    try:
                        log.info('单条内容请求！')
                        headers['User-Agent'] = random.choice(user_agent_list)
                        time.sleep(random.randint(1,3))
                        # print(article_data['new_article_url'])

                        article_data['new_article_url'] = 'https://mp.weixin.qq.com/s/mD2_MIyReU_eu_0YAsvMvg'

                        content_data = requests.get(url=article_data['new_article_url'], headers=headers, proxies=self.ip_proxy(), timeout=10, cookies=cookies).text
                        if not content_data:
                            content_data = session.get(url=article_data['new_article_url'], headers=headers, proxies=self.ip_proxy(), timeout=10, ).text
                        log.info('单条内容获取成功！')
                        for c_ in Selector(text=content_data).xpath('//img/@data-src').extract():
                            img_name = c_.split('/')[-1].replace('?','').replace('#','').replace('=','.')
                            Download(c_, img_dir, img_name)
                            img_base64 = get_base64(img_dir, img_name)
                            old = 'data-src="%s"' % c_
                            new = 'data-src="%s" src="data:image/png;base64,%s"' % (c_, img_base64)
                            content_data = content_data.replace(old, new)

                        con_data['BANK_NAME_'] = info['name'].split('银行')[0] + '银行'
                        con_data['CONTENT_TYPE_'] = 'html'
                        con_data['ENTITY_CODE_'] = entity_code
                        con_data['WECHAT_'] = code
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
                        title_data['PERIOD_CODE_'] = con_data['PERIOD_CODE_']
                        title_data['WECHAT_'] = con_data['WECHAT_']
                        title_data['ENTITY_NAME_'] = con_data['ENTITY_NAME_']
                        title_data['DEALTIME_'] = con_data['DEALTIME_']
                        title_data['DATETIME_'] = con_data['DATETIME_']
                        op_title.I_Mongodb(title_data)
                        op_title.conn.close()
                        # print('标题完成')
                        return True
                    except:
                        conn.close()
                        log.info('此条数据抓取有问题！')
                        return False
                else:
                    # print('new_article_url为空！')
                    log.info('new_article_url为空！获取内容链接出错！重新获取！')
                    time.sleep(random.randint(1, 3))
                    continue
        else:
            conn.close()
            return False

    def ip_proxy(self):
        log = ICrawlerLog(name='spider').save
        try:
            ip = RedisClient().get()
            log.info('当前使用ip为%s' % ip)
            proxies = {
                       'http': 'http://' + ip,
                       'https': 'https://' + ip,
                       }
            log.info('ip代理获取成功！')
            return proxies
        except Exception as e:
            log.error(e.args)
            log.error('ip代理获取失败！')
            print(6)
            return False


if __name__ == '__main__':
    url = 'http://www.ccidnet.com/news/focus/'
    # print(WechatSpider().rrr(url))
    # print(random.choice(user_agent_list))

