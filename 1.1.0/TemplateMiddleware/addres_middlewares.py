# encoding: utf-8
from .spider_middleware import M_Spiders
from SpiderTools.tool import get_jp_value
from SpidersLog.icrwler_log import log
from SpiderTools.tool import get_top_host
from Env.black_white import Black_White


class Address_Middleware(M_Spiders):

    def addr_ouput(self):
        """
        从mysql中读取所需配置信息
        """
        # 通过实体code拿到spi_scra_addr集合
        addr_output = self.opmysql.Select_Query(tablename='spi_scra_addr', where='CODE_="%s"' % self.code_)

        # 判断addr_output准确性的一些逻辑
        if not addr_output:
            raise Exception('没有在地址模板里查询到该实体,code:', self.code_)
        if len(addr_output) == 1:
            addr_output = addr_output[0]
        else:
            raise Exception('spi_scra_addr有多值，请检查,code:', self.code_)

        # 去得spi_grad_config的CONFIG_中的json,output数据项
        grad_config = self.opmysql.Select_Query('spi_grab_config', 'CONFIG_', 'ID_="%s"' % addr_output['GRAB_ID_'])[0]

        # 提取各类数据
        try:
            text_type = eval(grad_config)['output']['textType']
        except:
            text_type = 'json'
        try:
            content_algo = eval(grad_config)['output']['contentAlgo']
        except:
            content_algo = ''

        try:
            # 获取参数映射的数据库的参数类型
            datasource_map = eval(grad_config)['datasourceMap']
        except:
            datasource_map = ''
        # 去mongo查出所有的关联数据
        self.data_map = self.deal_source(datasource_map)
        # 把获取的数据组合在一起
        addrdict = {'grad_config': grad_config,
                    'type_': addr_output['TYPE_'],
                    'scra_config': addr_output['CONFIG_'],
                    'url': addr_output['PATH_'],
                    'item_config': '',
                    'textType': text_type,
                    'global_parm': '',
                    'expr': '',
                    'parm_type': '',
                    'content_algo': content_algo,
                    }

        if addr_output['TYPE_'] == 'FIXED' or addr_output['TYPE_'] == 'GRAB':
            # 处理input配置信息（各种参数）
            item_input = self.deal_input(get_jp_value(addr_output['CONFIG_'], '$.input[?(@)]'))
            # 去mongo查出所有的关联数据
            addrdict['item_input'] = self.deal_item(item_input)  # 处理input的所有参数组合成每个请求所需要的格式（字典），headers，page等
            addrdict['string_item'] = self.deal_input(get_jp_value(addr_output['CONFIG_'], '$.input[?(@)]'), 'string')

        if addr_output['TYPE_'] == 'PAGE':
            pattern = self.opmysql.Select_Query('spi_scra_addr_item', ['PATTERN1_', 'PATTERN2_', 'PATTERN3_'],
                                                'ADDR_CODE_="%s"' % addr_output['CODE_'])
            addrdict['pattern'] = pattern

        return addrdict

    # @property#Log是个类，如果是函数就不用写这个
    @log(name='middleware')
    def Invoking_Diff(self):
        """
        交给中间层处理配置信息
        """
        addrdict = self.addr_ouput()
        out = {}
        if addrdict:
            if addrdict['type_'] == 'PAGE':
                out = self.Page_Analyze(addrdict)

            if addrdict['type_'] == 'METHOD' or addrdict['type_'] == 'GRAB':
                out = self.Grab_Analyze(addrdict)

            if addrdict['type_'] == 'FIXED':
                out['url'] = self.deal_url(addrdict)
                out['white'] = self.white
                out['black'] = self.black
                out['domain'] = self.deal_domain(out['url'][0])

            if out:
                out['white'] = self.white
                out['black'] = self.black
            else:
                raise Exception('Grab_Analyze执行异常')

        else:
            raise Exception('addr_ouput函数执行执行结果为None')
        return out
