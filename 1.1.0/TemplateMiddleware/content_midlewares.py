# encoding: utf-8
from .spider_middleware import M_Spiders
from SpiderTools.tool import get_jp_value
from SpidersLog.icrwler_log import log
import jsonpath
import json


class Content_Middleware(M_Spiders):

    def con_output(self):
        """
        从mysql读取所需配置信息
        :return:
        """
        # 通过实体code拿到spi_scra_content的code和config
        con = self.opmysql.Select_Query(tablename='spi_scra_content', where='CODE_="%s"' % self.code_)
        con_grad_config = []
        gparm = []
        # SUB子模板，MAPPING抓包映射？，PARAM参数映射
        type_ = self.opmysql.Select_Query('spi_scra_content_item', 'TYPE1_', 'CONTENT_CODE_="%s" and '
                                          'TYPE1_!="MAPPING" and TYPE1_!="PARAM" and TYPE1_!="SUB"' % self.code_)
        child_xpath = self.opmysql.Select_Query('spi_scra_content_item', 'PATTERN1_',
                                                'CONTENT_CODE_="%s" AND TYPE1_="SUB" ' % self.code_)
        # img_config = self.opmysql.Select_Query('spi_scra_content_item', 'CONFIG_',
        #                                         'CONTENT_CODE_="%s" AND TYPE1_="SUB" ' % self.code_)
        if type_ is None:
            self.type_ = 'ALL'

        # 全局变量,ALL模式表示时左边从地址映射的结果，最后在内容输出
        global_parm = eval(con[0]['CONFIG_'])['input']
        for gl in global_parm:
            if gl['type'] == 'ALL':
                gparm.append({'code': gl['code'], 'value': gl['value']})

        for i_ in con:

            con_config = i_['CONFIG_']  # 内容output和input的配置信息，这里input表示地址映射内容数据
            exprlist = []
            con_grad_item = []

            # 通过内容code拿到spi_scra_content_item中的信息
            # 获取每个数据字段的配置信息
            con_item = self.opmysql.Select_Query(tablename='spi_scra_content_item',
                                                 where='CONTENT_CODE_="%s"' % i_['CODE_'])
            # 获取子模板配置信息
            child = self.opmysql.Select_Query('spi_scra_content', 'CODE_',
                                              'ENTITY_CODE_="%s" AND LEVEL_="CHILD" ' % i_['CODE_'])
            if child:  # 子模板逻辑处理
                child_prefix = self.opmysql.Select_Query('spi_scra_content_item', 'CONFIG_',
                                                         'CONTENT_CODE_="%s" and TYPE1_="SUB"' % i_['CODE_'])
                child_prefix_url = [eval(cp)['prefix_url'] for cp in child_prefix]

                if not isinstance(child, list):
                    child = [child]
                child_out = []
                for child_code in child:
                    child_item = self.opmysql.Select_Query('spi_scra_content_item', 'CODE_',
                                                           'CONTENT_CODE_="%s"' % child_code)
                    if not isinstance(child_item, list):
                        child_item = [child_item]
                    for ci in child_item:
                        child_out.append(ci.replace(child_code + '.', ''))
            else:
                child = []
                child_out = []
                child_xpath = []
                child_prefix_url = []
            # 映射关系
            self.mapping = {}
            for c_ in con_item:
                # MAPPING 引用映射内容抓包的数据
                if c_['TYPE1_'] == 'MAPPING':
                    c = {}
                    if c_['SOURCE_'] not in self.mapping:
                        self.mapping[c_['SOURCE_']] = [c_['CODE_']]
                    else:
                        self.mapping[c_['SOURCE_']].append(c_['CODE_'])

            parm_type = []
            exprdict = {}

            for c_ in con_item:

                contentdict = {}
                imgcss_config_dict = {}
                # page获取到spi_scra_content_item值，用于下载img的属性
                img_config = self.opmysql.Select_Query('spi_scra_content_item', 'CONFIG_', 'CODE_="%s"' % c_['CODE_'])
                # 有值直接存储，没有就为空
                if img_config[0]:
                    imgcss_config_dict['img_src_list'] = eval(img_config[0]).get('img_src')
                    # imgcss_config_dict['img_algo'] = eval(img_config[0]).get('img_algo')
                    # imgcss_config_dict['css_algo'] = eval(img_config[0]).get('css_algo')
                    contentdict['img_src_list'] = imgcss_config_dict
                else:
                    contentdict['img_src_list'] = ''
                parm_type.append({'code': c_['CODE_'].replace(self.code_ + '.', ''),
                                  'type1': c_['TYPE1_'],'type2': c_['TYPE2_']})
                contentdict['parm_type'] = parm_type        # 字段名称，内容，文本
                contentdict['datatype'] = c_['DATA_TYPE_']  # 字段类型：字符串，数字，日期，pdf等
                contentdict['required'] = c_['REQUIRED_']   # 是否必须字段
                contentdict['global_parm'] = gparm          # 输出字段：地址映射到内容的数据字段
                contentdict['out_put'] = json.loads(con_config)['output']   # 输出字段：其他字段和配置信息

                # 处理配置正则集问题
                if c_['COLLECTION_CODE_'] is not None and c_['COLLECTION_CODE_'] != '':
                    exprlist = []
                    keys = ['expr_code_', 'item_code', 'name_', 'expr_']

                    #  查询类:在spi_regular_expr_map取出'EXPR_CODE_', 'ITEM_CODE', 'ITEM_NAME'
                    expr_code = self.opmysql.Select_Query(output=['EXPR_CODE_', 'ITEM_CODE', 'ITEM_NAME'],
                                                          tablename='spi_regular_expr_map',
                                                          where='COLLECTION_CODE_="%s"' % c_['COLLECTION_CODE_'])
                    if isinstance(expr_code, list):
                        for e_ in expr_code:
                            # 查询正则表达式
                            EX = self.opmysql.Select_Query(output='EXPR_', tablename='spi_regular_expr',
                                                           where='CODE_="%s"' % e_[0])

                            if isinstance(EX, list) and len(EX) == 1:
                                EX = EX[0]
                            if not EX:
                                EX = ''
                            # 将该表达式添加到该类
                            e_.append(EX)
                            # 将该类处理成字典
                            code_dict = dict(zip(keys, e_))
                            exprlist.append(code_dict)

                            # else:
                            # EX = self.opmysql.Select_Query(output='EXPR_', tablename='spi_regular_expr', where='CODE_="%s"' % expr_code)
                            # exprlist.append(self.merge_unit(EX['EXPR_'], EX['CONFIG_']))
                            # exprlist.append(self.merge_unit(EX['EXPR_'], EX['CONFIG_']))

                    exprdict.update({c_['CODE_'].replace(self.code_ + '.', ''): exprlist})
                    exprlist = exprdict

                # 处理内容抓包模式问题
                if c_['TYPE1_'] == 'GRAB':
                    con_grad = self.opmysql.Select_Query('spi_grab_config', 'CONFIG_', 'ID_="%s"' % c_['GRAB_ID_'])[0]

                    text_type = eval(con_grad)['textType'] if isinstance(con_grad, str) else con_grad['textType']

                    contentdict['item_config'] = c_['CONFIG_']
                    contentdict['string_item'] = self.deal_input(get_jp_value(c_['CONFIG_'], '$.input[?(@)]'),
                                                                 'string')
                    contentdict['item_input'] = self.deal_item(
                        self.deal_input(get_jp_value(c_['CONFIG_'], '$.input[?(@)]')))
                    contentdict['grad_config'] = con_grad
                    contentdict['scra_config'] = con_config
                    contentdict['method'] = 'GRAB'
                    contentdict['expr'] = exprlist
                    contentdict['textType'] = text_type
                    contentdict['url'] = eval(con_grad)['url']
                    contentdict['content_algo'] = eval(con_grad)['contentAlgo'] if 'contentAlgo' in eval(
                        con_grad) else ''

                    con_grad_item.append(contentdict)

                # 直接处理页面模式，采集数据
                if c_['TYPE1_'] == 'CONTENT':  # 大文本
                    algo = {}
                    con_f = jsonpath.jsonpath(json.loads(con_config), '$.output')[0]

                    con_f = con_f if not isinstance(con_f, str) else eval(con_f)
                    # 处理字段的一些逻辑
                    if con_f:
                        if isinstance(con_f, list):
                            unit = []
                            for con_ in con_f:
                                if not isinstance(con_, dict):
                                    con_ = eval(con_)
                                unit.append('"%s":"%s"' % (con_['code'], con_['value']))
                                if 'algo' in con_ and con_['algo']:
                                    algo[con_['code']] = con_['algo']
                            con_f = '{%s}' % ','.join(unit)
                        else:
                            con_f = str(con_f)
                    else:
                        raise Exception('没有输出项')
                        # pass

                    contentdict['pattern'] = self.merge_unit(c_['PATTERN1_'], c_['PATTERN2_'], c_['PATTERN3_'])  # 将3个路径模式的value合在一起
                    contentdict['method'] = 'CONTENT'  # 内容（非抓包，子模板其他）
                    contentdict['expr'] = exprlist
                    contentdict['con_f'] = con_f       # 所有输出的结果配置
                    contentdict['code'] = c_['CODE_']
                    contentdict['algo'] = algo         # 各字段分别对应的算法

                    con_grad_item.append(contentdict)

                # 附件模式
                if c_['TYPE1_'] == 'FILE':
                    contentdict['method'] = 'FILE'
                    contentdict['expr'] = exprlist
                    contentdict['code'] = c_['CODE_']

                    con_grad_item.append(contentdict)

            con_grad_config.append(
                {'code': i_['CODE_'], 'config': con_grad_item, 'child': child, 'child_output': child_out,
                 'child_xpath': child_xpath, 'child_prefix': child_prefix_url})

        if self.type_ == 'ALL':
            all_con = {'config':
                {
                    'conout': jsonpath.jsonpath(json.loads(con_config), '$.output')[0],
                    'global_parm': gparm,
                    'type1': 'ALL'
                }
            }
            return all_con

        return con_grad_config

    # @property 引入这个的是才用这个属性from SpidersLog.MiddlewareLog import Log
    # @Log
    @log(name='middleware')
    def Invoking_Diff(self):
        """
        配置信息交个中间层加工
        :return:
        """
        grad_list = []
        con = self.con_output()
        grab = []
        content = []
        file = []

        if self.type_ == 'ALL':
            return [con]
        if con:
            for con_ in con:
                config = con_['config']
                for c_ in config:
                    # 抓包处理
                    if c_['method'] == 'GRAB':
                        info_ = self.Grab_Analyze(c_)
                        parm = info_['parm']
                        if parm:
                            if not isinstance(parm, list):
                                parm = eval(parm)
                            for i_ in parm:
                                for m in self.mapping:
                                    if 'expr' not in parm:
                                        break
                                    if i_['expr'] in self.mapping[m]:
                                        info_['mapping'] = True
                        grab.append(info_)
                    # 内容处理
                    if c_['method'] == 'CONTENT':
                        parm_type = c_['parm_type']
                        for p_ in parm_type:
                            if p_['code'] == c_['code'].replace(self.code_ + '.', ''):
                                c_['type1'] = p_['type1']
                                c_['type2'] = p_['type2']
                                break
                        del c_['parm_type']

                        info_ = c_
                        content.append(info_)
                    # 附件处理
                    if c_['method'] == 'FILE':
                        info_ = c_
                        file.append(info_)

                con_['config'] = {'CONTENT': content, 'GRAB': grab, 'FILE': file}
                grad_list.append(con_)
        else:
            return False
        return grad_list
