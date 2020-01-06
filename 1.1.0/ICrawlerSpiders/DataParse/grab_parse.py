# encoding: utf-8
# from SpiderTools.Out_Js import Fun_Js
from SpiderTools.tool import get_dict
from SpiderTools.tool import get_jp_value
from SpiderTools.tool import get_date_time
from SpidersLog.icrwler_log import ICrawlerLog
from SpiderTools.Js_func import JsFunc
from scrapy.selector import Selector
import time
import re
import jsonpath


class Grad_Parse:

    def __init__(self):

        self.log = ICrawlerLog('spider').save

    def grad_content_parse(self, content, meta):
        """
        内容抓包处理过程
        :param content:
        :param meta:
        :return:
        """
        url = meta['url']
        finalout = meta['final_out']
        conout = meta['con_out']
        entity_name = meta['entity_name']
        entity_code = meta['entity_code']
        exprconfig = meta['exprconfig']
        text_type = meta['textType']
        content_algo = meta['content_algo']
        result = []
        root = ''

        data = {}
        data['ENTITY_NAME_'] = entity_name
        data['ENTITY_CODE_'] = entity_code
        data['URL_'] = url
        data['DEALTIME_'] = str(time.time())
        data['DATETIME_'] = get_date_time()

        def __get_content(c):
            """
            处理jsonxpath，并返回信息
            :param c: 要处理的文本数据
            :return: 返回处理好的文本数据
            """

            for item in conout:
                code = item['code']
                # if root:
                #     expr = item['expr'].replace(root + '.', '')
                # else:
                expr = item['expr']

                try:
                    # values = Fun_Js().Get_Js(funname='exp', data=c, param=expr)
                    expr = expr.replace('jsonpath(', '').replace(')', '').replace('\'', '').replace('"', '')
                    values = jsonpath.jsonpath(c, expr)
                except Exception as e:
                    self.log.error('抓包中expr语法可能配置有问题expr为: %s' % expr)
                    self.log.error(e)
                    return False
                if not values:
                    values = ''
                if isinstance(values, list) and len(values) == 1:
                    values = values[0]
                if isinstance(values, str):
                    values = values.replace('\n', '')
                data[code] = values

                # 正则匹配大文本类型
                if item['type2'] == 'BLOB' and code in exprconfig:
                    tempdict = get_dict(exprconfig[code], values)
                    data.update(tempdict)
                try:
                    if item['algo']:
                        data[code] = JsFunc(item['algo'], values).text
                except:
                    pass
            return data

        if content_algo:
            content = JsFunc(content_algo, content).text
        if text_type == 'json':
            try:
                content = eval(content.replace('false', '\'\'').replace('null', '\'\'').replace('true', '\'\''))
            except:
                self.log.error('抓包内容数据有问题，数据匹配失败，可能是配置出问题，不是json格式，程序终止')
                return False
            # if '[*]' in finalout[0]['expr']:
            #     root = re.findall('\'(.*?)\'', finalout[0]['expr'])[0].split('[*]')[0] + '[*]'
            #     content = get_jp_value(content, root)

            if isinstance(content, list):
                self.log.error('抓包内容数据有问题，是个数组，无法匹配')
                return False
                # for c_ in content:
                #     d = __get_content(c_)
                #     result.append(d)
                # return result
            elif isinstance(content, dict) or isinstance(content, str):
                d = __get_content(content)
                return d
            else:
                self.log.error('内容抓包匹配函数失败，程序终止，请检查')
                return False
        elif text_type == 'html':
            content = Selector(text=content)
            for item in conout:
                data[item['code']] = content.xpath(item['expr']).extract_first()
            return data
