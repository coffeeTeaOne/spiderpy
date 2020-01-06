# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import json
import pyppeteer
import asyncio
import os


import requests
from scrapy import signals
from scrapy.http import HtmlResponse

from ICrawlerSpiders.settings import ENCRYPTION_ENTITY, ENCRYPTION_BY_HTML_ENTITY, ENCRYPTION_BY_API_AND_NO_IP_ENTITY, \
    ENCRYPTION_BY_HTML_FIREFOX, ENCRYPTION_BY_API_FIREFOX
from OperateDB.conn_redis import RedisClient
from SpiderTools.js_encrypt import GetJsEncryptPage,GetPageHtml, FirefoxGetPage
from SpiderTools.sougou_wechat_api import wash_url
from SpidersLog.icrwler_log import ICrawlerLog


class ProxyMiddleware(object):
    """
    scrapy设置ip代理
    """
    def __init__(self, ip):  # 这个方法有没有无所谓
        self.ip = ip

    @classmethod
    def from_crawler(cls, crawler):  # 这个方法有没有无所谓
        return cls(ip=crawler.settings.get('PROXIES'))

    def process_request(self, request, spider):
        """
        scrapy里面设置ip代理
        :param request:
        :param spider:
        :return:
        """
        self.log = ICrawlerLog(name='spider').save
        try:
            self.ip = RedisClient().get()
            if 'http:' in request.url:
                self.ip = 'http://' + self.ip
            if 'https:' in request.url:
                self.ip = 'https://' + self.ip
            self.log.info('当前使用ip为%s' % self.ip)
        except Exception as e:
            self.log.error(e)
            print(6)
            raise Exception(e)
        request.meta['proxy'] = self.ip


class DLMiddleware(object):
    '''
    修改部分spider的延迟时间
    '''
    def process_request(self, request, spider):
        '''
        延迟下载网页, 只要返回HTTPResponse就不再执行其他下载中间件
        :param request: scrapy整合的全局参数
        :param spider: spiders里的爬虫对象
        :return:
        '''

            # 修改部分spider的延迟时间
        if spider.entity_code in ['JRCP_JJ_GFYH_GW_ALL', 'JRCP_JJ_BHYH_GW_ALL', 'ZX_ZCGG_YBH_JGDT', 'ZX_ZCGG_ZGRMYH_TFS', 'ZX_ZCGG_YBH_GGTZ']:
            request.meta['download_timeout'] = 6000
            request.meta.setdefault('download_delay', 5)


class DownLoadsMiddleware(object):
    """
    js加密实体
    """
    def __init__(self):
        self.session = requests.Session()
        self.log = ICrawlerLog('spider').save
        try:
            self.ip = RedisClient().get()
        except Exception as e:
            self.log.error(e)
            print(6)
            raise e
        self.proxies = {
            "http": 'http://' + self.ip,
            "https": 'https://' + self.ip,
        }

    def process_request(self, request, spider):

        # 使用pyppeteer获取数据
        header = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"}
        # cookie加密实体
        if spider.entity_code in ENCRYPTION_ENTITY:
            try:
                JS_url = wash_url(request.url)
                # 获取cookie(默认get请求）
                if request.method == 'GET':
                    cookies, ip, ua, content,content_url = GetJsEncryptPage().run(JS_url, spider.entity_code)
                    print(JS_url)
                    return HtmlResponse(url=request.url, body=str(content), encoding='utf-8', request=request)
                # post请求走这个逻辑（post，cookie加密，必须配置referer）
                else:
                    # 修改这个 url 为 Referer 中的url
                    try:
                        JS_url = (request.headers.get('Referer') if request.headers.get('Referer') else request.url).decode('utf-8')
                    except:
                        JS_url = wash_url(request.url)
                    cookies, ip, ua, content, content_url = GetJsEncryptPage().run(JS_url, spider.entity_code)
                    try:
                        from urllib.parse import quote
                        data_ = request.meta.get('parm').copy()
                        for key in data_.keys():
                            data_[key] = quote(data_[key])
                    except:
                        data_ = ''
                    try:
                        data_.pop('SALE_SOURCE_')  # 获取请求参数
                    except Exception as e:
                        try:
                            data_.pop('SOURCE_TYPE_')  # 获取请求参数
                        except Exception as e:
                            pass
                        pass
                    view_url = wash_url(request.url)
                    # # 使用 pyppeteer 中的 UA / IP
                    header['User-Agent'] = ua
                    proxies = {'http': f'http://{ip}', 'https': f'https://{ip}'}
                    if request.meta.get('param_type') == 'PAYLOAD':
                        data_ = json.dumps(data_)
                    # # 使用代理IP 的实体
                    if spider.entity_code not in ENCRYPTION_BY_API_AND_NO_IP_ENTITY:
                        # 使用ip代理
                        if data_:
                            result = requests.post(url=view_url, headers=header, data=data_, cookies=cookies, proxies=proxies, allow_redirects=False, verify=False)
                        else:
                            result = requests.post(url=view_url, headers=header, cookies=cookies, proxies=proxies, allow_redirects=False, verify=False)
                    else:
                        # 不使用ip代理
                        if data_:
                            result = requests.post(url=view_url, headers=header, data=data_, cookies=cookies, allow_redirects=False, verify=False)
                        else:
                            result = requests.post(url=view_url, headers=header, cookies=cookies, allow_redirects=False, verify=False)

                    # 更换数据编码
                    if request.meta.get('textType') == 'html':
                        if result.status_code in [200, 304]:
                            encode = result.encoding
                            if not encode:
                                encode = 'UTF-8'
                            if encode == 'ISO-8859-1':
                                encodings = requests.utils.get_encodings_from_content(result.text)
                                if encodings:
                                    encode = encodings[0]
                                else:
                                    encode = result.apparent_encoding
                            sources = result.content.decode(encode, 'replace')
                    else:
                        sources = result.json()
                    return HtmlResponse(url=request.url, body=str(sources), encoding='utf-8', request=request)

            except Exception as e:
                # self.process_request(request, spider)
                self.log.error('响应超时, {}'.format(e))
                raise Exception(e)

        # 单独处理直接可以拿到HTML页面的实体--通过selenium + firefox（目前只有浦发官网动态，测试有问题）
        if spider.entity_code in ENCRYPTION_BY_HTML_ENTITY:
            try:
                JS_url = wash_url(request.url)
                print(JS_url)
                charset, cookie, html_url, content, ua, proxy = FirefoxGetPage().work(JS_url)
                return HtmlResponse(url=request.url, body=str(content), encoding=charset, request=request)
            except Exception as e:
                # self.process_request(request, spider)
                self.log.error('响应超时, {}'.format(e))
                raise Exception(e)

        # 单独处理直接可以拿到HTML页面的实体--通过 Firefox
        if spider.entity_code in ENCRYPTION_BY_HTML_FIREFOX or spider.entity_code in ENCRYPTION_BY_API_FIREFOX:
            try:
                page = FirefoxGetPage()
                if spider.entity_code in ENCRYPTION_BY_API_FIREFOX:
                    # 修改这个 url 为 Referer 中的url
                    try:
                        JS_url = (request.headers.get('Referer') if request.headers.get('Referer') else request.url).decode('utf-8')
                    except:
                        JS_url = wash_url(request.url)
                    charset, cookies, html_url, page_source, UA, IP = page.work(JS_url)
                    try:
                        from urllib.parse import quote
                        data_ = request.meta.get('parm').copy()
                        for key in data_.keys():
                            data_[key] = quote(data_[key])
                    except:
                        data_ = ''
                    try:
                        data_.pop('SALE_SOURCE_')  # 获取请求参数
                    except Exception as e:
                        try:
                            data_.pop('SOURCE_TYPE_')  # 获取请求参数
                        except Exception as e:
                            pass
                        # self.log('请求参数传递错误, {}'.format(e))
                        pass
                    view_url = wash_url(request.url)

                    # 使用 firefox 中的 UA / IP
                    header['User-Agent'] = UA
                    proxies = {'http': f'http://{IP}', 'https': f'https://{IP}'}

                    if request.meta.get('param_type') == 'PAYLOAD':
                        data_ = json.dumps(data_)

                    # 使用代理IP 的实体
                    if spider.entity_code not in ENCRYPTION_BY_API_AND_NO_IP_ENTITY:
                        if data_:
                            result = requests.post(url=view_url, headers=header, data=data_, cookies=cookies,
                                                   proxies=proxies, allow_redirects=False,
                                                   verify=False) if request.method == 'POST' else requests.get(
                                url=view_url, headers=header, params=data_, cookies=cookies, proxies=proxies,
                                allow_redirects=False, verify=False)
                        else:
                            result = requests.post(url=view_url, headers=header, cookies=cookies, proxies=proxies,
                                                   allow_redirects=False,
                                                   verify=False) if request.method == 'POST' else requests.get(
                                url=view_url, headers=header, cookies=cookies, proxies=proxies, allow_redirects=False,
                                verify=False)

                    else:
                        if data_:
                            result = requests.post(url=view_url, headers=header, data=data_, cookies=cookies,
                                                   allow_redirects=False,
                                                   verify=False) if request.method == 'POST' else requests.get(
                                url=view_url, headers=header, params=data_, cookies=cookies, allow_redirects=False,
                                verify=False)
                        else:
                            result = requests.post(url=view_url, headers=header, cookies=cookies, allow_redirects=False,
                                                   verify=False) if request.method == 'POST' else requests.get(
                                url=view_url, headers=header, cookies=cookies, allow_redirects=False, verify=False)

                    # 更换数据编码
                    if request.meta.get('textType') == 'html':
                        if result.status_code in [200, 304]:
                            encode = result.encoding
                            if not encode:
                                encode = 'UTF-8'
                            if encode == 'ISO-8859-1':
                                encodings = requests.utils.get_encodings_from_content(result.text)
                                if encodings:
                                    encode = encodings[0]
                                else:
                                    encode = result.apparent_encoding
                            sources = result.content.decode(encode, 'replace')
                    else:
                        sources = result.json()
                    return HtmlResponse(url=request.url, body=str(sources), encoding='utf-8', request=request)

                else:
                    JS_url = wash_url(request.url)
                    charset, cookie, html_url, page_source, UA, IP = page.work(JS_url)
                    return HtmlResponse(url=request.url, body=str(page_source), encoding=charset, request=request)
            except Exception as e:
                # self.process_request(request, spider)
                self.log.error('响应超时, {}'.format(e))
                raise Exception(e)


pyppeteer.DEBUG = False


class FundscrapyDownloaderMiddleware(object):
    """
    通过pyppeteer直接获取response页面方式
    """

    def __init__(self):
        # print("Init downloaderMiddleware use pypputeer.")
        os.environ['PYPPETEER_CHROMIUM_REVISION'] = '588429'
        # pyppeteer.DEBUG = False
        # print(os.environ.get('PYPPETEER_CHROMIUM_REVISION'))
        loop = asyncio.get_event_loop()
        task = asyncio.ensure_future(self.getbrowser())
        loop.run_until_complete(task)

        # self.browser = task.result()
        # print(self.browser)
        # print(self.page)
        # self.page = await browser.newPage()

    async def getbrowser(self):
        ip = RedisClient().get()
        self.browser = await pyppeteer.launch({'headless': True, 'timeout': 10,
                                'args': [
                                    '--no-sandbox',
                                    '--disable-gpu',
                                    '--disable-infobars',
                                    '--proxy-server={}'.format(ip),
                                ], })
        self.page = await self.browser.newPage()
        # return await pyppeteer.launch()

    async def getnewpage(self):
        return await self.browser.newPage()

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        if spider.entity_code == 'ZX_CJXW_GJJRJG_GJSWZJ_GDSW':
            loop = asyncio.get_event_loop()
            task = asyncio.ensure_future(self.usePypuppeteer(request))
            loop.run_until_complete(task)
            # return task.result()
            # print(request.url)
            # print(task.result())
            return HtmlResponse(url=request.url, body=task.result(), encoding="utf-8", request=request)

    async def usePypuppeteer(self, request):
        print(request.url)
        # page = await self.browser.newPage()
        await self.page.goto(request.url)
        content = await self.page.content()
        return content

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class TestMiddleware(object):
    def process_request(self, request, spider):
        """
        测试
        :param request:
        :param spider:
        :return:
        """
        if spider.entity_code in ['CCBPage','CCBPage2','CCBPage3','CCBORGANIZE','CCBORGANIZE2','CCBORGANIZE3']:
            try:
                import requests
                import ssl
                ssl._create_default_https_context = ssl._create_unverified_context
                requests.packages.urllib3.disable_warnings()
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
                    'Cookie': '',
                }
                # print(request.url)
                res = requests.request(method='GET', url=request.url, headers=headers, verify=False, allow_redirects=False).text
                print(res)
                if '{' not in res and '}' not in res:
                    print('cookie过期！')
                    return False
                return HtmlResponse(url=request.url, body=str(res), encoding='utf-8', request=request)
            except Exception as e:
                return False


