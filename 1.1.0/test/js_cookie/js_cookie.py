import asyncio
import base64
import os
import ssl
import time, random

import pyppeteer
import requests
from pyppeteer.launcher import launch  # 控制模拟浏览器用
from pyppeteer import errors

from ICrawlerSpiders.useragent import user_agent_list
from OperateDB.conn_redis import RedisClient
from SpiderTools.tool import get_ip, platform_system
from SpidersLog.icrwler_log import ICrawlerLog
from staticparm import root_path
from ICrawlerSpiders.settings import ENCRYPTION_ENTITY, ENCRYPTION_BY_HTML_ENTITY, ENCRYPTION_BY_HTML_AND_IP_ENTITY, \
    ENCRYPTION_NOT_IP_ENTITY


class GetJsEncryptPage(object):

    def __init__(self):

        self.loop = asyncio.get_event_loop()
        self.log = ICrawlerLog('spider').save

    async def main(self, url, entityCode):  # 定义main协程函数，
        # 以下使用await 可以针对耗时的操作进行挂起
        if entityCode in ENCRYPTION_NOT_IP_ENTITY:
            browser = await launch({'headless': False, 'args': ['--no-sandbox', '--disable-infobars',
                                                               # '--proxy-server={}'.format(get_ip()),
                                                               ], })  # 启动pyppeteer 属于内存中实现交互的模拟器
        else:
            browser = await launch({'headless': False, 'args': ['--no-sandbox', '--disable-infobars',
                                                               '--proxy-server={}'.format(RedisClient().get()),
                                                               ], })  # 启动pyppeteer 属于内存中实现交互的模拟器
        page = await browser.newPage()  # 启动个新的浏览器页面标签
        await page.setUserAgent(
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36")
        cookies = {}
        try:
            await asyncio.wait_for(page.goto(url), timeout=10.0)  # 访问页面
            # 始终让window.navigator.webdriver=false
            # navigator是windiw对象的一个属性，同时修改plugins，languages，navigator 且让
            # await page.setJavaScriptEnabled(enabled=True)  # 使用 JS 渲染
            await page.evaluate(
                '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')  # 以下为插入中间js，将淘宝会为了检测浏览器而调用的js修改其结果。
            await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
            await page.evaluate(
                '''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
            await page.evaluate(
                '''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')
            await asyncio.wait_for(page.goto(url), timeout=10.0)  # 访问页面
            await asyncio.sleep(2)
        except:
            await page.evaluate('''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
            await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
            await page.evaluate(
                '''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
            await page.evaluate(
                '''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')
            # await page.evaluate('window.open("{}");'.format(url))
            await page.evaluate('window.location="{}";'.format(url))
            # await page.goto(url)  # 访问登录页面
            await asyncio.sleep(2)
        try:
            cookies = await asyncio.wait_for(self.get_cookie(page), timeout=5.0)
        except Exception as e:
            await browser.close()
        finally:
            await browser.close()
        return cookies

    async def get_cookie(self, page):
        # res = await page.content()
        cookies_list = await page.cookies()
        cookies = {}
        for cookie in cookies_list:
            cookies[cookie.get('name')] = cookie.get('value')
        return cookies

    def retry_if_result_none(self, result):
        return result is None

    def input_time_random(self, ):
        return random.randint(100, 151)

    def run(self, url, entityCode=None):
        result = {}
        try:
            # task = asyncio.wait([])
            result = self.loop.run_until_complete(self.main(url, entityCode))  # 将协程注册到事件循环，并启动事件循环
        except Exception as e:
            self.log.info('协程被动结束, chrome关闭')
            for task in asyncio.Task.all_tasks():
                task.cancel()

                self.loop.stop()

                self.loop.run_forever()
        finally:
            self.loop.close()
        return result


class BaseJsEncryptPage(object):

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.log = ICrawlerLog('spider').save

    async def get_cookie(self, page):
        # res = await page.content()
        cookies_list = await page.cookies()
        cookies = {}
        for cookie in cookies_list:
            cookies[cookie.get('name')] = cookie.get('value')
        return cookies

    def work(self, url):
        pass

    def run(self, url, func):
        result = {}
        try:
            # task = asyncio.wait([])
            result = self.loop.run_until_complete(func(url))  # 将协程注册到事件循环，并启动事件循环
        except Exception as e:
            self.log.info('协程被动结束, chrome关闭')
            for task in asyncio.Task.all_tasks():
                task.cancel()
                self.loop.stop()
                self.loop.run_forever()
        finally:
            self.loop.close()
        return result


class GetPageHtml(BaseJsEncryptPage):

    async def change_status(self, page):
        await page.evaluate('''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
        await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
        await page.evaluate(
            '''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
        await page.evaluate(
            '''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')

    async def get_charset(self, page):
        await page.evaluate('''() =>{ var charset = document.charset; return charset; } ''')

    async def request_check(self, req):
        '''请求过滤, 指定类型的请求被处理'''
        if req.resourceType in ['image', 'media', 'eventsource', 'websocket']:
            await req.abort()
        else:
            await req.continue_()

    async def intercept_response(self, res):
        resourceType = res.request.resourceType
        if resourceType in ['image', 'media']:
            resp = await res.text()
            print(resp)

    async def goto(self, page, url):
        for _ in range(5):
            try:
                await page.goto(url, {'timeout': 0, 'waitUntil': 'networkidle0'})
                break
            except (pyppeteer.errors.NetworkError, pyppeteer.errors.PageError) as ex:
                # 无网络 'net::ERR_INTERNET_DISCONNECTED','net::ERR_TUNNEL_CONNECTION_FAILED'
                if 'net::' in str(ex):
                    await asyncio.sleep(10)
                else:
                    raise

    async def work(self, url):
        IP = RedisClient().get()
        browser = await launch({'headless': True, 'timeout': 10,
                                # 'userDataDir': r'./SpiderTools/PythonSpiderChromeLibs',\
                                'args': [
                                    '--no-sandbox',
                                    '--disable-gpu',
                                    '--disable-infobars',
                                    '--proxy-server={}'.format(IP),
                                ], })
        page = await browser.newPage()  # 启动个新的浏览器页面标签
        UA = random.choice(user_agent_list)
        await page.setUserAgent(UA)
        await page.setJavaScriptEnabled(enabled=True)  # 使用 JS 渲染
        # await page.setRequestInterception(True)
        # page.on('request', self.intercept_response)
        data = ''
        charset = 'utf-8'
        try:
            await self.change_status(page)
            await asyncio.wait_for(self.goto(page, url), timeout=10.0)
            # page_ = await browser.pages()  # 获取标签page, pyppeteer 的tag是一个page
            time.sleep(3)
            await self.change_status(page)
            await asyncio.wait_for(page.reload(), timeout=5.0)
            # data = await page.content()
            data = await asyncio.wait_for(page.content(), timeout=5.0)
            await asyncio.sleep(3)
            charset = await page.evaluate('''() =>{ var charset = document.charset; return charset; } ''')
        except Exception as e:
            self.log.info('获取失败')
            pass
        finally:
            await browser.close()
        return data, charset


if __name__ == '__main__':
    url = 'http://www.ip138.com/'
    url_ = 'http://www.jsbchina.cn/CN/kjjr/jrxx/jzcg/xygg/index.html?flag=1'
    referer = 'https://www.spdb.com.cn/web_query/'
    cookies = GetJsEncryptPage().run(referer)
    print(cookies)
