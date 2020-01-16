import asyncio
import random

import pyppeteer
import os

from ICrawlerSpiders.useragent import user_agent_list
from OperateDB.conn_redis import RedisClient

# 有点击的情况代码示例
# await page.goto(url)
# # 输入Gmail
# await page.type('#identifierId', username)
# # 点击下一步
# await page.click('#identifierNext > content')
# page.mouse  # 模拟真实点击
# time.sleep(10)
# # 输入password
# await page.type('#password input', password)
# # 点击下一步
# await page.click('#passwordNext > content > span')
# page.mouse  # 模拟真实点击
# time.sleep(10)
# # 点击安全检测页面的DONE
# # await page.click('div > content > span')#如果本机之前登录过，并且page.setUserAgent设置为之前登录成功的浏览器user-agent了，
# # 就不会出现安全检测页面，这里如果有需要的自己根据需求进行更改，但是还是推荐先用常用浏览器登录成功后再用python程序进行登录。
#
# # 登录成功截图
# await page.screenshot({'path': './gmail-login.png', 'quality': 100, 'fullPage': True})
# # 打开谷歌全家桶跳转，以Youtube为例
# await page.goto('https://www.youtube.com')
# time.sleep(10)


os.environ['PYPPETEER_CHROMIUM_REVISION'] = '588429'
pyppeteer.DEBUG = True


class PyppeteerGetResponse(object):
    def __init__(self):
        pass

    async def get_cookie(self, page):
        # res = await page.content()
        cookies_list = await page.cookies()
        cookies = {}
        for cookie in cookies_list:
            cookies[cookie.get('name')] = cookie.get('value')
        return cookies


    async def main(self,url = 'https://news.163.com/20/0107/19/F2AF0CER00018AOR.html'):
        # print("in main ")
        # print(os.environ.get('PYPPETEER_CHROMIUM_REVISION'))
        # ip = RedisClient().get()

        # 设置无头和代理
        browser = await pyppeteer.launch({'headless': True, 'timeout': 20,
                                    'args': [
                                        '--no-sandbox',
                                        '--disable-gpu',
                                        '--disable-infobars',
                                        # '--proxy-server={}'.format(ip),
                                    ], })
        page = await browser.newPage()
        # 设置ua
        await page.setUserAgent(random.choice(user_agent_list))
        # 访问页面
        await page.goto(url)
        content = await page.content()         # 页面
        url = page.url                         # url
        cookies = await self.get_cookie(page)  # cookie
        # await page.screenshot({'path': 'example.png'})
        await browser.close()
        return {'content': content, 'cookies': cookies, 'url': url}

    def run(self,):
        loop = asyncio.get_event_loop()
        task = asyncio.ensure_future(self.main())
        loop.run_until_complete(task)
        return task.result()


if __name__ == '__main__':

    print(PyppeteerGetResponse().run())
