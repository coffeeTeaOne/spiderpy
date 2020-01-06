# encoding: utf-8
from random import uniform
import time


class Function(object):
    """
    部分函数小工具
    """

    def timestamp(self, num=10):
        """
        产生10,13位的时间戳
        :param num: 产生几位时间戳,默认10位
        :return:time_10,time_13
        """
        if isinstance(num, int) and num == 10:
            # 去掉小数,强制转换
            time_10 = int(time.time())
            return time_10
        elif isinstance(num, int) and num == 13:
            # 将秒转换为毫秒
            time_13 = int(round(time.time() * 1000))
            return time_13
        else:
            raise Exception('time_stamp function parm bad input')

    def substr(self, input_str, left_num, right_num):
        """
        字符串截取
        :param input_str: 需要截取的字符串
        :param left_num: 截取起始点
        :param right_num: 截取终点
        :return: new_str:被截取下来的字符串
        """
        # 判断各参数类型和left_num小于right_num
        if isinstance(input_str, str) and isinstance(left_num, int) and \
                isinstance(right_num, int) and left_num < right_num:
            new_str = ''
            for i in range(left_num, right_num + 1):
                new_str += input_str[i]
            return new_str
        else:
            raise Exception('bad input')

    def random_num(self, start_num=0, end_num=1):
        """
        随机产生数字,默认0-1
        :param start_num: 范围起始点
        :param end_num: 范围终点
        :return: new_num:产生的数字(浮点数)
        """
        # 判断参数类型和start_num小于end_num
        if isinstance(start_num, int) and isinstance(end_num, int) and start_num < end_num:
            new_num = uniform(start_num, end_num)
            return new_num
        else:
            raise Exception('bad input')
