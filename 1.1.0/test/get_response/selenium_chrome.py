import time

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

# from SpiderTools.tool import SpiderException,ResponseHTML, wash_url

# from SpiderTools.chrome_ip import create_proxyauth_extension
# from SpidersLog.icrwler_log import ICrawlerLog



class ChromeGetResponse(object):

    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

    d = DesiredCapabilities.CHROME
    d['loggingPrefs'] = {'performance': 'ALL'}

    def __init__(self, ):
        # 浏览器初始化
        option = webdriver.ChromeOptions()
        option.add_argument("--start-maximized")
        # 暂时不用代理
        option.add_argument('--headless')
        option.add_argument('--disable-gpu')  # 禁用 GPU 硬件加速，防止出现bug
        # 禁止图片加载
        prefs = {"profile.managed_default_content_settings.images": 2}
        option.add_experimental_option("prefs", prefs)
        option.add_argument('user-agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"')
        # self.proxy = RedisClient().get()
        # print(self.proxy)

        # 设置代理方式一：
        # option.add_argument('--proxy-server=http://{}'.format(self.proxy))
        # /home/spiderjob/domain/tools/chromedriver
        # self.browser = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver", chrome_options=option)  # 创建实例
        # self.browser = webdriver.Chrome(executable_path="/home/spiderjob/domain/tools/chromedriver", chrome_options=option)  # 创建实例
        self.browser = webdriver.Chrome(executable_path=r"C:\Users\lyial\Desktop\coffee\venv/chromedriver", chrome_options=option)  # 创建实例

        # 设置代理方式二：
        # proxyauth_plugin_path = create_proxyauth_extension(
        #     proxy_host="XXXXX.com",
        #     proxy_port=9020,
        #     proxy_username="XXXXXXX",
        #     proxy_password="XXXXXXX"
        # )
        # option.add_extension(proxyauth_plugin_path)  # 设置代理
        # self.browser = webdriver.Chrome(chrome_options=option)
        self.wait = WebDriverWait(self.browser, 60)
        # self.wait = wait.WebDriverWait(self.browser, 60)
        self.browser.get('https://www.baidu.com/?tn=22073068_3_oem_dg')
        # self.browser.get('https://per.spdb.com.cn')

    def run_request(self,  url, code_='0', page='0'):
        '''
        下载网页, 只要返回HTTPResponse就不再执行其他下载中间件
        :param request: scrapy整合的全局参数
        :param spider: spiders里的爬虫对象
        :return:
        '''
        # log = ICrawlerLog(name='spider').save
        # 新打开一个标签页, 访问新网址, 跳到当前页, 获取数据, 关闭当前页面, 回到原始页
        try:
            # view_url = wash_url(url)
            view_url = url
            # js_list = [
            #            # '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''',
            #            r"Object.defineProperty(navigator, 'webdriver', {get: () => undefined,});",
            #            r'''window.navigator.chrome = { runtime: {},  }; ''',
            #            r'''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''',
            #            r'''Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });''',
            #            # r"() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5, 6],}); }",
            #            r"Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5, 6],});",
            #
            #            ]
            # for js in js_list:
            #     self.browser.execute_script(js)
            # 访问目标网页
            js = 'window.open("{}");'.format(view_url)
            # time.sleep(2)
            self.browser.execute_script(js)

            handles = self.browser.window_handles
            print(handles)
            if len(handles) > 4:
                raise Exception('网络错误, 请重启')
                # log.error('浏览器请求异常,请检查网络')
                # raise SpiderException('网络错误, 请重启')

            # for handle in handles:  # 切换窗口
            #     if handle != self.browser.current_window_handle:
            #         self.browser.switch_to_window(handle)
            #         break
            self.browser.implicitly_wait(3)
            self.browser.switch_to_window(self.browser.window_handles[-1])

            # 获取cookies
            target_cookie = {}
            cookies = self.browser.get_cookies()
            for cookie in cookies:
                target_cookie[cookie["name"]] = cookie["value"]

            # 获取url
            html_url = self.browser.current_url
            # 获取response
            response_result = self.browser.page_source
            self.browser.close()
            self.browser.quit()
            return html_url,response_result,target_cookie
        except:
            self.run_request(url)
            if len(handles) > 4:
                # log.error('浏览器请求异常,请检查网络')
                # raise SpiderException('网络错误, 请重启')
                raise Exception('网络错误, 请重启')
            # log.error('响应超时')


if __name__ == '__main__':
    html_url, response_result, target_cookie = ChromeGetResponse().run_request('http://www.pbc.gov.cn/goutongjiaoliu/113456/113469/index.html')
    print(html_url,response_result,target_cookie)