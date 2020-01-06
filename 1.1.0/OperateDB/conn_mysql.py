# encoding: utf-8
from Env.parse_yaml import DBConfigParser
from SpidersLog.icrwler_log import ICrawlerLog
import pymysql
import traceback


class Static_Config:

    def __init__(self, host=None, port=None, user=None, password=None, dbanme=None):
        if host is None and port is None and user is None and password is None and dbanme is None:
            # self.config = DBConfigParser().get_config(server='mysql', key='1.103conn')
            # self.config = DBConfigParser().get_config(server='mysql', key='43conn')
            # self.config = DBConfigParser().get_config(server='mysql', key='localhostconn')
            # self.config = DBConfigParser().get_config(server='mysql', key='222conn')
            # self.config = DBConfigParser().get_config(server='mysql',key='41conn')
            # self.config = DBConfigParser().get_config(server='mysql', key='41conn_test')
            self.config = DBConfigParser().get_config(server='mysql', key='myconn_test')
            # self.config = DBConfigParser().get_config(server='mysql', key='67.25conn')
            self.config['cursorclass'] = pymysql.cursors.DictCursor
        else:
            self.config = {
                'host': host,
                'port': port,
                'user': user,
                'password': password,
                'db': dbanme,
                'charset': 'utf8',
                'cursorclass': pymysql.cursors.DictCursor,
            }

        self.log = ICrawlerLog(name='spider').save


class Op_Mysql(Static_Config):
    # 返回可用于multiple rows的sql拼装值
    def multipleRows(self, params):
        ret = []
        # 根据不同值类型分别进行sql语法拼装
        for param in params:
            if isinstance(param, (int, float, bool)):
                ret.append(str(param))
            elif isinstance(param, (str, 'utf-8')):
                param = param.replace('"', '\\"')
                ret.append('"' + param + '"')
            else:
                print('unsupport value: %s ' % param)
        return '(' + ','.join(ret) + ')'

    def Insert_Query(self, tablename, column, datas):
        try:
            connection = pymysql.connect(**self.config)
        except pymysql.err.OperationalError as e:
            self.log.error('pymysql.err.OperationalError:%s' % str(e))
            raise e
        except Exception as e:
            self.log.error(e)
            raise e
        count = 0
        try:
            with connection.cursor() as cursor:
                v = ','.join(["%s" for i in range(len(column))])
                if isinstance(column, list):
                    column = ','.join(column)

                try:
                    if len(datas) == 1:
                        query_sql = 'INSERT INTO ' + tablename + '(' + column + ') VALUES%s' % self.multipleRows(
                            datas[0])
                        cursor.execute(query_sql)
                    else:
                        query_sql = 'INSERT INTO ' + tablename + '(' + column + ') VALUE(' + v + ')'
                        cursor.executemany(query_sql, datas)
                    count = count + 1
                    connection.commit()
                except pymysql.err.IntegrityError as e:
                    self.log.info(e)
                    self.log.info(datas)
                    # errorcode = eval(str(e))[0]
                    # if errorcode == 1062:
                    #     print('主键重复')
                    pass
                except Exception as e:
                    traceback.print_exc()
                    # print(e,datas)
                    connection.rollback()
                    # print('需要特殊处理','INSERT INTO %s(%s) VALUES (%s)',datas)
                finally:
                    connection.close()
        finally:
            connection.close()

        # print('本次共插入%d条' %count)

    def Select_Query(self, tablename, output=None, where='1=1', dict_=False):
        try:
            connection = pymysql.connect(**self.config)
        except pymysql.err.OperationalError as e:
            self.log.error('pymysql.err.OperationalError:%s' % str(e))
            raise e
        except Exception as e:
            self.log.error(e)
            raise e

        try:
            with  connection.cursor() as cursor:
                outputlist = []

                if not output:
                    sql = 'select * from %s where %s' % (tablename, where)

                if isinstance(output, list):
                    sql = 'select %s from %s where %s' % (','.join(output), tablename, where)

                if isinstance(output, str):
                    sql = 'select %s from %s where %s' % (output, tablename, where)

                cursor.execute(sql)
                result = cursor.fetchall()

                if dict_:
                    return result

                if result is None or isinstance(result, tuple):
                    return None

                for res_ in result:
                    r = []
                    if isinstance(output, list):
                        for item in output:
                            r.append(res_[item])
                        outputlist.append(r)
                    if isinstance(output, str):
                        outputlist.append(res_[output])

                if not output:
                    outputlist = result

                # if len(outputlist)==1 and isinstance(outputlist[0],str):
                #     return outputlist[0]
                # else:
                return outputlist
        finally:
            connection.close()


if __name__ == '__main__':
    Op_Mysql().Insert_Query(tablename=None, column=None, datas=None)
