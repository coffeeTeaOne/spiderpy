# encoding: utf-8
from OperateDB import conn_mysql
from ICrawlerSpiders.useragent import user_agent_list
from SpiderTools import js_analyze
from SpiderTools.out_js import Fun_Js
from SpiderTools.tool import get_jp_value
from SpiderTools.lcs import LCS
from SpiderTools.tool import get_node
from SpidersLog.icrwler_log import ICrawlerLog
from SpidersLog.icrwler_log import log
from SpiderTools.tool import get_top_host
from Env.black_white import Black_White
from OperateDB.conn_mongodb import Op_MongoDB
from OperateDB.conn_mysql import Op_Mysql
from SpiderTools.Js_func import JsFunc
import json
import random
import jsonpath


class M_Spiders():

    # 实体名称
    # entity_name = "成都信用"
    def __init__(self, code_, parm=None, type_=None):
        '''
        初始化
        :param code_: #code
        '''
        self.opmysql = conn_mysql.Op_Mysql()
        self.code_ = code_
        self.parm = parm
        self.type_ = type_
        self.midd_log = ICrawlerLog(name='middleware').save
        self.black = Black_White().get_black()
        self.white = Black_White().get_white()
        self.data_map = ''

    def merge_unit(self, *args):
        """
        合并元素用
        :param args:
        :return: 返回合并元素
        """
        unit = []
        for i in args:
            unit.append(i)
        return unit

    def unicode_str(self, s):
        """
        把特殊转义的转义，目前是空格符
        :param s:需转义的字符串
        :return:返回转义的字符串
        """
        if not isinstance(s, str):
            return s
        if 'http://www.abchina.com' in s:
            return s

        un_ = {"data": [{"code": "", "expr": ['\t', '/t', '&nbsp;', '&nbsp', '\\t', '\\\\t']}]}

        for d_ in un_['data']:
            value = d_['code']
            for e_ in d_['expr']:
                s = s.replace(e_, value)
        return s

    @log(name='middleware')
    def Get_Grab_Basic_Info(self, param, garddict, status=None, method=None, paramtype=None):
        '''
        获取抓包信息，根据传入的参数来获取相应的值，比如传入的是header拿到的就是拼接好的header
        :param grad_config: 第一层的config json对象
        :param sceond: 第二层的config json对象 可能没有
        :param first: 第三层的config json对象 可能没有
        :param param:jsonpath表达式
        :return:返回组装数据
        '''

        result = []
        result_dict = {}
        root = []
        grad_config = garddict['grad_config']

        # second = garddict['item_config']
        # third = garddict['scra_config']
        if method == 'string':
            item_input = garddict['string_item']
        else:
            item_input = garddict['item_input']
        # 获取参数列表, 关联来源参数 reference['PRO_NAME_']       ('$.param[?(@)]', graddict, status=1)
        paramlist = get_jp_value(grad_config, param)

        if not paramlist:
            return None

        unit = []

        if paramtype == 'playload':
            for i in paramlist[0]:
                paramlist.append({'code': i, 'expr': paramlist[0][i]})
            paramlist.pop(0)

        for parm in paramlist:
            if 'itemType' in parm and parm['itemType'] == 'paramOutput':
                continue
            code = parm['code']
            expr = parm['expr']
            if 'algo' in parm:
                algo = parm['algo']
            else:
                algo = ''
            if code == 'User-Agent':
                continue
            if 'jsonpath' in expr:
                value = self.deal_jsonpath(expr)
            else:
                value = self.deal_reference(item_input, expr)  # 处理参数传递
            if value and '[*]' in value:
                root_v = value.split('[*].')
                if len(root_v) == 2:
                    root_parm = root_v[1]
                    root_value = root_v[0] + '[*]'
                else:
                    root_parm = root_v[-1]
                    root_v.pop(-1)
                    root_value = '[*].'.join(root_v) + '[*]'
                root.append('{"root":"%s","code":"%s","expr":"%s","algo":"%s"}' % (root_value, code, root_parm, algo))
            else:
                if isinstance(value, list):
                    if result:
                        for i in range(len(result)):
                            va = self.unicode_str(value[i])
                            if algo:
                                va = JsFunc(algo, va).text
                            v = {code: va}
                            result[i].update(v)
                    else:
                        result = [{code: JsFunc(algo, self.unicode_str(v)).text if algo else self.unicode_str(v)} for v
                                  in value]
                else:
                    va = self.unicode_str(value)
                    if algo:
                        va = JsFunc(algo, va).text
                    result_dict[code] = self.unicode_str(va)
                if status != 1:
                    unit.append('"%s":"%s"' % (code, self.unicode_str(value)))

        if len(root) > 0:
            return '{"data":[%s]}' % (','.join(root))
        elif status == 2:
            return {"data": unit}
        elif result:
            return result
        elif result_dict:
            return [result_dict]
        else:
            return '{%s}' % ','.join(unit)

    @log(name='middleware')
    def Get_Static_Data(self, json_path, garddict, item_input):
        grad_config = garddict['grad_config']
        data_list = get_jp_value(grad_config, json_path)  # 获取静态输出数据项
        if not data_list:
            return None
        if isinstance(item_input, list):
            static_data = []
            for i_input in item_input:
                data_dict = {}
                for data in data_list:
                    if data.get('type') == 'STRING' or data.get('type') == 'DATAMAP':
                        data_dict[data.get('name')] = i_input.get(data.get('name'))
                static_data.append(data_dict)
        elif isinstance(item_input, dict):
            static_data = {}
            for data in data_list:
                if data.get('type') == 'STRING' or data.get('type') == 'DATAMAP':
                    static_data[data.get('name')] = item_input.get(data.get('name'))
        else:
            static_data = ''
        return static_data

    @log(name='middleware')
    def Grab_Analyze(self, graddict):
        '''
        模版抓包分析方法
        :param configlist:配置信息列表，里面包含了多层配置信息
        :return: 返回together，里面包含了，headers信息，forms信息，提交方式信息，请求的url地址，最终输出项，是否有更目录有输出根节点
        '''
        # 解析多层配置文件获取headers信息，装载进together中
        headers = self.Get_Grab_Basic_Info('$.headers[?(@)]', graddict, method='string')

        if isinstance(headers, list):
            headers = headers[0]

        if isinstance(headers, dict):
            headers['User-Agent'] = random.choice(user_agent_list)

        if headers and isinstance(headers, str):
            if headers != '{}':
                headers = '{"User-Agent":"%s",%s}' % (
                random.choice(user_agent_list), headers.replace('{', '').replace('}', ''))
            else:
                headers = '{"User-Agent":"%s"}' % (random.choice(user_agent_list))

            try:
                headers = eval(headers)
            except:
                raise Exception('headers格式处理不正常，headers为: ', headers)

        together = {'header': headers}

        param_type = eval(graddict['grad_config'])['paramType']

        if param_type == 'COMMON':
            # 解析多层配置文件获取form表单信息，及mongo信息 返回处理好的请求数据列表
            form = self.Get_Grab_Basic_Info('$.param[?(@)]', graddict, status=1)
            if not form or form == '{}':
                form = []

        if param_type == 'PAYLOAD':
            form = []
            forms = self.Get_Grab_Basic_Info('$.payload.params', graddict, status=1, paramtype='playload')

            if forms and not isinstance(forms, list):
                forms = forms.replace('{{', '[{').replace('}}', '}]')
                forms = self.deal_item(forms)

            for f_ in forms:
                payload = eval(graddict['grad_config'])['payload']
                payload['params'].update(f_)
                form.append(self.deal_payload(payload))

        # 解析多层配置文件获取提交方式
        requestmethod = get_jp_value(graddict['grad_config'], '$.method')[0]

        # 解析多层配置文件获取请求url信息
        try:
            url = self.deal_url(graddict)
        except:
            raise Exception('请求url配置有问题，请检查')

        try:
            include_url = eval(graddict['grad_config'])['includeUrls']
        except:
            include_url = ''
        # 将包含url（一般是首页）添加到url列表中
        if include_url:
            url.append(include_url)

        if not url:
            raise Exception('请求url为空')

        content_url = get_jp_value(graddict['grad_config'], '$.output.url')
        # 解析多层配置文件获取最终的输出项
        if not graddict['item_config']:
            # 结果输出数据项配置：{'data': [{'code': 'PRO_NAME_', 'name': '产品名称'}, {'code': 'PRO_CODE_', 'name': 'PRO_CODE_'}]}
            final_out = js_analyze.Return_Result(graddict['scra_config']).An_Js_One('output')
            out_put = 'None'
            if graddict['textType'] == 'html':  # 判断response响应html/json
                content_out = js_analyze.Return_Result(graddict['grad_config']).An_Js_One('output')
            else:
                # 取出结果输出的公共部分（最大公约数算法），组合配置：'{"data":[{"root":"$.Data.Table[*]","code":"PRO_NAME_","expr":"ProdName","algo":""},{"root":"$.Data.Table[*]","code":"PRO_CODE_","expr":"ProductNo","algo":""}]}'
                content_out = self.Get_Grab_Basic_Info('$.output.data[?(@)]', graddict)
            if not content_url or not isinstance(content_url, list) or len(content_url) != 1:
                raise Exception('地址page模式没有取到内容url')
            together['content_url'] = content_url[0]
            output_list = get_jp_value(graddict['grad_config'], '$.output.data[*]')
        else:
            final_out = js_analyze.Return_Result(graddict['item_config']).An_Js_One('output')
            out_put = js_analyze.Return_Result(graddict['scra_config']).An_Js_One('output')
            content_out = js_analyze.Return_Result(graddict['grad_config']).An_Js_One('output')
            output_list = get_jp_value(graddict['grad_config'], '$.output[*]')

        content_out = content_out if isinstance(content_out, dict) or isinstance(content_out, list) else json.loads(content_out)
        item_input = graddict.get('item_input')
        static_data = self.Get_Static_Data('$.input[?(@)]', graddict, item_input)

        if graddict['parm_type']:
            tempcontent = []
            for c_ in content_out:
                for g_ in graddict['parm_type']:
                    if c_['code'] == g_['code']:
                        c_.update(g_)
                        tempcontent.append(c_)
                        break
            content_out = tempcontent

        together['parm'] = form
        together['static_data'] = static_data
        together['method'] = requestmethod
        together['url'] = url
        together['domain'] = self.deal_domain(url[0])
        together['final_out'] = final_out
        together['out_put'] = out_put
        together['content_out'] = content_out
        together['global_parm'] = graddict['global_parm']
        together['textType'] = graddict['textType']
        together['expr'] = graddict['expr']
        together['param_type'] = param_type

        param_output = []
        result_output = []
        result_pattern = []
        if output_list:
            for ou_ in output_list:
                if 'itemType' not in ou_ or ou_['itemType'] == 'resultOutput':
                    result_pattern.append(ou_['expr'])
                    result_output.append(ou_)
                elif 'itemType' in ou_ and ou_['itemType'] == 'paramOutput':
                    param_output.append({'code': ou_['code'], 'expr': ou_['expr']})

        together['content_algo'] = graddict['content_algo']
        together['param_output'] = param_output
        together['result_output'] = result_output

        if graddict['textType'] == 'json':
            try:
                node = content_out['data'][0]['root']
            except:
                node = ''

        if graddict['textType'] == 'html':

            if 'pattern' in graddict and graddict['pattern']:
                parttern = graddict['pattern']
            else:
                # parttern = get_jp_value(content_out, '$.data[*].expr]')
                parttern = result_pattern

            if len(parttern) > 1:
                lcs = LCS(parttern[0], parttern[1]).get_lcs()
                for p_ in parttern:
                    lcs = get_node(lcs, p_)
                node = lcs
            else:
                node = ''

        together['node'] = node

        return together

    @log(name='middleware')
    def Page_Analyze(self, pagedict):
        """
        page模式分析
        :param pagedict:
        :return:
        """
        urllist = []
        jsondata = pagedict['scra_config']
        url = pagedict['url']

        try:
            prefix_url = eval(pagedict['grad_config'])['output']['prefix_url']
        except:
            prefix_url = ''

        try:
            prefix_expr = eval(jsondata)['prefix_expr']
        except:
            prefix_expr = ''

        together = {'prefix_url': prefix_url, 'prefix_expr': prefix_expr}

        try:
            together['algo'] = eval(pagedict['grad_config'])['output']['algo']
        except:
            together['algo'] = ''

        try:
            includeurl = eval(pagedict['grad_config'])['includeUrls']
        except:
            includeurl = ''

        if includeurl:
            urllist.append(includeurl)

        inputvalue = jsonpath.jsonpath(json.loads(jsondata), '$.input[?(@)]')

        if not inputvalue:
            together['pattern'] = list(zip(*pagedict['pattern']))  # xpath路径

            together['output'] = jsonpath.jsonpath(json.loads(jsondata), '$.output')  # output输出

            urllist.append(url)

            together['url'] = urllist
        else:
            for j_ in inputvalue:
                code = j_['code']
                type = j_['type']

                together['pattern'] = list(zip(*pagedict['pattern']))  # xpath路径

                together['output'] = jsonpath.jsonpath(json.loads(jsondata), '$.output')  # output输出

                if type == 'SCOPE':
                    for i in range(int(j_['min']), int(j_['max']), int(j_['step'])):
                        urllist.append(url.replace('{%s}' % code, str(i)))
                elif type == 'MAP':
                    collection = j_['collection']
                    if not isinstance(collection, list):
                        collection = eval(collection)
                    for i in collection:
                        urllist.append(url.replace('{%s}' % code, i.strip("'")))
                else:
                    urllist.append(url)

                together['url'] = urllist

        together['domain'] = self.deal_domain(urllist[0])

        return together

    def deal_item(self, pform):
        '''
        处理/拼接form表单
        :param pform: 请求表单    参数映射的所有配置  {'code': 'SALE_SOURCE_', 'expr': '官网', 'type': 'STRING', 'algo': ''}
        :return:返回拼接好的表单
        '''
        froms = []
        new_froms = []
        p_form = []
        # 拼接完整的fromdata
        if pform:
            fo = {}
            if isinstance(pform, list):
                pform = pform
            else:
                pform = json.loads(pform)
            # 请求参数替换全局变量
            for f_ in pform:
                code = f_['code']
                value = f_['expr']
                if f_['type'] == 'ALL':
                    if not self.parm:
                        raise Exception('请求参数需要去地址列表中拿取全局参数的值，但没有拿到值，请检查')
                    for p_ in self.parm:
                        if p_['code'] == code:
                            fo[code] = p_['value']
                            continue
                    continue
                fo[code] = self.unicode_str(value)

            for pf_ in pform:
                if pf_['type'] == 'STRING':
                    p_form.append(pf_)

            for pf_ in pform:
                if pf_['type'] == 'DATAMAP':
                    p_form.append(pf_)

            for pf_ in pform:
                if pf_['type'] == 'SCOPE' or pf_['type'] == 'MAP':
                    p_form.append(pf_)

            for p_ in p_form:  # 把参数是列表的数据拼接一下
                if p_['type'] == 'SCOPE':
                    vrange = eval(p_['expr'])
                    min = vrange[0]
                    max = vrange[1]
                    step = vrange[2]
                    if len(froms) == 0:
                        for r_ in range(min, max, step):
                            fo[p_['code']] = str(r_)
                            froms.append(fo.copy())
                    else:
                        froms_temp = froms.copy()
                        for f_ in froms_temp:
                            for r_ in range(min, max, step):
                                fv = f_.copy()
                                fv[p_['code']] = str(r_)
                                froms.append(fv)
                            froms.pop(froms.index(f_))
                elif p_['type'] == 'MAP':
                    collection = eval(p_['expr'])
                    if len(froms) == 0:
                        for c_ in collection:
                            fo[p_['code']] = str(c_)
                            froms.append(fo.copy())
                    else:
                        froms_temp = froms.copy()
                        for f_ in froms_temp:
                            for c_ in collection:
                                fv = f_.copy()
                                fv[p_['code']] = str(c_)
                                froms.append(fv)
                            froms.pop(froms.index(f_))
                elif p_['type'] == 'DATAMAP':
                    db_data = self.data_map[p_['source']]  # 从mongo查出的所有数据
                    algo = p_['algo']
                    if len(froms) == 0:
                        for db_ in db_data:
                            for d_ in db_['PARAM_']:
                                if p_['field'] == d_['code']:
                                    if p_['datatype'] == 'STRING':
                                        value = str(d_['value'])
                                        if algo:
                                            value = JsFunc(algo, value).text
                                        fo[p_['code']] = value
                                        froms.append(eval(str(fo)))
                                    elif p_['datatype'] == 'SCOPE':
                                        collection = eval(d_['value'])
                                        for c_ in collection:
                                            fo[p_['code']] = str(c_)
                                            froms.append(fo.copy())
                    else:
                        for db_ in db_data:
                            index = db_data.index(db_)
                            for d_ in db_data[index]['PARAM_']:
                                if p_['field'] == d_['code']:
                                    if p_['datatype'] == 'STRING':
                                        fv = froms[index].copy()
                                        value = str(d_['value'])
                                        if algo:
                                            value = JsFunc(algo, value).text
                                        fv[p_['code']] = value
                                        froms[index] = fv
                                    elif p_['datatype'] == 'SCOPE':
                                        collection = eval(d_['value'])
                                        for c_ in collection:
                                            fv = froms[index].copy()
                                            fv[p_['code']] = str(c_)
                                            new_froms.append(fv)
        else:
            fo = None
        # froms分页请求，一页请求所有的信息在一个字典中，组合成一个列表[{requests1},{requests2},{}...]
        if not froms:
            froms.append(fo)
        if new_froms:
            froms = new_froms
        return froms

    def deal_input(self, inputvalue, type_=None):
        '''
        返回input的字典格式
        :param inputvalue:
        :return:
        '''
        if not isinstance(inputvalue, list):
            self.midd_log.error('处理input的值，但input的值不是list')
            return False

        string_dict = {}
        collection_dict = {}
        item_dict = {}
        range_dict = {}
        db_dict = {}
        item = []
        string_item = {}

        for i_ in inputvalue:
            if i_['type'] == 'MAP':
                collection_dict[i_['code']] = i_['collection']
                item.append({"code": i_['code'], "expr": "%s" % i_['collection'], "type": "MAP", "algo": i_['algo']})
            elif i_['type'] == 'ITEM':
                name = i_['expr'].replace(self.code_ + '.', '')
                item_dict[i_['code']] = i_['name']
                for p_ in self.parm:
                    if p_['code'] == name:
                        item_dict[i_['code']] = p_['value']
                        item.append({"code": i_['code'], "expr": p_['value'], "type": "ITEM", "algo": i_['algo']})
                        string_item[i_['code']] = p_['value']
                        break
            elif i_['type'] == 'SCOPE':
                range_dict[i_['code']] = [int(i_['min']), int(i_['max']), int(i_['step'])]
                item.append({"code": i_['code'], "expr": "%s" % [int(i_['min']), int(i_['max']), int(i_['step'])],
                             "type": "SCOPE", "algo": i_['algo']})
            elif i_['type'] == 'DATAMAP':
                db_dict[i_['code']] = {
                    'field': i_['dataTitle'], 'algo': i_['algo'], 'datatype': i_['dataType'],
                    'mapping': i_['collectionMap']
                }
                item.append({"code": i_['code'], "field": i_['dataTitle'], "type": "DATAMAP", "algo": i_['algo'],
                             "source": i_['collectionMap'], "expr": "", "datatype": i_['dataType']})
            else:
                if 'value' in i_:
                    name = 'value'
                else:
                    name = 'defaultValue'
                string_dict[i_['code']] = i_[name]
                string_item[i_['code']] = i_[name]
                item.append({"code": i_['code'], "expr": i_[name], "type": "STRING", "algo": i_['algo']})

        input_dict = {'STRING': string_dict,
                      'MAP': collection_dict,
                      'ITEM': item_dict,
                      'SCOPE': range_dict,
                      'DATAMAP': db_dict
                      }
        if type_ == 'string':
            return string_item
        return item

    def deal_url(self, graddict):
        """
        处理有分页的url
        :param graddict:
        :return:
        """
        purl = graddict['url']
        url = []
        # 处理url中的页数,格式[{'page': '1'}, {'page': '2'}, {'page': '3'}]
        url_param = self.Get_Grab_Basic_Info('$.urlParam[?(@)]', graddict, 1)

        # if isinstance(url_param, list):
        #     db = url_param[1]
        #     url_param = url_param[0]

        if url_param:
            if not isinstance(url_param, list) and not isinstance(url_param, dict):
                url_param = eval(url_param.replace('{{', '[{').replace('}}', '}]'))
            # url_param = self.deal_item(url_param)
            for url_p in url_param:
                p_url = purl
                for p_ in url_p:
                    p_url = p_url.replace('{%s}' % p_, url_p[p_])
                url.append(p_url)
        else:
            url = [purl]

        return url

    def deal_domain(self, url):
        domain = get_top_host(url)

        if not domain:
            raise Exception('匹配域名失败')

        b_w = Black_White().prevent_domain(domain, self.white, self.black)

        if b_w is None:
            raise Exception('域名不在黑白名单内')
        elif not b_w:
            raise Exception('域名在黑名单内')
        else:
            pass

        return domain

    def deal_source(self, dbsource):
        if dbsource:
            db_source = {}
            for db in dbsource:
                if db['dataBaseType'] == 'mongo':
                    if db['datasource'] == 'serverhost':
                        host = None
                    else:
                        host = db['datasource']
                    # 实例化mongo查询对象
                    op = Op_MongoDB(host=host, db=db['db'], coll=db['collection'], conn=Op_MongoDB().conn_mongo())
                    db_data = op.S_Mongodb()  # 查出所有的数据
                    op.conn.close()
                    if not db_data:
                        raise Exception('去mongo获取数据，数据为空')
                    db_source[db['code']] = db_data
                if db['dataBaseType'] == 'mysql':

                    mysql_data = []

                    if db['datasource'] == 'serverhost':
                        host = None
                    else:
                        host = db['datasource']

                    op = Op_Mysql(host=host)

                    db_data = op.Select_Query(db['tableName'], dict_=True)

                    if not db_data:
                        raise Exception('去mysql获取数据，数据为空')

                    db_data = [{"PARAM_": [{"code": d_, "value": db_[d_]} for d_ in db_]} for db_ in db_data]

                    db_source[db['code']] = db_data

            return db_source
        else:
            return ''

    def deal_payload(self, input_data):
        if isinstance(input_data, str):
            input_data = eval(input_data)

        for k, v in input_data.get('params').items():
            s = str(input_data.get('expr'))
            m = s.replace(jsonpath.jsonpath(input_data.get('expr'), k)[0], v)
            input_data['expr'] = eval(m)
        return input_data['expr']

    def deal_reference(self, data, expr):

        result = []
        if not isinstance(data, list):
            data = [data]

        for d_ in data:

            if not isinstance(d_, dict):
                d_ = json.loads(d_)

            reference = d_

            result.append(eval(expr))

        if isinstance(result, list) and len(result) == 1:
            result = result[0]

        return result

    def deal_jsonpath(self, expr):
        def jsonpath(str):
            return str

        return eval(expr)
