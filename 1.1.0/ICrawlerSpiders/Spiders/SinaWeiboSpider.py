import json
import re

import requests
import time
import random
import jsonpath

from Env.parse_yaml import FileConfigParser
from OperateDB.conn_redis import  RedisClient
from SpiderTools.pdf import user_agent
from SpiderTools.tool import Download, get_base64, platform_system
from SpidersLog.icrwler_log import ICrawlerLog
from OperateDB.conn_mongodb import Op_MongoDB
from TemplateMiddleware.content_midlewares import Content_Middleware
from staticparm import root_path


cookies_list = [
    '{"SUB": "_2A25w4AyYDeRhGeRK61cX8ybJyDuIHXVTlHlQrDV8PUNbmtBeLUegkW9NU3mQIHSQjMkg7pBbG5kGNk1QWGD48RRV"}',
    '{"SUB": "_2A25xmZ64DeRhGeBH61MU9CnJwzSIHXVTZSLwrDV6PUJbkdAKLRD6kW1NQcj3mmz71co9kqauPUVBpMsnTQZZDaEZ"}',
    '{"SUB": "_2A25w4Md-DeRhGeFN71YS8izKyD6IHXVTl7-2rDV8PUNbmtBeLVHZkW9NQDUQOR34l0lstuLxNqBVSpBJrnMc-FMD"}',
    '{"SUB": "_2A25w4MziDeRhGeFN71YS8i3Myz6IHXVTl7kqrDV8PUNbmtBeLVfAkW9NQDUQ_GH9C67gC0EPg513qu4bcybTX4Ib"}',
    '{"SUB": "_2A25w4M1NDeRhGeFN71YX8C7IzDuIHXVTl7mFrDV8PUNbmtBeLW7ykW9NQDUQ9jnneh6qf_xmXJHcevJRo31udEU4"}',
    '{"SUB": "_2A25w4M0jDeRhGeFN71YS8izLzjmIHXVTl7nrrDV8PUNbmtBeLVDZkW9NQDUQw3eRQzQ4SGZqCLCaphe7cjqxTpYS"}',
    '{"SUB": "_2A25w4M2aDeRhGeFN71YX8C7PwjiIHXVTl7hSrDV8PUNbmtBeLVOtkW9NQDUQ43OoEL3ll0ty51Ai2055v1FqtLNJ"}',
    '{"SUB": "_2A25w4bvJDeRhGeFN71YX8C7KyzSIHXVTlqoBrDV8PUNbmtBeLUmkkW9NQDUQgC1v13N7f1Vei1AkJMuB_uR6AqPj"}',
    '{"SUB": "_2A25w4bxzDeRhGeFN71YS8i3MzzuIHXVTlqq7rDV8PUNbmtBeLVn7kW9NQDUQ9C3V8cllyeNWjHkahHFdxcVUktf_"}',
    '{"SUB": "_2A25w4bwkDeRhGeFN71YX8C7LwjiIHXVTlqrsrDV8PUNbmtBeLXfSkW9NQDUQv36Nyp093ZQ2SKdcFAO5hka6VpVC"}',
    '{"SUB": "_2A25w4bzpDeRhGeFN71YS8i3PwzWIHXVTlqkhrDV8PUNbmtBeLVL4kW9NQDUQs2DZ2oNRX9suG1_Ahtt-wnunBqpA"}',
    '{"SUB": "_2A25w4b1XDeRhGeFN71YS8i3IzD2IHXVTlqmfrDV8PUNbmtBeLU2ikW9NQDURRZXpiXGvfKliYycm0zAKLt4whTUj"}',
    '{"SUB": "_2A25w4b0FDeRhGeFN71YX8C7Ezj-IHXVTlqnNrDV8PUNbmtBeLVTXkW9NQDUQtECA2kF3yYLHmXj1tnIYyht58IEI"}',
    '{"SUB": "_2A25w4b3KDeRhGeFN71YS8i3PyD6IHXVTlqgCrDV8PUNbmtBeLXWskW9NQDUQvStT-gJwcsPPblMbh9Sc9boKwCsQ"}',
    '{"SUB": "_2A25w4b2MDeRhGeFN71YS8izEyTyIHXVTlqhErDV8PUNbmtBeLU_9kW9NQDUQ2pjt-6U9mUwU2UjobKXYJI2BALWO"}',
    '{"SUB": "_2A25w4b52DeRhGeFN71YX8C7KwjuIHXVTlqi-rDV8PUNbmtBeLXDykW9NQDUQkS6pG12BrTW9lcc_VbsVwfki3J6T"}',
    '{"SUB": "_2A25w4b4qDeRhGeFN71YS8i3Jzj6IHXVTlqjirDV8PUNbmtBeLRDhkW9NQDURWCIiXC0SJzZrxfJds_Qqvei3PUpK"}',
]


class WeiBoSpider:

    name = 'weibo'

    def __init__(self, url, entity_code, entity_name, *args, **kwargs):
        """
        定义参数
        :param code_: code
        :param url_: 入口url
        :param args:
        :param kwargs:
        """
        super(WeiBoSpider, self).__init__(*args, **kwargs)
        self.code_ = entity_code
        self.url = url
        self.entity_name = entity_name
        self.conn = Op_MongoDB().conn_mongo()

        self.basic_info_mongodb = Op_MongoDB(db='spider_data', coll='WEIBOBASICINFO', key='null', conn=self.conn)
        self.info_mongodb = Op_MongoDB(db='spider_data', coll='WEIBOINFO', key='null', conn=self.conn)

        # 需要遍历的url
        self.comments_url = 'https://m.weibo.cn/comments/hotflow'          # 评论
        self.content_url = 'https://m.weibo.cn/statuses/extend'            # 微博内容主体
        self.main_url = 'https://m.weibo.cn/api/container/getIndex'       # 主页
        self.company_url = 'https://m.weibo.cn/u/'

        self.log = ICrawlerLog('spider').save

    def ip_proxy(self):
        log = ICrawlerLog(name='spider').save
        try:
            ip = RedisClient().get()
            log.info('当前使用ip为%s' % ip)
            proxies = {
                       'http': 'http://' + ip,
                       'https': 'https://' + ip
                       }
            return proxies
        except Exception as e:
            log.error(e.args)
            print(6)
            return False

    def query_code(self):
        """
        通过微博账号来查询数据
        :param code: 微博账号
        :return:
        """

        mid_data = ['WeiBo.CONTENT', 'WeiBo.CONTENT1']
        try:
            middle_main = Content_Middleware(mid_data[0]).Invoking_Diff()
        except:
            middle_main = None
        if middle_main:
            self.log.info('地址中间件程序执行成功')
            main_urls = middle_main[0].get('url')
            if main_urls:
                main_url = main_urls[0]
            else:
                main_url = self.main_url
        else:
            self.log.error('地址中间件执行异常')
            main_url = self.main_url
        # 微博的用户code
        weibo_code = self.url.split('?')[0].split('/')[-1]
        # weibo_code = '3207936915'
        param_top = {
            'type': 'uid',
            'value': str(weibo_code),
            # 'containerid': '1076032248803312',
        }

        # 微博基本资料信息
        microblog_basic_infor = dict()

        # 主页/微博/照片的containerids
        containerids = dict()
        # time.sleep(random.uniform(1, 3))
        try:
            time.sleep(random.randint(1, 2))
            if self.code_ == 'PABCCMICROBLOG':
                cookies = {
                'SUB':'_2A25xmZ64DeRhGeBH61MU9CnJwzSIHXVTZSLwrDV6PUJbkdAKLRD6kW1NQcj3mmz71co9kqauPUVBpMsnTQZZDaEZ',
                'SUHB':'09Pt2j5xf9wMmP',
                'SCF':'AjDPkdKjX8tRnAkAYQMh6JAYckuOEg1PHvK6g_XVWJHhevpTUDvx6djEkofPBy732wftibta7H8DsuIXn3G0xrk.',
                '_T_WM':'94688994739',
                'MLOGIN':'1',
                'XSRF-TOKEN':'8fd3eb',
                'WEIBOCN_FROM':'1110006030',
                'M_WEIBOCN_PARAMS':'luicode%3D20000174%26uicode%3D20000174'
                }
                # cookies = {'SUB': '_2A25xn2OADeRhGeBH61MU9CvPwjSIHXVTYA3IrDV6PUJbkdAKLW34kW1NQcj2sDsjjPPYj1FPYLvQORExlm3mffRx', }
                # 获取 XSRF-TOKEN
                resp = requests.get('https://m.weibo.cn/api/config', headers={'User-Agent': random.choice(user_agent)}, cookies=cookies, allow_redirects=False)
                XSRF_TOKEN = resp.json().get('data').get('st')
                cookies['XSRF-TOKEN'] = XSRF_TOKEN
                header = {
                    'User-Agent': random.choice(user_agent),
                    'x-xsrf-token': XSRF_TOKEN,
                    'x-requested-with': 'XMLHttpRequest',
                }
                res_m = requests.get(url=main_url, params=param_top, proxies=self.ip_proxy(), cookies=cookies, headers=header, timeout=20, allow_redirects=False)
            else:
                res_m = requests.get(url=main_url, params=param_top,proxies=self.ip_proxy(),
                                    headers={'User-Agent':random.choice(user_agent)}, timeout=20, allow_redirects=False)

        except Exception as e:
            # print(e.args)
            self.log.error('微博首页请求失败！')
            return False
        # print(res_m.text)
        microblog_basic_infor['MAIN_URL_'] = 'https://m.weibo.cn/u/' + weibo_code
        res_main = res_m.json()
        if res_main.get('ok') == 1:
            try:
                microblog_basic_infor['WEIBO_CODE_'] = str(weibo_code)
                microblog_basic_infor['NAME_'] = jsonpath.jsonpath(res_main, 'data.userInfo.screen_name')[0]
                microblog_basic_infor['FOCUS_'] = jsonpath.jsonpath(res_main, 'data.userInfo.follow_count')[0]
                microblog_basic_infor['REPLIER_HEAD_'] = jsonpath.jsonpath(res_main, 'data.userInfo.avatar_hd')[0]
                # 获取: 星标 地址, 简介
                microblog_basic_infor['VIRIFIED_'] = \
                    jsonpath.jsonpath(res_main, '$..verified_reason')[0] if self.code_ == 'PABCCMICROBLOG' else ''
                microblog_basic_infor['BIREF_'] = \
                    jsonpath.jsonpath(res_main, '$..description')[0] if self.code_ == 'PABCCMICROBLOG' else ''
                microblog_basic_infor['LOCATION_'] = '北京'
                # verified 是否为星标用户
                microblog_basic_infor['VERIFIED_'] = jsonpath.jsonpath(res_main, '$..verified')[0]
                microblog_basic_infor['FANS_'] = jsonpath.jsonpath(res_main, 'data.userInfo.followers_count')[0]
                #  主页信息
                containerids['home_page_containerid'] = jsonpath.jsonpath(res_main, 'data.tabsInfo.tabs[0].containerid')[0]
                # 评论信息
                containerids['microblog_containerid'] = jsonpath.jsonpath(res_main, 'data.tabsInfo.tabs[1].containerid')[0]
                # 获取图片
                containerids['image_containerid'] = jsonpath.jsonpath(res_main, 'data.tabsInfo.tabs[2].containerid')[0]
            except Exception as e:
                self.log.error('内容匹配错误')
                return False

            # 所属公司请求数据
            if self.code_ != 'PABCCMICROBLOG':
                param_company = {
                    'type': 'uid',
                    'value': str(weibo_code),
                    'containerid': containerids['home_page_containerid'],
                }
                try:
                    time.sleep(random.randint(1, 3))
                    # cookies = json.loads(RedisClient(name='weibo_cookies').get())
                    cookies = json.loads(random.choice(cookies_list))
                    res_c = requests.get(url=main_url, params=param_company, proxies=self.ip_proxy(), cookies=cookies, headers={'User-Agent':random.choice(user_agent)}, timeout=20, allow_redirects=False)
                    microblog_basic_infor['COMPANY_URL_'] = res_c.url
                    res_company = res_c.json()
                except:
                    res_company = None
                    self.log.error('微博公司网页请求错误！')
                try:
                    # 获取微博公司全称
                    microblog_basic_infor['COMPANY_'] = jsonpath.jsonpath(res_company, 'data.cards.0..card_group.1.item_content')[0]
                except Exception as e:
                    self.log.error('内容匹配错误' + e)
            else:
                microblog_basic_infor['COMPANY_'] = '中国平安银行'
                microblog_basic_infor['COMPANY_URL_'] = "https://m.weibo.cn/api/container/getIndex?type=uid&value=2248803312&containerid=2302832248803312"
            # 详细资料请求数据
            param_basic_information = {
                'containerid': '{}_-_INFO'.format(containerids.get('home_page_containerid')),
            }
            if self.code_ != 'PABCCMICROBLOG':
                try:
                    time.sleep(random.randint(1, 3))
                    # cookies = json.loads(RedisClient(name='weibo_cookies').get())
                    cookies = json.loads(random.choice(cookies_list))
                    res_m_b_i = requests.get(url=main_url, params=param_basic_information, cookies=cookies, headers={'User-Agent':random.choice(user_agent)}, proxies=self.ip_proxy(), timeout=20, allow_redirects=False)
                except:
                    self.log.error('内容匹配错误')
                    return False
                microblog_basic_infor['DETAILED_URL_'] = res_m_b_i.url
                res_microblog_basic_information = res_m_b_i.json()
                if res_microblog_basic_information:
                    try:
                        microblog_basic_infor['VIRIFIED_'] = jsonpath.jsonpath(res_microblog_basic_information, '$.data.cards.0.card_group.2.item_content')[0]
                        microblog_basic_infor['BIREF_'] = jsonpath.jsonpath(res_microblog_basic_information, '$.data.cards.0.card_group.3.item_content')[0]
                        microblog_basic_infor['LOCATION_'] = jsonpath.jsonpath(res_microblog_basic_information, '$.data.cards.1.card_group.1.item_content')[0]
                    except Exception as e:
                        self.log.error('内容匹配错误')
                        return False

            # 保存基本资料信息
            microblog_basic_infor['ENTITY_NAME_'] = self.entity_name
            microblog_basic_infor['ENTITY_CODE_'] = self.code_
            microblog_basic_infor['DEALTIME_'] = time.time()
            # 定位元素传入参数(字典)
            main_position_ele = dict()
            main_position_ele['WEIBO_CODE_'] = str(weibo_code)
            self.updata_info(self.basic_info_mongodb, main_position_ele, microblog_basic_infor)
            self.log.info('{}新浪微博基本资料存储完成!'.format(microblog_basic_infor.get('NAME_')))
            # print('{}新浪微博基本资料存储完成!'.format(microblog_basic_infor.get('NAME_')))

            # 微博动态信息
            page_content = ''  # 第一页
            while True:
                # print(containerids.get('microblog_containerid'))
                param_microblog = {
                    'containerid': '{}'.format(containerids.get('microblog_containerid')),
                    'since_id': str(page_content)
                }
                try:
                    time.sleep(random.randint(1, 3))
                    # cookies = json.loads(RedisClient(name='weibo_cookies').get())
                    cookies = json.loads(random.choice(cookies_list))
                    res_mic = requests.get(url=main_url, params=param_microblog, cookies=cookies, proxies=self.ip_proxy(),headers={'User-Agent':random.choice(user_agent)}, timeout=20, allow_redirects=False)
                except Exception as e:
                    return False
                res_microblog = res_mic.json()
                # 每一页最多有20条数据
                for count_content in range(21):
                    # 第一条
                    count_content += 1
                    contents = []
                    content_info = dict()
                    # print(count_content, '条')
                    try:
                        try:
                            # 转发
                            content_info['RELAYS_'] = \
                            jsonpath.jsonpath(res_microblog, 'data.cards.{}.mblog.reposts_count'.format(count_content))[0]
                            # 点赞
                            content_info['PRAISES_'] = \
                            jsonpath.jsonpath(res_microblog, 'data.cards.{}.mblog.attitudes_count'.format(count_content))[0]
                            # 评论
                            content_info['REPLIES_'] = \
                            jsonpath.jsonpath(res_microblog, 'data.cards.{}.mblog.comments_count'.format(count_content))[0]
                            # 原创 & 转载
                            content_info['OWN_'] = \
                                '原创' if jsonpath.jsonpath(res_microblog, 'data.cards.{}.mblog.retweeted_status'.format(count_content)) else '转载'
                        except:
                            continue

                        # 处理内容图片
                        content_img_num = 0
                        content_img_list = []
                        # print('four')
                        while True:
                            try:
                                content_img = jsonpath.jsonpath(res_microblog, 'data.cards.{}.mblog.pics.{}.url'.format(count_content, content_img_num))
                                if content_img:
                                    # content_img = [self.deal_img_base64(content_img[0])]
                                    content_img_list += content_img
                                    content_img_num += 1
                                else:
                                    break
                            except Exception as e:
                                self.log.error(e.args)
                                break

                        content_info['CONTENT_IMAGES_'] = content_img_list
                        # print(content_info)

                        # 发布时间
                        u_time_= \
                            jsonpath.jsonpath(res_microblog, 'data.cards.{}.mblog.created_at'.format(count_content))[0]
                        content_info['PUBLISH_TIME_'] = self.format_time(str(u_time_))
                        # 评论/留言comments_id
                        comments_id = \
                            jsonpath.jsonpath(res_microblog, 'data.cards.{}..mblog.id'.format(count_content))[0]
                        try:
                            time.sleep(random.randint(1, 3))
                            # cookies = json.loads(RedisClient(name='weibo_cookies').get())
                            cookies = json.loads(random.choice(cookies_list))
                            res_content = requests.get(url=self.content_url + '?id=' + comments_id, proxies=self.ip_proxy(), cookies=cookies, headers={'User-Agent':random.choice(user_agent)}, timeout=20, allow_redirects=False).json()
                        except Exception as e:
                            # 内容请求失败，继续下一条信息！
                            continue
                        try:
                            text_content = \
                                jsonpath.jsonpath(res_content, 'data.longTextContent')[0]
                            from scrapy.selector import Selector
                            content_info['CONTENT_'] = ''.join(Selector(text=text_content).xpath('//text()').extract())
                        except Exception as e:
                            # 没有内容，继续下一条信息！
                            continue
                        content_info['CONTENT_CODE_'] = comments_id
                        content_info['CONTENT_URL_'] = 'https://m.weibo.cn/detail/' + comments_id

                        # 处理评论信息 , 获取评论
                        self.session = requests.Session()
                        cookies = {'SUB': '_2A25xn2OADeRhGeBH61MU9CvPwjSIHXVTYA3IrDV6PUJbkdAKLW34kW1NQcj2sDsjjPPYj1FPYLvQORExlm3mffRx',}
                        # cookies = json.loads(RedisClient(name='weibo_cookies').get())
                        self.session.cookies = requests.utils.cookiejar_from_dict(cookies)
                        # 获取 XSRF-TOKEN
                        resp = self.session.get('https://m.weibo.cn/api/config', headers={'User-Agent':random.choice(user_agent)}, allow_redirects=False)
                        XSRF_TOKEN = resp.json().get('data').get('st')
                        cookies['XSRF-TOKEN'] = XSRF_TOKEN
                        header = {
                            'User-Agent': random.choice(user_agent),
                            'x-xsrf-token': XSRF_TOKEN,
                            'x-requested-with': 'XMLHttpRequest',
                        }
                        # 新的类型请求, 更换新的cookies
                        self.session.headers = header
                        self.session.cookies = requests.utils.cookiejar_from_dict(cookies)
                        comments_results = []
                        comments_results, max_id = self.comments_data(comments_results, comments_id, cookies, header)
                        if not comments_results and comments_results != []:
                            return False
                        # 反复回调,拿到所有的评论信息
                        while max_id:
                            comments_results, max_id = self.comments_data(comments_results, comments_id, cookies, header, max_id)
                        # print(comments_results)
                        content_info['INFO_COMMENTS_'] = comments_results
                        # 将评论信息汇总到该文章下
                        contents.append(content_info)
                        # 数据存储
                        for i in contents:
                            i['ENTITY_NAME_'] = self.entity_name
                            i['BANK_CODE_'] = self.code_
                            i['DEALTIME_'] = time.time()
                            # 内容定位元素
                            content_position_ele = dict()
                            content_position_ele['CONTENT_CODE_'] = i.get('CONTENT_CODE_')
                            self.updata_info(self.info_mongodb, content_position_ele, i)
                        # print('{}条微博存储完成'.format(count_content+1))
                        if content_info:
                            continue
                    except Exception as e:
                        self.log.error(e)
                        break
                try:
                    page_content = jsonpath.jsonpath(res_microblog, 'data.cardlistInfo.since_id')[0]
                except Exception as e:
                    self.log.error(e)
                    # page_content = None
                    break
                print(page_content)
            self.log.info('{}爬取成功！'.format(self.entity_name))
            return True
        else:
            self.log.error('{}的账号不存在或者异常,数据无法抓取!'.format(self.entity_name))
            return False

    def comments_data(self, comments_results, comments_id, cookies, header, max_i=0):
        """
        处理当页评论/留言信息（一页有10~20条评论信息）
        :param comments_dict: 内容数据
        :param comments_id: 内容状态id
        :param max_id: 页码(为0时为最后一页,页码是'138830612324215'字段)
        :return:
        """
        try:
            print(max_i)
            time.sleep(random.randint(1, 3))
            # cookies = json.loads(RedisClient(name='weibo_cookies').get())
            cookies = json.loads(random.choice(cookies_list))
            proxies = self.ip_proxy()
            if int(max_i) == 0:
                res_com = requests.get(
                    url='https://m.weibo.cn/comments/hotflow?id={0}&mid={0}&max_id_type=0'.format(comments_id),
                    proxies=proxies, cookies=cookies, timeout=20, allow_redirects=False)
            else:
                res_com = requests.get(
                    url='https://m.weibo.cn/comments/hotflow?id={0}&mid={0}&max_id={1}&max_id_type=0'.format(
                        comments_id, max_i), proxies=proxies, cookies=cookies, timeout=20, allow_redirects=False)

            if res_com.status_code == 200:
                res_com = res_com.json()
        except Exception as e:
            self.log.error(e)
            return comments_results, 0

        # 分页id
        try:
            if res_com['ok'] == 1:
                max_i = jsonpath.jsonpath(res_com, 'data.max_id')[0]
            else:
                return comments_results, 0
        except Exception as e:
            self.log.error(e)
            # max_id赋值为0,停止请求
            max_i = 0
        count_comments = 0

        while True:
            comments_dict = dict()
            try:
                comm_text = \
                    jsonpath.jsonpath(res_com, 'data.data.{}.text'.format(count_comments))[0]
                from scrapy.selector import Selector
                comments_dict['COMMENT_'] = ''.join(Selector(text=comm_text).xpath('//text()').extract())

                REPLIER_TIME_ = \
                    jsonpath.jsonpath(res_com, 'data.data.{}.created_at'.format(count_comments))[0]
                comments_dict['REPLIER_TIME_'] = self.cst_to_str(str(REPLIER_TIME_))
                # 头像
                src = jsonpath.jsonpath(res_com, 'data.data.{}.user.avatar_hd'.format(count_comments))[0]
                comments_dict['REPLIER_HEAD_'] = self.deal_img_base64(src=src)

                comments_dict['REPLIER_PRAISES_'] = \
                    jsonpath.jsonpath(res_com, 'data.data.{}.like_count'.format(count_comments))[0]

                comments_dict['REPLIER_'] = \
                    jsonpath.jsonpath(res_com, 'data.data.{}.user.screen_name'.format(count_comments))[0]

                comments_dict['REPLIER_REPLIES_'] = \
                    jsonpath.jsonpath(res_com, 'data.data.{}.total_number'.format(count_comments))[0]
                comments_dict['VERIFIED_'] = \
                    jsonpath.jsonpath(res_com, 'data.data.{}.user.verified'.format(count_comments))[0]

                comments_dict['TEXT_IMG_'] = \
                    jsonpath.jsonpath(res_com, 'data.data.{}.user.pic.url'.format(count_comments))
                if comments_dict:
                    comments_results.append(comments_dict)
                    count_comments += 1
            except Exception as e:
                self.log.error(e)
                break
        return comments_results, max_i

    def updata_info(self, mongod, elem_dict, item):
        """
         数据去重保存
        :param mongod:  collections
        :param elem_dict: 定位元素(字典)
        :param item: 需要存储的数据(json格式)
        :return:
        """

        try:
            mongod.conn_db_coll().update(elem_dict, {"$set": item}, True)
        except Exception as e:
            self.log.error(e)
            self.log.error('mongodb数据库数据存储异常!')
        finally:
            self.conn.close()

    def save_data(self, mongod, results):
        """
        :param results: 微博基本资料和微博内容及评论
        :return:
        """
        try:
            mongod.I_Mongodb(results)
        except Exception as e:
            self.log.error(e)
            self.log.error('mongodb数据库数据存储异常!')
        finally:
            self.conn.close()

    def format_time(self,d_time):
        """
        格式化发布时间
        :param d_time:
        :return:
        """
        try:
            if re.match('\d+?-\d+?', d_time) and len(d_time) <= 5:
                data_time = time.strftime('%Y-', time.localtime()) + d_time
            elif re.match('^\d+?-\d+?-\d+?', d_time) and 8 <= len(d_time) <= 10:
                data_time = d_time
            else:
                data_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        except Exception as e:
            self.log.error(e)
            data_time = d_time
        return data_time

    def cst_to_str(self, cstTime):
        """
        格式化评论时间
        :param cstTime:
        :return:
        """
        try:
            tempTime = time.strptime(cstTime, '%a %b %d %H:%M:%S +0800 %Y')
            resTime = time.strftime('%Y-%m-%d %H:%M:%S', tempTime)
            return resTime
        except:
            return cstTime

    def deal_img_base64(self, src):
        import os
        try:
            img_dir = FileConfigParser().get_path(server=platform_system(), key='sinaimg')
            img_dir = root_path + img_dir
            img_name = src.split('/')[-1].replace('?', '').replace('#', '').replace('=', '.')
            Download(src, img_dir, img_name)
            img_base64 = get_base64(img_dir, img_name)
            os.remove(img_dir + img_name)
            return img_base64
        except Exception as e:
            self.log.error(e.args)
            return src









