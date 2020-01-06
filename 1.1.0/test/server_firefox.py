
import os, sys
import time, random
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile


curPath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(curPath[:-12])



class FirefoxGetResponse(object):
    """
    返回  (charset: '编码', cookie, html_url: '搜索结果的实体url', response: '具体响应的')
    """
    def __init__(self):
        # self.log = ICrawlerLog('spider').save
        # self.IP = RedisClient().get()
        self.UA = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36'
        option = webdriver.FirefoxOptions()
        # option.add_argument('-headless')  # 启用无头
        option.add_argument("--start-maximized")
        option.add_argument('--no-sandbox')
        option.add_argument('user-agent="{}"'.format(self.UA))
        option.add_argument('--disable-gpu')  # 禁用 GPU 硬件加速，防止出现bug

        # profile = FirefoxProfile()
        # 激活手动代理配置（对应着在 profile（配置文件）中设置首选项）
        # profile.set_preference("network.proxy.type", 1)
        # ip及其端口号配置为 http 协议代理
        # profile.set_preference("network.proxy.http", self.IP.split(':')[0])
        # profile.set_preference("network.proxy.http_port", self.IP.split(':')[-1])
        # 所有协议共用一种 ip 及端口，如果单独配置，不必设置该项，因为其默认为 False
        # profile.set_preference("network.proxy.share_proxy_settings", True)
        # 默认本地地址（localhost）不使用代理，如果有些域名在访问时不想使用代理可以使用类似下面的参数设置
        # profile.set_preference("network.proxy.no_proxies_on", "localhost")
        # self.browser = webdriver.Firefox(options=option)
        # self.browser = webdriver.Firefox(options=option, firefox_profile=profile, firefox_binary='C:\Program Files\Mozilla Firefox/firefox.exe')
        self.browser = webdriver.Firefox(options=option, log_path=os.path.devnull,firefox_binary='C:\Program Files\Mozilla Firefox/firefox.exe')
        self.browser.maximize_window()
        # self.browser.get('https://www.baidu.com/?tn=22073068_3_oem_dg')
        self.browser.set_page_load_timeout(60)
        self.browser.set_script_timeout(60)  # 这两种设置都进行才有效

    def changeWebdriver(self, browser):
        # 设置 webdriver 属性
        browser.execute_script('''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
        browser.execute_script('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
        browser.execute_script('''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
        browser.execute_script('''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')

    def work(self, url):
        cookie = {}
        html_url = ''
        response = ''
        charset = 'utf-8'
        # 打开网页
        try:
            self.changeWebdriver(self.browser)
            # self.browser.execute_script('window.open("{}");'.format('https://www.baidu.com/?tn=22073068_3_oem_dg'))
            time.sleep(3)
            js = 'window.open("{}");'.format(url)
            self.changeWebdriver(self.browser)
            self.browser.execute_script(js)
            time.sleep(9)
            self.changeWebdriver(self.browser)

            handles = self.browser.window_handles
            if len(handles) > 4:
                raise ValueError

            self.browser.refresh()

            # 切换到第三个窗口（最后一个）
            self.browser.switch_to_window(self.browser.window_handles[-1])

            # 整个页面html
            response = self.browser.page_source
            # 获取cookies逻辑
            if self.browser.get_cookies():
                for i in self.browser.get_cookies():
                    cookie[i["name"]] = i["value"]
            # 获取当前页面url
            html_url = self.browser.current_url
            # charset
            charset = self.browser.execute_script('return document.charset;')

        except Exception as e:
            pass
            # self.log(f'selenium直接获取数据异常异常终止, {e}')
        finally:
            self.browser.close()
            self.browser.quit()
        # print(response)
        return (charset, cookie, html_url, response, self.UA)


if __name__ == '__main__':

    url = 'http://www.abchina.com/cn/PersonalServices/SvcBulletin/default_1.htm'

    charset, cookie, html_url, response, UA = FirefoxGetResponse().work(url)
    print(charset, cookie, html_url, response, UA)
