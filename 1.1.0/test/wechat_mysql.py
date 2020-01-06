import time
import pymysql


# datas = """NRCWKWECHAT 南海农商银行微刊 nanhainongshang,NRCLSJRWECHAT 南海农商银行零售金融 gh_b540b14de11e,SDELSWECHAT 顺德农商银行零售银行 SHUNDEnongshang,SDEEPWECHAT 顺德农商银行恩平支行 gh_9e0e73a728eb,SDEYDWECHAT 顺德农商银行英德支行 gh_88c7e5c3d7c4,SDEJRSCWECHAT 顺德农商银行金融市场 gh_ed09c97107ca,SDEWSHWECHAT 顺德农商银行微生活 gh_33150ac1ea83,SDEJRWECHAT 顺德农商银行公司金融 gh_68213812bb45"""
# data_list=[]
# for i in datas.split(','):
#     new = i.split(' ')
#     data_dict = {}
#     data_dict['code'] = new[0]
#     data_dict['name'] = new[1]
#     data_dict['id'] = new[2]
#     data_list.append(data_dict)
#     print(data_list)


class ConnMySQL41(object):

    def __init__(self):
        """
        连接数据库
        :return:
        """
        self.conn = pymysql.connect(host='172.22.69.41', user='root', passwd='dev007%P', db='spider_test',
                                    charset='utf8')
        # self.conn = pymysql.connect(host='127.0.0.1', user='root', passwd="123456", db='spider',charset='utf8')
        # self.conn = pymysql.connect(host='192.168.1.103', user='spider', passwd="spider#O2018", db='spider',charset='utf8')

    def insert_data(self, table_name, data):
        """
        添加数据
        :param tablename: 表名
        :param data: 添加数据(元祖转换为字符串)
        :return:
        """
        sql = "insert into {} values {};".format(table_name, data)
        with self.conn.cursor() as cur:
            try:
                self.conn.ping(reconnect=True)
                cur.execute(sql)
                self.conn.commit()
            except Exception as e:
                print(e)
                self.conn.rollback()
        self.conn.close()


if __name__ == '__main__':
    results_sdns = [{'code': 'NRCWKWECHAT', 'name': '南海农商银行微刊', 'id': 'nanhainongshang'},
                    {'code': 'NRCLSJRWECHAT', 'name': '南海农商银行零售金融', 'id': 'gh_b540b14de11e'},
                    {'code': 'SDELSWECHAT', 'name': '顺德农商银行零售银行', 'id': 'SHUNDEnongshang'},
                    {'code': 'SDEEPWECHAT', 'name': '顺德农商银行恩平支行', 'id': 'gh_9e0e73a728eb'},
                    {'code': 'SDEYDWECHAT', 'name': '顺德农商银行英德支行', 'id': 'gh_88c7e5c3d7c4'},
                    {'code': 'SDEJRSCWECHAT', 'name': '顺德农商银行金融市场', 'id': 'gh_ed09c97107ca'},
                    {'code': 'SDEWSHWECHAT', 'name': '顺德农商银行微生活', 'id': 'gh_33150ac1ea83'},
                    {'code': 'SDEJRWECHAT', 'name': '顺德农商银行公司金融', 'id': 'gh_68213812bb45'}]

    results = [{'code': 'BHBLFWECHAT', 'name': '河北银行廊坊分行', 'id': 'hebblffh'},
               {'code': 'BHBWXWECHAT', 'name': '河北银行微讯', 'id': 'bankhebei'},
               {'code': 'BHBZJKCCWECHAT', 'name': '河北银行张家口赤城支行', 'id': 'hbbank-zjkcczh'},
               {'code': 'BHBZJKWECHAT', 'name': '河北银行张家口分行', 'id': 'hbbank0313'},
               {'code': 'BHBXTRWECHAT', 'name': '河北银行邢台分行', 'id': 'hebeiyinhang_xt'}]
    for i in results:
        da = "('" + i['code'] + "', '" + i[
            'name'] + "', 'WECHAT', 'RUNING', 'DAY', '1', '0 18 1 01/1 * ? ', '{\"entityType\":\"weChat\",\"id\":\"" + \
             i[
                 'id'] + "\"}', null, null, '1.0.9', null, null, 'P0130524', '陈建飞', '2019-10-14 14:47:50', 'N', null, 'P0130524', '陈建飞', '2019-10-14 14:47:50', 25)"
        print(da)
        ConnMySQL41().insert_data(table_name='spi_scra_entity', data=str(da))
