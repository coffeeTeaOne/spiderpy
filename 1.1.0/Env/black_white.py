# encoding: utf-8
from OperateDB.conn_mysql import Op_Mysql
from SpiderTools.tool import get_top_host
import re


class Black_White(object):

    def __init__(self):
        self.op_mysql = Op_Mysql()

    def get_white(self):
        '''
        白名单
        :param url: 请求url
        :return:
        '''

        white_list = self.op_mysql.Select_Query(tablename='spi_black_white_list', output='DOMMAIN_ADDR_',
                                                where='TYPE_="WHITE"')
        if white_list is None:
            raise Exception('白名单查询出来为空')
        return white_list

    def get_black(self):
        '''
        黑名单
        :return:
        '''

        black_list = self.op_mysql.Select_Query(tablename='spi_black_white_list', output='DOMMAIN_ADDR_',
                                                where='TYPE_="BLACK"')
        if black_list is None:
            black_list = []
        return black_list

    def prevent_outer_chain(self, url, white, black):
        # expr = '^https?://[a-zA-Z0-9]*.(.*?)/'
        # expr = '^https?://[a-zA-Z-]*.?[a-zA-Z0-9]*.%s[/a-zA-Z-]*' %domain_name
        # domain = re.findall(expr, url)[0]
        domain = get_top_host(url)
        if domain in white:
            return True

        if domain in black:
            return False

        return None

    def prevent_domain(self, domain, white, black):
        '''
        :param domain:
        :param white:
        :param black:
        :return: 再白名单里返回True，再黑名单里返回False，否则返回None
        '''
        if domain in white:
            return True

        if domain in black:
            return False

        return None
