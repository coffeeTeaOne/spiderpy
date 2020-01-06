# encoding: utf-8
from SpiderTools.tool import platform_system
from Env.parse_yaml import FileConfigParser
from Env import log_variable as lv
from SpidersLog.file_handler import SafeFileHandler
import logging
import logging.handlers
import traceback


class MiddlewareLog():
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }  # 日志级别关系映射

    def __init__(self, logger=None):
        self.logger = logger

    def __call__(self, *args, **kwargs):
        '''
            指定保存日志的文件路径，日志级别，以及调用文件
            将日志存入到指定的文件中
        '''
        jobinst_id = lv.get_jobinst_id()
        job_code = lv.get_job_code()
        fire_time = lv.get_fire_time()
        group_code = lv.get_group_code()

        # year = time.strftime('%Y', time.localtime())  # 获取完整年份
        # month = time.strftime('%m', time.localtime())  # 获取月
        # day = time.strftime('%d', time.localtime())  # 获取日

        # 创建一个logger
        self.logger = logging.getLogger(self.logger)
        self.logger.setLevel(logging.INFO)
        # 创建一个handler，用于写入日志文件
        # self.log_time = time.strftime("%Y_%m_%d_")
        log_path = FileConfigParser().get_path(server=platform_system(), key='log')
        # log_path = './Logs/'
        # log_path = '/home/ijep/domain/logs/python/'
        # log_name = log_path + 'icrawlerspider.spider.%s-%s-%s.log' % (year, month, day)
        log_name = log_path + 'icrawlerspider.middleware.log'

        file_name = self.logger.handlers[0].baseFilename.split('\\')[-1] if len(self.logger.handlers) > 0 else ''

        if log_name.split('/')[-1] != file_name:
            self.logger.handlers.clear()  # 多个不同文件名的情况下用这个

        if not self.logger.handlers:
            # 追加模式,按照日期来设置日志，handlers中TimedRotatingFileHandler就是按照日期来设置,RotatingFileHandler这个按照文件大小来设置
            # fh = logging.handlers.TimedRotatingFileHandler(log_name, when='D', interval=1, encoding='utf-8')
            fh = SafeFileHandler(log_name, mode='a', encoding='utf-8')
            # fh.setLevel(logging.INFO)

            # 定义handler的输出格式
            formatter = logging.Formatter('[%(asctime)s][%(levelname)s] ' + '%s %s %s %s '
                                          % (group_code, job_code, jobinst_id, fire_time) + '%(message)s')
            # '%(filename)s->%(funcName)s line:%(lineno)d

            fh.setFormatter(formatter)

            # 给logger添加handler
            self.logger.addHandler(fh)

            # 添加下面一句，在记录日志之后移除句柄
            # self.logger.info('记录数据')
            # self.logger.removeHandler(fh)
            # 关闭打开的文件
            fh.close()
        return self.logger


class Log():
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        log = MiddlewareLog()()
        log.info("{}开始执行".format(self.func))
        func = self.func
        try:
            # result = func() #如果不是在类的函数里使用装饰器就可以这么写，如果这么写会报需要self入参（因为你是用类作为装饰器，函数就不会这样）
            result = func(*args, **kwargs)  # 没有（）就是一个类
            if result:
                log.info("{}执行成功".format(self.func))
                log.info("结果是: %s" % result)
                return result
            else:
                log.error("{}执行后返回值为空".format(self.func))
        except Exception as e:
            traceback.print_exc()
            log.error("{}程序异常执行失败".format(self.func))
            log.error(e)


def log(func):
    def wraaper(*args, **kwargs):
        log = MiddlewareLog()()
        log.info("{}开始执行".format(func))
        try:
            result = func(*args, **kwargs)  # 如果不是在类的函数里使用装饰器就可以这么写，如果这么写会报需要self入参（因为你是用类作为装饰器，函数就不会这样）
            if result:
                log.info("{}执行成功".format(func))
                log.info("结果是: %s" % result)
                return result
            else:
                log.error("{}执行后返回值为空".format(func))
        except Exception as e:
            traceback.print_exc()
            log.error("{}程序异常执行失败".format(func))
            log.error(e)

    return wraaper
