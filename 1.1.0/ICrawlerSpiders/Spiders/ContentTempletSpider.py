# encoding: utf-8
from OperateDB.conn_mongodb import Op_MongoDB
from OperateDB.conn_redis import RedisClient
from SpiderTools.dian_ping_files.dian_ping import ParseFont, ParseStaticFont
from SpidersLog.icrwler_log import ICrawlerLog
from TemplateMiddleware.content_midlewares import Content_Middleware
from bson.objectid import ObjectId
from Exception.http_code import HttpCode
from Env.parse_yaml import DBConfigParser
from ICrawlerSpiders.useragent import user_agent_list
from ICrawlerSpiders.DataParse.grab_parse import Grad_Parse
from ICrawlerSpiders.DataParse.page_parse import Page_Parse
from SpiderTools.tool import get_date_time, ip_proxy
from SpiderTools.tool import get_jp_value
from SpiderTools.deal_pdf_two import PDF
from SpiderTools.tool import get_dict
from staticparm import pdf_dir
from SpiderTools.tool import get_base64
import random
import ssl
import time
import requests

ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings()


class C_Templet_Spdiers:
    """
    实例化参数，数据库，ip代理等
    """

    # name ='ContentTempletSpider'
    def __init__(self, code_, type_, entity_code, entity_name, dbname, method, key, *args, **kwargs):
        super(C_Templet_Spdiers, self).__init__(*args, **kwargs)
        # 参数相关
        self.code_ = code_
        self.type_ = type_
        self.entity_code = entity_code
        self.entity_name = entity_name
        self.dbname = dbname
        self.method = method
        self.status = ''

        # self.parm = list(zip(code_.split(','), type_.split(',')))
        self.code_ = code_.split(',')
        if isinstance(self.code_, str):
            self.code_ = [self.code_]

        # 数据库配置
        config = DBConfigParser()
        temp_db = config.get_temp_db()
        self.data_db = config.get_data_db()

        # 数据库相关
        self.conn = Op_MongoDB().conn_mongo()
        self.data_mongodb = Op_MongoDB(db=self.data_db, coll=dbname, key='null', conn=self.conn)
        self.temp_mongodb = Op_MongoDB(db=temp_db, coll=entity_code, key='null', conn=self.conn)
        self.log = ICrawlerLog('spider').save

    def u_data(self, id, status):
        '''
        如果内容爬取与异常退出，将temp表该实体的status改为2
        :param id: 数据id
        :param status: 状态值
        :return:
        '''
        st = False
        if self.status == 2:
            match = {"$where": "function(){return %d-this.LOCKTIME_>300}" % time.time()}
            try:
                st = self.temp_mongodb.S_Mongodb_One(match=match)
                self.status = 2
            except Exception as e:
                print(4)
                self.log.error(e)
                return False
        if (self.status == 1 and st == False) or (self.status == 2 and st):
            result = self.temp_mongodb.U_Mongodb({"_id": ObjectId(id), "STATUS_": "%s" % self.status},
                                                 {"$set": {"_id": ObjectId(id), "STATUS_": "%s" % status,
                                                           "LOCKTIME_": "%s" % str(time.time())}})
            if result['updatedExisting']:
                return True
        return False


class Content_Start(C_Templet_Spdiers):
    def start_requests(self):
        # 去mongo中取状态为1的数据，只取一条数据
        try:
            self.log.info('从mongo地址temp表中取一条数据')
            url_result = self.temp_mongodb.S_Mongodb_One(where={'STATUS_': '1'})
            self.status = 1
        except Exception as e:
            self.log.error(e)
            print(4)
            return False

        # 取状态为2的数据
        if not url_result:
            match = {"$where": "function(){return %d-this.LOCKTIME_>300}" % time.time()}  # 取时间大于300秒的数据
            try:
                url_result = self.temp_mongodb.S_Mongodb_One(match=match)
                self.status = 2
            except Exception as e:
                print(4)
                self.log.error(e)
                return False
            if not url_result:
                self.log.error('去mongodb中取一条数据，但没有找到可用数据，终止程序')
                print(0)
                return False

        _id = url_result['_id']
        # print(url_result['URL_'])

        # 将stadus的状态改为2
        if not self.u_data(_id, '2'):
            print(4)
            return False

        if not isinstance(url_result, list):
            url_result = [url_result]
        # url_result只有一条数据
        for urll in url_result:
            compare = []
            result = []
            grad_result = []
            self.url = urll['URL_']  # 内容url
            try:
                self.param = urll['PARAM_']  # 地址模板获取到的数据可用于映射到内容
            except KeyError:
                self.param = []
            for code_ in self.code_:
                r, c = self.__request_middware(code_, self.url)
                r['URL_'] = self.url
                result.append(r)
                # grad_result.append(g)
                compare.append(c)

            # 取匹配度最大的数据
            if len(compare) > 1:
                self.log.info('找出匹配度最高的数据')
                index = compare.index(max(compare))
                final_list = result[index]
                result = []
                result.append(final_list)
            if len(grad_result) > 1:
                self.log.error('抓包多个内容模板是否要做匹配度检查请检查')
                print(1)
                return None
            elif len(grad_result) == 1 and len(result) == 0:
                result = grad_result
            elif len(grad_result) == 1 and len(result) == 1:
                result[0] = grad_result[0].update(result[0])
            elif len(grad_result) == 0:
                pass
            else:
                self.log.error('内容抓取数据失败')
                print(1)
                return None
            # 输出结果
            if result:
                try:
                    status = self.data_mongodb.I_Mongodb(result)  # 存储数据
                    status = status[0] if isinstance(status, list) else status
                    from bson.objectid import ObjectId
                    try:
                        if not isinstance(_id, ObjectId):
                            _id = ObjectId(_id)
                        self.temp_mongodb.R_Mongodb({'_id': _id})  # 删除temp里面的该条数据
                        self.log.info('内容抓取数据成功，并成功插入mongo中')
                        print(0)
                    except Exception as e:
                        if isinstance(status, ObjectId):
                            self.data_mongodb.R_Mongodb({'_id': status})  # 自定义mongo数据回滚
                        self.log.error(
                            '模板:{}, 数据插入 mongo>spider_data 成功，但删除spider_url_temp失败, 程序终止'.format(self.entity_code))
                        self.log.error(e)
                        print(4)
                except Exception as e:
                    self.log.error('数据插入mongo失败，程序终止')
                    self.log.error(e)
                    print(4)
            else:
                self.log.info('插入mongo数据为空,result为空，未匹配到数据或者其它问题，程序终止')
                print(4)
            self.conn.close()  # 关闭 mongo 连接

    def __grab_requests(self, middware):
        """
        内容抓包模式的处理
        :param middware:
        :return:
        """
        self.log.info('开始抓包模式')
        # Middware = self.___get_middware(code_, param, None)
        _result = []
        for midd in middware:
            pheaders = midd['header']
            pform = midd['parm']
            if isinstance(pform, str):
                pform = eval(pform)
            if isinstance(pform, list) and len(pform) > 0:
                pform = pform[0]
            # refmongoval = midd['mongodb'][3]
            pmethod = midd['method']
            purl = midd['url'][0]
            final_out = midd['final_out']
            out_put = midd['out_put']
            con_out = midd['content_out']
            exprconfig = midd['expr']
            global_parm = midd['global_parm']
            text_type = midd['textType']
            content_algo = midd['content_algo']

            if pmethod == 'GET':
                parm = pform
                formdata = None
            if pmethod == 'POST':
                formdata = pform
                parm = None
            proxies = ip_proxy()
            # 不加verify=False，会报requests.exceptions.SSLError: HTTPSConnectionPool 错误
            self.log.info('开始请求%s，请求参数为%s,头信息为%s,请求代理为%s' % (purl, pform, pheaders, proxies))
            content_data = requests.request(method=pmethod, url=purl, params=parm, data=formdata,
                                            headers=pheaders, proxies=proxies, verify=False,
                                            allow_redirects=False)
            # 处理编码问题
            if content_data.status_code in [200, 304]:
                encode = content_data.encoding
                if not encode:
                    encode = 'UTF-8'
                if encode == 'ISO-8859-1':
                    encodings = requests.utils.get_encodings_from_content(content_data.text)
                    if encodings:
                        encode = encodings[0]
                    else:
                        encode = content_data.apparent_encoding
                content_data = content_data.content.decode(encode, 'replace')
                # 处理大众点评的数据字体
                if '_DZDP_' in self.entity_code:
                    try:
                        content_data = ParseFont().main(content_data)
                        content_data = ParseStaticFont().main(content_data)
                    except Exception as e:
                        self.log.error('点评数据数据处理异常, {}'.format(e))

                if len(content_data) > 0:
                    self.log.info('请求%s成功' % purl)
                    self.log.info('开始处理抓包模式的数据')
                    gresult = Grad_Parse().grad_content_parse(content_data, meta={"url": purl,
                                                                                  "final_out": final_out,
                                                                                  "out_put": out_put,
                                                                                  "con_out": con_out,
                                                                                  "entity_name": self.entity_name,
                                                                                  "entity_code": self.entity_code,
                                                                                  'exprconfig': exprconfig,
                                                                                  'textType': text_type,
                                                                                  'content_algo': content_algo
                                                                                  })
                    if not gresult:
                        self.log.error('内容抓包数据匹配失败，程序终止，网址:%s' % purl)
                        print(1)
                        raise Exception('False')
                    if isinstance(gresult, dict):
                        _result.append(gresult)
                else:
                    self.log.error('请求%s返回数据为空' % purl)
                    print(1)
                    raise Exception('False')
            else:
                self.log.error('抓包%s失败' % purl)
                self.log.error(HttpCode().get_code_info(content_data.status_code))
                print(2)
                raise Exception('False')

        grad = {}
        if len(_result) > 0:
            for i_ in _result:
                grad.update(i_)
            grad['url'] = purl
            grad['dealtime'] = str(time.time())
        return grad

    def __page_requests(self, middware, code_, url, child_xpath, child_prefix):
        """
        开始内容页面请求
        :param middware:
        :param code_:
        :param url:
        :param child_xpath:
        :param child_prefix:
        :return:
        """
        self.log.info('开始页面模式')
        proxies = ip_proxy()
        try:
            self.log.info('开始请求%s,请求代理为%s' % (self.url, proxies))
            content = requests.request(method='GET', url=url, proxies=proxies, verify=False,
                                       headers={'User-Agent': random.choice(user_agent_list)}
                                       # ,allow_redirects=False
                                       )
            # print(content.status_code)
        except requests.exceptions.ConnectionError:
            self.log.error('ConnectionError,请求%s失败' % self.url)
            print(2)
            raise Exception('False')
        # 处理编码问题
        if content.status_code in [200, 304, 301]:
            encode = content.encoding
            if not encode:
                encode = 'UTF-8'
            if encode == 'ISO-8859-1' or encode not in ['utf-8', 'gbk', 'gb2312']:
                encodings = requests.utils.get_encodings_from_content(content.text)
                if encodings:
                    encode = encodings[0]
                else:
                    encode = content.apparent_encoding
            try:
                content = content.content.decode(encode)
            except:
                # 这里处理也会存在问题
                for i in ['utf-8', 'gbk', 'gb2312']:
                    try:
                        content = content.content.decode(encoding=i, errors='replace')  # 不会报错
                        break
                    except:
                        continue

            # 处理大众点评的数据字体
            if '_DZDP_' in self.entity_code:
                try:
                    content = ParseFont().main(content)
                    content = ParseStaticFont().main(content)
                except Exception as e:
                    self.log.error('点评数据数据处理异常, {}'.format(e))
            self.log.info('开始处理页面模式的数据')
            temp_compare, child_url = Page_Parse().page_content_parse(content, meta={'pattern': middware, 'url': url,
                                                                                     "entity_name": self.entity_name,
                                                                                     "entity_code": self.entity_code,
                                                                                     "content_code": code_,
                                                                                     "algo": middware[0]['algo'],
                                                                                     "child_xpath": child_xpath,
                                                                                     "child_prefix": child_prefix
                                                                                     })
            if not temp_compare:
                self.log.error('内容page模式数据匹配失败，网址:%s' % url)
                print(1)
                raise Exception('False')
            return temp_compare, child_url
        else:
            self.log.error('page模式访问网页%s失败' % url)
            self.log.error(HttpCode().get_code_info(content.status_code))
            print(2)
            # self.temp_mongodb.R_Mongodb({'_id': ObjectId(_id)})
            raise Exception('False')

    def __all_parm(self, middware, code_):
        """
        处理映射参数
        :param middware:
        :param code_:
        :return:
        """
        self.log.info('开始ALL模式')
        # 全局变量处理
        global_parm = {}
        gl = middware['global_parm']
        if gl:
            self.log.info('替换全局变量')
            for m_ in gl:
                for pa_ in self.param:
                    name = m_['value'].replace(code_ + '.', '')
                    if pa_['code'] == name:
                        global_parm[m_['code']] = pa_['value']
        global_parm['ENTITY_NAME_'] = self.entity_name
        global_parm['ENTITY_CODE_'] = self.entity_code
        global_parm['URL_'] = self.url
        global_parm['DEALTIME_'] = str(time.time())
        global_parm['DATETIME_'] = get_date_time()
        return global_parm

    def __get_file(self, midd, url, code_):
        """
        处理pdf文件，下载，转文本
        :param midd:
        :param url:
        :param code_:
        :return:
        """
        pdf = PDF()
        file = {}
        content = ''
        global_parm = self.__get_global_parm(midd, code_)
        file.update(global_parm)
        for FILE in midd:
            name = self.entity_code + '_' + url.split('/')[-1]
            code = FILE['code'].replace(code_ + '.', '')
            if FILE['datatype'] == 'IMGPDF' or FILE['datatype'] == 'NOIMGPDF':
                try:
                    pdf.download_pdf(url, pdf_dir, name)
                except Exception as e:
                    self.log.error('类型1为附件，在线PDF下载失败,url:' % url)
                    raise Exception(e)

            if FILE['datatype'] == 'IMGPDF':
                content = pdf.imgpdf_change_img_local(pdf_dir + name)
                file[code] = content
                file['PDF_BASE64_'] = get_base64(pdf_dir, name)
            if FILE['datatype'] == 'NOIMGPDF':
                content = pdf.noimgpdf_change_word(pdf_dir + name)
                file[code] = content
                file['PDF_BASE64_'] = get_base64(pdf_dir, name)
            if content and FILE['expr']:
                tempdict = get_dict(FILE['expr'][code], content)
                file.update(tempdict)
            file['ENTITY_NAME_'] = self.entity_name
            file['ENTITY_CODE_'] = self.entity_code
            file['URL_'] = url
            file['DEALTIME_'] = str(time.time())
            file['DATETIME_'] = get_date_time()
        return file

    def __get_global_parm(self, midd, code_):
        """
        地址映射内容的数据
        :param midd:
        :param code_:
        :return:
        """
        global_parm = {}
        gl = midd[0]['global_parm']  # 映射的字段
        out_put = get_jp_value(midd[0], '$.out_put[*].code')  # 所有输出的字段
        if len(gl) > 0:
            self.log.info('替换全局变量')
            for m_ in gl:
                for pa_ in self.param:
                    name = m_['value'].replace(code_ + '.', '').strip()
                    if pa_['code'].strip() == name and pa_['code'] in out_put:
                        global_parm[m_['code']] = pa_['value']
        return global_parm

    def __get_middware(self, code_):
        """
        获取内容配置信息
        :param code_:
        :return:
        """
        try:
            Middware = Content_Middleware(code_, parm=self.param).Invoking_Diff()
            if not Middware:
                print(1)
                self.log.error('内容中间件执行失败，程序终止')
                raise Exception('False')
        except:
            print(1)
            self.log.error('内容中间件执行异常，程序终止')
            raise Exception('False')

        self.log.info('内容模板中间件执行成功')
        self.log = ICrawlerLog('spider').save
        return Middware

    def __request_middware(self, code_, url):
        """
        内容请求处理
        :param code_:
        :param url:
        :return:
        """
        Middware = self.__get_middware(code_)
        gr = {}
        rs = {}
        co = 0
        child_url = []
        for midd in Middware:
            midd_config = midd['config']
            # 处理全是映射的情况
            if 'type1' in midd_config and midd_config['type1'] == 'ALL':
                # result.append(self.__all_parm(midd_config,code_))
                return self.__all_parm(midd_config, code_), 0

            # 内容抓包模式处理
            if midd_config['GRAB']:
                gr.update(self.__grab_requests(midd_config['GRAB']))  # 内容抓包请求
                global_parm = self.__get_global_parm(midd_config['GRAB'], code_)  # 抓包映射数据
                gr.update(global_parm)
                if not gr:
                    return False

            # 内容page模式处理
            if midd_config['CONTENT']:
                temp_compare, child_url = self.__page_requests(midd_config['CONTENT'],  # 每个字段配置信息（数组）
                                                               code_,  # 内容编码
                                                               url,  # 内容url
                                                               midd['child_xpath'],  # 子模板xpath
                                                               midd['child_prefix'])  # 子模板url前缀
                global_parm = self.__get_global_parm(midd_config['CONTENT'], code_)  # 所有需要映射数据处理
                tcdict = temp_compare[0]
                tcdict.update(global_parm)  # 更新映射数据的字段
                # 计算匹配度，并放入list
                n = 0
                if len(temp_compare) > 1 and isinstance(temp_compare[1], list):
                    for tc in temp_compare[1]:
                        if tc == '':
                            continue
                        if tcdict[tc] != '' or tcdict[tc]:
                            n = n + 1
                co = n
                rs.update(tcdict)
            rs.update(gr)

            # 处理页面内容是PDF等附件类
            if midd_config['FILE']:
                FILE = midd_config['FILE']
                rs.update(self.__get_file(FILE, url, code_))

            # 处理子模板
            if midd['child']:
                if not child_url:
                    raise Exception('child_url为空')
                for child, c_url in list(zip(midd['child'], child_url)):
                    child_rs, child_co = self.__request_middware(child, c_url)
                    rs.update(child_rs)
                    co = child_co + co
            return rs, co
