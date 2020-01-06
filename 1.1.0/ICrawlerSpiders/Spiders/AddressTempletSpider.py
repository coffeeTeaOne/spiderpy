# encoding: utf-8
from scrapy.spidermiddlewares.httperror import HttpError
# from ICrawlerSpiders.useragent import user_agent_list
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError, ConnectionRefusedError
# from functools import reduce
from OperateDB.conn_mongodb import Op_MongoDB
from SpiderTools.dian_ping_files.dian_ping import ParseFont, ParseStaticFont
from SpiderTools.tool import get_jp_value, diff_url
from SpiderTools.tool import re_text
from SpiderTools.tool import complement_url
from SpiderTools.tool import get_date_time
from Env.parse_yaml import DBConfigParser
from TemplateMiddleware.addres_middlewares import Address_Middleware
from SpidersLog.icrwler_log import ICrawlerLog
from Env.black_white import Black_White
from scrapy.selector import Selector
from SpiderTools.Js_func import JsFunc
from staticparm import max_duplicate
import demjson
# import execjs
import json
import scrapy.crawler
import ssl
import time
import jsonpath
import scrapy

ssl._create_default_https_context = ssl._create_unverified_context


class A_Templet_Spiders(scrapy.Spider):
    name = 'AddressTempletSpider'
    # 计数
    success = 0
    total = 0
    duplicate = 0
    black_url = 0
    gray_url = 0
    entity = ''
    s_code = ['PSBCORGANIZE']

    def __init__(self, code_, type_, entity_code, entity_name, key, *args, **kwargs):
        '''
        定义参数
        :param code_: code
        :param type_: content还是grab
        :param entity_code: 实体code
        :param entity_name: 实体名称
        :param dbname:
        :param jobinstid: job调度id
        :param method: get还是post
        :param args:
        :param kwargs:
        '''
        super(A_Templet_Spiders, self).__init__(*args, **kwargs)

        # 参数相关
        self.code_ = code_
        self.type_ = type_
        self.entity_code = entity_code
        self.entity = entity_code
        self.entity_name = entity_name
        self.key = key

        # 数据库配置相关
        config = DBConfigParser()
        self.fixed_db = config.get_fixed_db()
        self.temp_db = config.get_temp_db()

        # 数据库相关
        self.conn = Op_MongoDB().conn_mongo()
        self.mongodb = Op_MongoDB(db=self.fixed_db, coll=entity_code, key=key, conn=self.conn)
        self.tempmongodb = Op_MongoDB(db=self.temp_db, coll=entity_code, key=key, conn=self.conn)
        self.address_mongodb = Op_MongoDB(db='spider_address', coll=code_, conn=self.conn)

    def start_requests(self):

        try:
            # 中间件解析配置信息
            midd = Address_Middleware(self.code_).Invoking_Diff()
            if not midd:
                self.log.error('地址中间件返回False')
                print(1)
                raise Exception('地址中间件返回False')
        except Exception as e:
            log = ICrawlerLog(name='middleware').save
            log.error('%s' % e)
            print(1)
            raise Exception('地址中间件执行异常')

        self.log = ICrawlerLog(name='spider').save
        self.log.info('地址中间件程序执行成功')
        self.white = midd['white']
        self.black = midd['black']
        address_url = []

        if self.type_ != "FIXED":  # 固定模式不走这个逻辑
            # 将地址页面url集合存在mongo里，分别获取，这个逻辑是防止已采集的数据将不采集
            address_url = self.address_mongodb.S_Mongodb()
            if not address_url:
                self.address_mongodb.I_Mongodb([{'URL_': m_} for m_ in list(set(midd['url']))])
            address_url = self.address_mongodb.S_Mongodb(output='URL_')

        # 抓包模式处理
        if self.type_ == "GRAB":
            pform = midd['parm']               # 请求参数
            static_data = midd['static_data']  # 固定参数字段
            purl = midd['url']                 # 请求的url列表
            pheaders = midd['header']          # 请求headers
            pmethod = midd['method']           # 请求方式
            param_type = midd['param_type']    # 请求参数类型common，payload
            v_parm = ''
            meta = {"v_parm": '',
                    "final_out": midd['final_out'],   # 输出字段，只有code和name
                    "con_out": midd['content_out'],   # 输出字段，xpath/jsonpath，name，algo，expr（自己部分）
                    "textType": midd['textType'],     # 内容格式：json/html
                    "node": midd['node'],             # xpath/jsonpath公共部分
                    "entity_name": self.entity_name,  # 实体名称
                    "entity_code": self.entity_code,  # 实体编码
                    "domain": midd['domain'],         # 域名
                    "content_url": midd['content_url'],      # 默认存入mongo主键：{url}
                    "content_algo": midd['content_algo'],    # 内容js函数
                    "param_output": midd['param_output'],    # 参数输出
                    "result_output": midd['result_output'],  # 结果输出
                    }
            request_map = []
            if len(pform) == len(purl):  # 将请求参数和url组合在一起
                for url in purl:
                    index = purl.index(url)
                    form = pform[index]
                    request_map.append((url, form))
            elif len(pform) == 0:
                for url in purl:
                    request_map.append((url, None))
            else:
                for form in pform:
                    for url in purl:
                        request_map.append((url, form))
            # 参数映射的列表的长度(n) 与 请求数(m/page)成乘法关系 其乘积(n*m) = 最终的结果输出项, 但由于主键限制, 所以这种配置产生的请求应该取每个响应中唯一值. 所以配置此类模板时, 请限制参数映射的列表的长度/请求数 的数量为 1 个, 而且数据来源的mongo最好为一个
            for rm in request_map:
                url = rm[0]
                form = rm[1]
                meta['parm'] = form
                try:
                    meta['static_data'] = static_data[request_map.index(rm)] if isinstance(static_data,list) else static_data
                except:
                    # 临时策略, 可修改
                    meta['static_data'] = static_data[0] if isinstance(static_data, list) else static_data
                meta['p_url'] = url
                if url not in address_url:
                    continue
                # print(url,form)
                if self.duplicate < int(max_duplicate):
                    if param_type == 'PAYLOAD':
                        bodys = json.dumps(form)
                        yield scrapy.Request(
                            url=url, headers=pheaders, method=pmethod, meta=meta, body=bodys,
                            callback=self.grad_adress_parse, dont_filter=True,
                            errback=lambda respone, arg2=v_parm: self.errback_httpbin(respone, v_parm)
                        )

                    else:
                        yield scrapy.FormRequest(
                            url=url, headers=pheaders, formdata=form, method=pmethod, meta=meta,
                            callback=self.grad_adress_parse, dont_filter=True,
                            errback=lambda respone, arg2=v_parm: self.errback_httpbin(respone, v_parm)
                        )

        # 页面模式处理
        if self.type_ == 'PAGE':
            urllist = midd['url']
            for p_url in urllist:
                if p_url not in address_url:
                    continue
                if self.duplicate < max_duplicate:
                    yield scrapy.Request(url=p_url, callback=self.page_adress_parse, encoding='utf-8',
                                         meta={'pattern': midd['pattern'], 'prefix_url': midd['prefix_url'],
                                               'prefix_expr': midd['prefix_expr'],
                                               'entity_name': self.entity_name,
                                               'entity_code': self.entity_code,
                                               'domain': midd['domain'],
                                               'algo': midd['algo'],
                                               'p_url': p_url
                                               }
                                         , errback=lambda respone, arg2=p_url: self.errback_httpbin(respone, arg2)
                                         )

        # 固定模式处理
        if self.type_ == 'FIXED':
            final = []
            for url in midd['url']:
                fixed = {}
                final.append(self.__assembly(fixed, url))
            self.__import_data(final)

    def grad_adress_parse(self, response):
        """
        地址抓包模式解析并入库
        :param response:
        :return:
        """
        self.log.info('{}，响应成功！'.format(str(response.url)))
        v_parm = response.meta['v_parm']
        response_content = response.body
        self.__grad_parse(response, response_content, response.meta)

    def page_adress_parse(self, response):
        """
        地址page模式内容处理并入库
        :param response:
        :return:
        """
        # print(response.meta['proxy'])
        self.log.info('{}，响应成功！'.format(str(response.url)))
        pattern = response.meta['pattern']
        prefix_url = response.meta['prefix_url']
        algo = response.meta['algo']
        final = []
        data = []
        # 内容解析
        for p_ in pattern:
            if len(p_) != 2:
                continue
            for p1_ in p_:
                temdata = []
                if p1_ is None or p1_ == '':
                    continue
                v = response.xpath(p1_).extract()
                if v is None or len(v) < 1:
                    continue
                else:
                    for n in v:
                        temdata.append(n)
                data.append(temdata)
            if len(data) == 2:
                break

        if len(data) != 2:
            self.log.error('url=%s page模式未匹配到数据,xpath=%s' % (response.url, pattern))
            return None

        for url, name in list(zip(*data)):
            address = {}
            if algo:
                url = JsFunc(algo, "%s" % url).text
                if not url:
                    self.log.error('algo中js匹配url出错')
                    raise Exception('algo中js匹配url出错')

            # 补全url地址
            if prefix_url and algo:
                url = prefix_url + url
            else:
                # 自动补全url的功能
                url = complement_url(response.url, url, prefix_url)

            if not url:
                self.log.error('url为空，不插入')
                continue

            # 地址信息入库
            address['NAME_'] = re_text(name)
            final.append(self.__assembly(address, url))

        self.__import_data(final)
        self.address_mongodb.R_Mongodb({'URL_': response.meta['p_url']})

    def __import_data(self, final):
        """
        判断是否在白名单内，然后存储
        :param final:
        :return:
        """
        for x, y in final:
            # 入mongodb
            # print(x['URL_'])
            try:
                b_w = Black_White().prevent_outer_chain(x['URL_'], self.white, self.black)
                if b_w is None:
                    self.log.error('%s不在黑白名单内' % x['URL_'])
                    self.gray_url = self.gray_url + 1
                    continue
                if not b_w:
                    self.log.error('%s在黑名单内' % x['URL_'])
                    self.black_url = self.black_url + 1
                    continue
                if not x[self.key]:
                    self.log.error(x)
                    self.log.error('主键为空，不插入')
                    continue
                try:
                    dynamic_conn = Op_MongoDB(db=self.fixed_db, coll=self.entity_code, key=self.key).conn_mongo()
                    self.mongodb.conn = dynamic_conn
                    self.tempmongodb.conn = dynamic_conn
                except:
                    self.log.error('动态创建mongo连接失败')
                    return False
                status = self.mongodb.I_Mongodb(x)  # fixed表
                if status != 'duplicate':
                    try:
                        self.tempmongodb.I_Mongodb(y)
                    except Exception as e:
                        from bson.objectid import ObjectId
                        if isinstance(status, ObjectId):
                            self.mongodb.R_Mongodb({'_id': status})
                            self.log.info(f'temp表写入失败, 删除fixed对应记录--{status}')
                        self.log.error('写入fixed表成功, 插入失败{}, {}'.format(e, x))
                    # dynamic_conn.close()
                    self.success += 1
                elif status == 'duplicate':  # 两种情况 , 没写入那一定是被判断 duplicate
                    self.duplicate += 1
                else:
                    pass
                dynamic_conn.close()
            except Exception as e:
                self.log.error(e)

        self.total = self.total + len(final)

    def errback_httpbin(self, failure, name):
        '''
        srapy请求异常输出
        :param failure:
        :param name:
        :return:
        '''
        if failure.check(ConnectionRefusedError):
            request = failure.request
            self.log.error('ConnectionRefusedError： %s' % (request.url))
        elif failure.check(HttpError):
            response = failure.value.response
            self.log.error('HttpError on %s satus_code:%s' % (response.url, response.status))
        elif failure.check(DNSLookupError):
            request = failure.request
            self.log.error('DNSLookupError on %s', request.url)
        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.log.error('TimeoutError on %s', request.url)
        else:
            request = failure.request
            self.log.error('OtherError on %s', request.url)
            self.log.error(repr(failure))

    def close(spider, reason):
        """
        日志输出计数
        :param reason:
        :return:
        """
        log = ICrawlerLog(name='spider').save
        if spider.total != 0 or spider.duplicate != 0 or spider.success != 0:
            log.info('地址模板%s执行成功 ' % spider.entity)
            log.info('总共抓取%s条,成功抓取%s条,重复抓取%s条,黑名单%s条，灰名单%s条'
                     % (spider.total, spider.success, spider.duplicate, spider.black_url, spider.gray_url))
            print(0)
        else:
            log.error('执行异常')
            spider.address_mongodb.R_Mongodb({})
            print(5)
        spider.conn.close()

    def grad_adress_parse_temp(self, response, meta):
        """
        地址抓包模式解析并入库
        :param response:
        :param meta:
        :return:
        """
        v_parm = meta['v_parm']
        response_content = response.content
        self.__grad_parse(response, response_content, meta)

    def __assembly(self, data, url):
        """
        组合数据fix，temp
        :param data:
        :param url:
        :return:
        """
        unit = []
        data['URL_'] = url                       # 默认主键
        data['DEALTIME_'] = str(time.time())     # 时间戳
        data['ENTITY_NAME_'] = self.entity_name  # 实体名称
        data['ENTITY_CODE_'] = self.entity_code  # 实体编码
        data['TEMPLATE_CODE_'] = self.code_      # 地质编码
        unit.append(data)
        grad = eval(str(data))
        grad['STATUS_'] = '1'
        grad['LOCKTIME_'] = ''
        grad['DEALTIME_'] = str(time.time())
        grad['DATETIME_'] = get_date_time()
        unit.append(grad)
        return unit

    def __grad_parse(self, response, response_content, meta):
        """
        抓包内容解析
        :param response:
        :param response_content:
        :param meta:
        :return:
        """
        text_type = meta['textType']         # 内容格式
        node = meta['node']                  # 公共部分
        content_url = meta['content_url']    # 默认主键，{url}
        p_url = meta['p_url']                # 当前请求的url
        content_algo = meta['content_algo']  # 内容js函数
        parm = meta['parm']                  # 请求参数
        static_data = meta['static_data']    # 静态参数
        param_output = meta['param_output']  # 参数输出
        result_output = meta['result_output']  # 输出字段，code，name
        con_out = meta['con_out']              # 输出字段，xpath/jsonpath，name，algo，expr（自己部分）

        final = []

        # 处理response的编码问题
        try:
            content_data = str(response_content, encoding='utf-8')
        except:
            encode = response.encoding
            if encode == 'ISO-8859-1' or encode == 'cp1252':
                encode = 'gb2312'
            try:
                content_data = str(response_content, encoding=encode)
            except:
                content_data = response.text

        # 处理大众点评的数据字体
        if '_DZDP_' in self.entity_code:
            try:
                content_data = ParseFont().main(content_data)
                content_data = ParseStaticFont().main(content_data)
            except Exception as e:
                self.log.error('点评数据数据处理异常, {}'.format(e))

        if not content_data and len(content_data) < 10:
            self.address_mongodb.R_Mongodb({'URL_': p_url})
            self.log.error('去请求网站返回数据为空,url:%s' % p_url)
            return False

        # 判断内容类型，json或是js返回内容
        if text_type != 'html':
            try:
                content_data = demjson.decode(content_data)  # str转dict
            except:
                content_data = content_data
        # print(content_data)

        # 内容算法，主要处理jQuery（）形式
        if content_algo:
            try:
                js_data = JsFunc(content_algo, content_data).text
                if isinstance(js_data, dict) or isinstance(js_data, list):
                    content_data = js_data
                else:
                    # 算法处理json后处理
                    if text_type != 'html':
                        try:
                            content_data = eval(js_data)
                        except:
                            content_data = demjson.decode(js_data)
                    # 算法处理html后处理
                    else:
                        content_data = js_data
            except:
                self.log.error('js函数处理内容异常')
                return False

        # 如果json内容是列表情况，公共部分赋值为空
        if isinstance(content_data, list):
            node = ''

        # xpath、jsonpath通过最大公约数计算公共部分提取出来的node
        if node:  # xpath，jsonpath最大公约数

            # 内容json格式解析
            if text_type == 'json':
                # 匹配公共部分内容，缩小范围
                content = jsonpath.jsonpath(content_data, node)
                # content为空再进行二次匹配
                if not content:
                    content = jsonpath.jsonpath(content_data, node[:-3])[0]
                    if not content:
                        self.log.error('地址抓包没有匹配到数据')
                        return False
                    content = eval(content)
                content_data = content

            # 内容html格式解析
            elif text_type == 'html':
                response_data = Selector(text=content_data)
                if node[-1] == '/' and node[-2] == '/':  # xpath最后是//结束，例：//div//ul[@id='a']//
                    node = node[:-2]
                    content_data = response_data.xpath(node)
                else:
                    content_data = response_data.xpath(node[:-1])

            # 其他格式，暂时为拓展
            else:
                pass
        else:
            if isinstance(content_data, str):
                if content_data[0] == '[':
                    if content_data[-1] != ']':
                        content_data = content_data + ']'
                    content_data = eval(content_data)
                else:
                    response_data = Selector(text=content_data)
                    content_data = [response_data]
            elif isinstance(content_data, dict):
                content_data = [content_data]
            else:
                pass

        # 目前得到的content_data为list形式的数据（缩小范围后的）
        if not content_data:
            self.address_mongodb.R_Mongodb({'URL_': p_url})
            self.log.error('地址抓包内容经过处理后值为空，请检查问题,url:%s' % p_url)
            return False

        # 将输出字段的信息匹配出来
        con_data = jsonpath.jsonpath(con_out, '$.data[?(@)]')
        con_data = con_data if con_data else con_out if isinstance(con_out, list) else [con_out]

        #  循环遍历内容的list，分别获取每个的数据项
        for sel in content_data:
            url = content_url
            grad = {}
            param = []
            for item in con_data:  # 循环遍历读取数据项的配置信息：jsonpath/xpath，code，name等
                code = item['code']
                par = item['expr']
                if 'itemType' in item and item['itemType'] == 'paramOutput':
                    continue
                if 'algo' in item:
                    algo = item['algo']
                else:
                    algo = ''

                # 解析数据，jsonpath获取数据
                if text_type == 'json':
                    # jsonpath获取数据
                    if '$.' in par or '.' in par:
                        # jsonpath获取数据，在此应指定必要字段输出，为输出抛出异常，非必要字段可异常为空
                        try:
                            values = get_jp_value(sel, par)
                        except Exception as e:
                            self.log.error(e)
                        if values:
                            values = values
                        else:
                            values = ''
                    else:
                        try:
                            values = sel[int(par)]
                        except:
                            try:
                                values = sel[par]
                            except:
                                values = ''
                    if isinstance(values, list) and len(con_data) > 1:
                        for i in range(len(values)):
                            if not isinstance(values[i], str):
                                values[i] = str(values[i])
                        values = ','.join(values) if len(values) > 0 else ''

                # 解析数据，xpath获取数据
                elif text_type == 'html':
                    # xpath获取数据，在此应指定必要字段输出，为输出抛出异常，非必要字段可异常为空
                    try:
                        if len(con_data) == 1:
                            values = sel.xpath(par.replace(node, '')).extract()  # 把公共部分替换为空再解析
                        else:
                            values = sel.xpath(par.replace(node, '')).extract_first()
                            values = re_text(values) if values else ''
                    except Exception as e:
                        self.log.error('xpath:{}获取异常！'.format(str(par)))

                # 其他类型
                else:
                    pass
                if len(con_data) > 1:
                    # js函数处理
                    if algo:
                        values = JsFunc(algo, values).text

                    # 如果获取的是url，对url进行处理
                    # elif '@href' in par:
                    #     values = diff_url(url=str(values), last_url=response.url)
                        # print(values)
                    # else:
                    #     pass

                    tdict = {"code": code, "value": re_text(str(values))}
                    param.append(tdict)  # 将获取到的数据组合到一起
                    # 判断该字段是否是主键
                    if code == self.key:
                        grad[code] = re_text(str(values))
                    # 循环遍历, 直到替换成功,code为PRO_CODE_才替换，'http://ewealth.abchina.com/fs/{PRO_CODE_}.htm'
                    url = url.replace('{%s}' % code, re_text(str(values)))
                else:
                    for v_ in values:
                        grad = {}
                        if algo:
                            v_ = JsFunc(algo, v_).text
                        url_ = url.replace('{%s}' % code, re_text(str(v_)))
                        tdict = {"code": code, "value": re_text(str(v_))}
                        grad['PARAM_'] = [tdict]
                        if code == self.key:
                            grad[code] = re_text(str(v_))
                        for po in param_output:  # 参数输出数据存储
                            if po['code'] == self.key:
                                grad[po['code']] = re_text(str(static_data[po['expr']]))
                            url = url.replace('{%s}' % po['code'], re_text(str(static_data[po['expr']])))
                            grad['PARAM_'] = [{"code": po['code'], "value": re_text(static_data[po['expr']])}]
                        final.append(self.__assembly(grad, url_))
            # 参数输出数据存储
            if len(con_data) > 1:
                for po in param_output:  # 处理参数输出
                    if po['code'] == self.key:
                        grad[po['code']] = re_text(str(static_data[po['expr']]))
                    url = url.replace('{%s}' % po['code'], re_text(str(static_data[po['expr']])))
                    param.append({"code": po['code'], "value": re_text(static_data[po['expr']])}) # 在静态数据里面去获取
                if not url:
                    self.log.error('url为空，不插入,param:%s' % param)
                    continue
                grad['PARAM_'] = param
                final.append(self.__assembly(grad, url))
        # 存入mongo
        self.__import_data(final)
        # 删除spider_address里面那个url
        self.address_mongodb.R_Mongodb({'URL_': p_url})
