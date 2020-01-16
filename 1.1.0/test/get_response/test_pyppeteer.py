import asyncio
import random

from pyppeteer import launch
from pyquery import PyQuery as pq

# async def main():
#     browser = await launch()
#     page = await browser.newPage()
#     await page.goto('http://quotes.toscrape.com/js/')
#     doc = pq(await page.content())
#     print('Quotes:', doc('.quote').length)
#     await browser.close()
#
# if __name__ == '__main__':
#
#     asyncio.get_event_loop().run_until_complete(main())


class GetJsEncryptPage():
    def __init__(self):
        self.loop = asyncio.get_event_loop()

    async def main(self, url, ):  # 定义main协程函数，
        # 以下使用await 可以针对耗时的操作进行挂起
        browser = await launch({'headless': True, 'args': ['--no-sandbox', '--disable-infobars',
                                                                # '--proxy-server={}'.format(get_ip()),
                                                                ],})  # 启动pyppeteer 属于内存中实现交互的模拟器
        page = await browser.newPage()  # 启动个新的浏览器页面标签
        await page.setUserAgent("Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36")
        cookies = {}
        try:
            await page.goto(url)  # 访问页面
            # 始终让window.navigator.webdriver=false
            # navigator是windiw对象的一个属性，同时修改plugins，languages，navigator 且让
            # await page.setJavaScriptEnabled(enabled=True)  # 使用 JS 渲染
            await page.evaluate('''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')  # 以下为插入中间js，将淘宝会为了检测浏览器而调用的js修改其结果。
            await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
            await page.evaluate('''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
            await page.evaluate('''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')
            await page.goto(url)  # 访问页面
            # content = await page.content()  # 获取页面内容
            await asyncio.sleep(2)
        except:
            await page.evaluate('''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
            await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
            await page.evaluate('''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
            await page.evaluate('''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')
            # await page.evaluate('window.open("{}");'.format(url))
            await page.evaluate('window.location="{}";'.format(url))
            # await page.goto(url)  # 访问登录页面
        try:
             cookies = await self.get_cookie(page)
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
            cookies[cookie.get('name')] =  cookie.get('value')
        return cookies

    def run(self, url, func):
        result = {}
        try:
            # task = asyncio.wait([])
            result = self.loop.run_until_complete(func(url))  # 将协程注册到事件循环，并启动事件循环
        except Exception as e:
            for task in asyncio.Task.all_tasks():
                task.cancel()
                self.loop.stop()
                self.loop.run_forever()
        # self.loop.close()
        return result
