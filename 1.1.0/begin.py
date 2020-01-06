# encoding: utf-8
import os
from scrapy import cmdline
from OperateDB import conn_mysql
from SpidersLog.icrwler_log import ICrawlerLog
from ICrawlerSpiders.Spiders.ContentTempletSpider import Content_Start
from Env import log_variable as lv
from ICrawlerSpiders.Spiders.SinaWeiboSpider import WeiBoSpider
from ICrawlerSpiders.Spiders.SougouWechatSpider import WechatSpider
import sys
import traceback

from mapbar import mpfrun

entity_code = '110000BJRCB'
address_code = '110000BJRCB.ADDR'
# method = 'SPIDER_ADDRESS'
method = 'SPIDER_CONTENT'
jobinst_id = 'None'
fire_time = '1538150400423'
job_code = 'None'
from VERSION import VERSION_NUMBER


def Begin():
    # method = sys.argv[1]
    # entity_code = sys.argv[2]
    # jobinst_id = sys.argv[3]
    # fire_time = sys.argv[4]
    # address_code = sys.argv[5]

    log.info('当前实体{}运行的版本为：{}'.format(str(entity_code), str(VERSION_NUMBER)))

    # lv.set_job_code(job_code)
    lv.set_job_code(entity_code)
    lv.set_jobinst_id(jobinst_id)
    lv.set_group_code(method)
    lv.set_fire_time(fire_time)
    lv.set_address_code(address_code)

    opmysql = conn_mysql.Op_Mysql()
    # 查实体
    try:
        data = opmysql.Select_Query(output=['NAME_', 'TYPE_', 'CONFIG_'],
                                    tablename='spi_scra_entity',
                                    where='CODE_="%s"' % entity_code)[0]
    except:
        log.error('传入实体code错误')
        print(8)
        return False
    # 抓包、页面模式
    Tpye = opmysql.Select_Query(output='TYPE_',
                                tablename='spi_scra_addr',
                                where='CODE_="%s"' % address_code)

    if isinstance(Tpye, list):
        Tpye = Tpye[0]
    entity_name = data[0]
    dbanme = data[1]
    # TYPE_ = data[1]
    # parent_id = opmysql.Select_Query(output='PARENT_ID_', tablename='spi_entity_type', where='CODE_="%s"' % dbanme)
    # if isinstance(parent_id, list):
    #     parent_id = parent_id[0]
    # # if parent_id:
    # #     dbanme = dbanme + '_' + parent_id
    config = eval(data[2])

    log.info('爬虫开始执行')
    log.info('爬虫选取实体code：%s' % entity_code)
    # 微信模板
    if config['entityType'] == 'weChat':
        WechatSpider().query_code(code=config['id'],
                                  entity_code=entity_code,
                                  entity_name=entity_name)
        print(0)
    # 微博模板
    elif config['entityType'] == 'weibo':
        WeiBoSpider(url=config['id'],
                    entity_code=entity_code,
                    entity_name=entity_name).query_code()
        print(0)
    else:
        # 地址模板
        if method == 'SPIDER_ADDRESS':
            # 启动图吧第一层的模板
            if 'MAPBAR_DEATAIL_FIRST_' in entity_code:
                mpfrun(entity_code)
            else:
                if not Tpye:
                    log.error('传入地址code错误')
                    print(8)
                    return False
                # type_:页面、抓包
                type_ = opmysql.Select_Query(output='TYPE_',
                                             tablename='spi_scra_addr',
                                             where='CODE_="%s"' % address_code)[0]
                if not type_:
                    print(8)
                    log.error('传入地址code错误')
                    return False

                if type_ == 'GRAB':  # 抓包模式，该模式下才能使用除URL_其他数据项为主键
                    key = get_key(address_code, opmysql)
                else:
                    key = 'URL_'
                spidername = 'AddressTempletSpider'
                line = 'scrapy crawl %s -a code_=%s -a type_=%s -a entity_code=%s -a entity_name=%s -a dbname=%s ' \
                       '-a key=%s -L WARNING' % (spidername, address_code, type_, entity_code, entity_name, dbanme, key)
                log.info(line)
                cmdline.execute(line.split())  # 带参数启动scrapy

        if method == 'SPIDER_CONTENT':
            code = opmysql.Select_Query('spi_scra_content', 'CODE_', 'ENTITY_CODE_="%s"' % entity_code)
            if not code:
                log.error('没有该内容code')
                print(8)
                return False
            key = 'null'
            type_ = []
            for c in code:  # 循环处理内容模板content，content1，content2等
                type1_ = opmysql.Select_Query('spi_scra_content_item', 'TYPE1_', 'CONTENT_CODE_="%s" and '
                                               'TYPE1_!="MAPPING" and TYPE1_!="PARAM" and TYPE1_!="SUB"' % c)
                if type1_:
                    if isinstance(type1_, list):
                        for i in set(type1_):
                            type_.append(i)
                    else:
                        type_.append(type1_)
            type_ = list(set(type_))  # 去重
            # spidername = 'ContentTempletSpider'
            if type_ is None:
                type_ = 'ALL'
            if isinstance(type_, list):
                type_ = ','.join(type_)
            if isinstance(code, list):
                code = ','.join(code)
            # 启动内容模板
            Content_Start(code_=code,
                          type_=type_,
                          entity_code=entity_code,
                          entity_name=entity_name,
                          dbname=dbanme,
                          method=method,
                          key=key).start_requests()


def get_key(code, op):
    # 获取存入fixed和temp的主键，keyParam表示在结果数据项里有确认主键，默认URL_
    # 获取地址主键id
    grab_id = op.Select_Query('spi_scra_addr', 'GRAB_ID_', 'CODE_="%s"' % code)[0]
    # config：url、请求参数、headers、结果输出（数据项，xpath/jsonpath)、cookie、js函数等，主要分为input和output两个部分
    config = op.Select_Query('spi_grab_config', 'CONFIG_', 'ID_="%s"' % grab_id)[0]
    out_put = eval(config)['output']['data']
    for o_ in out_put:
        if 'keyParam' in o_ and o_['keyParam'] == 'Y':
            return o_['code']
    return 'URL_'


def run():
    # for _ in range(500):
        try:
            log.info('爬虫开始运行---')
            Begin()
        except Exception as e:
            # traceback.print_exc()
            # print(e)
            log.error('爬虫遇到异常失败')
            log.error(e)
            return False
            # continue


if __name__ == '__main__':
    log = ICrawlerLog('spider').save
    run()
