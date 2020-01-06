# encoding: utf-8
from pymongo import MongoClient
from Env.parse_yaml import DBConfigParser
from SpidersLog.icrwler_log import ICrawlerLog
# 有用
from bson.objectid import ObjectId
import pymongo
import time
import traceback
from pymongo.errors import *


class Mo_config:
    DB = 'Spider'
    COLLECTION = 'business'

    def __init__(self, host=None, port=None, db=None, coll=None, key=None, contimeout=None, conn=None, *args, **kwargs):
        # config = DBConfigParser().get_config(server='mongodb', key='73-81-102conn')
        # config = DBConfigParser().get_config(server='mongodb', key='69conn')
        config = DBConfigParser().get_config(server='mongodb', key='localhostconn')
        # config = DBConfigParser().get_config(server='mongodb', key='67.25conn')
        # config = DBConfigParser().get_config(server='mongodb', key='69.41conn')

        self.host = host
        self.port = port
        self.db = db
        self.coll = coll
        self.key = key
        self.conn = conn
        super(Mo_config, self).__init__()

        self.contimeout = contimeout
        if host is None:
            self.host = config['host']
        if port is None:
            self.port = config['port']
        if not isinstance(self.port, int):
            raise TypeError("port must be an instance of int")
        if db is None:
            self.db = self.DB
        if coll is None:
            self.coll = self.COLLECTION
        if contimeout is None:
            self.contimeout = 60
        if key is None or key == 'None':
            self.key = 'URL_'

    def conn_mongo(self):
        # conn = MongoClient(host,port)
        # serverSelectionTimeoutMS 如果不想等待这么久可以设置低点
        if '|' in self.host:
            host_port = ["{}:{}".format(i, str(self.port)) for i in str(self.host).split('|')]
            conn = MongoClient(host_port,
                               connect=False,
                               connectTimeoutMS=self.contimeout,
                               serverSelectionTimeoutMS=60)
        else:

            conn = MongoClient('%s:%d' % (self.host, self.port),
                               connect=False,
                               connectTimeoutMS=self.contimeout,
                               serverSelectionTimeoutMS=60)
        return conn

    def reconnect(self, op, method, data=None):  # 数据库重新连接可能会导致数据量temp,fixed多一条少一条

        log = ICrawlerLog('spider').save

        result = False
        try:
            result = eval(op)
        except DuplicateKeyError as e:  # 插入重复
            log.info('数据重复')
            log.info(e)
            return 'duplicate'
        except ServerSelectionTimeoutError as e:  # 连接超时重试, 未进入重连, 疑是 ServerSelectionTimeoutError 未被正常捕获
            n = 0
            for i in range(5):
                try:
                    log.info('%s %s %d time reconnection.....' % (str(e), method, i))
                    result = eval(op)
                    log.info('网络错误, 重连插入,{}'.format(op))
                    break
                except:
                    n = n + 1
                    time.sleep(3)
                    result = 'duplicate'
            if n > 4:
                raise Exception(' %s reconnection time pass 5 time' % method)
        except NetworkTimeout as e:  # 连接超时重试
            n = 0
            for i in range(5):
                try:
                    log.info('%s %s %d time reconnection.....' % (str(e), method, i))
                    result = eval(op)
                    log.info('网络错误, 重连插入,{}'.format(op))
                    break
                except:
                    n = n + 1
                    time.sleep(3)
                    result = 'duplicate'
            if n > 4:
                raise Exception('data %s reconnection time pass 5 time' % method)
        except InvalidOperation as e:
            raise Exception(e, '#########data other error data is ', data)
        except Exception as e:
            # raise Exception('%s mongodb other exception : ' %method, e)   # 原代码逻辑,
            n = 0
            # print('丢掉 mongo 连接')
            for i in range(5):
                try:
                    log.info('%s %s %d time reconnection.....' % (str(e), method, i))
                    result = eval(op)
                    if result != 'duplicate' or result != False:
                        log.info('网络错误, 重连插入成功,{}'.format(op))
                    else:
                        log.error('网络错误, 重连插入失败,{}'.format(op))
                    break
                except:
                    n = n + 1
                    time.sleep(3)
                    result = 'duplicate'
            if n > 4:
                raise Exception(' %s reconnection time pass 5 time' % method)
        return result

    def conn_db_coll(self, ):
        # conn = self.conn_mongo()
        db = self.conn[self.db]
        if not db:
            raise Exception('mongodb没有该Database:', self.db, ',请检查')
        collection = db[self.coll]
        if not collection:
            raise Exception('mongodb没有该Database：', self.db, ' 或者该Collection:', self.coll, ',请检查')
        log = ICrawlerLog('spider').save

        # indexname = collection.index_information()
        # print(indexname)

        if self.key == 'null':  # or (self.key + '_1') in indexname:
            pass
        else:
            try:
                # collection.ensure_index(self.key, unique=True)
                collection = self.deal_index(collection)  # 动态创建索引
            except pymongo.errors.DuplicateKeyError:
                pass
            except pymongo.errors.ServerSelectionTimeoutError as e:
                n = 0
                for i in range(5):
                    try:
                        log.info('%s collection %d time reconnection.....' % (str(e), i))
                        collection = self.deal_index(collection)
                        break
                    except:
                        n = n + 1
                        time.sleep(2)
                if n > 4:
                    self.close_mongo()
                    raise Exception('collection reconnection time pass 5 time')
            except Exception as e:
                n = 0
                for i in range(5):
                    try:
                        log.info('%s collection %d time reconnection.....' % (str(e), i))
                        collection = self.deal_index(collection)
                        break
                    except:
                        n = n + 1
                        time.sleep(2)
                if n > 4:
                    self.close_mongo()
                    raise Exception('collection reconnection time pass 5 time')
                raise e
        #  返回 Mongo 连接对象
        return collection

    def close_mongo(self):
        # self.conn = self.conn_mongo()
        # self.conn.close()
        pass

    def deal_index(self, collection):
        try:
            indexname = [indx['name'] for indx in collection.list_indexes()]
        except Exception as e:
            self.close_mongo()
            raise Exception(e)

        for i_ in indexname:
            if '_id_' == i_ or self.key + '_1' == i_:  # ('key', SON([('URL_', 1)])), ('name', 'URL__1') 键与键名
                continue
            else:
                try:
                    collection.drop_index(i_)  # 删除指定索引
                except pymongo.errors.OperationFailure:
                    pass
                except Exception as e:
                    self.close_mongo()
                    raise Exception(e)
        collection.ensure_index(self.key, unique=True)  # 设置主键
        return collection


class Op_MongoDB(Mo_config):

    def S_Mongodb(self, collection=None, output=None, where=None, match=None):
        try:
            col = self.conn_db_coll()
            result = []
            if where is not None:
                coll = col.find(where)
            elif match is not None:
                coll = col.find(match)
            else:
                coll = col.find()
            for item in coll:
                install = []
                oinstall = []
                if (collection is None and output is None and where is None) or output == 'all' \
                        or (collection is None and output is None):
                    result.append(item)
                elif output is not None:
                    if isinstance(output, str):
                        result.append(item[output])
                    elif isinstance(output, list):
                        for o in output:
                            oinstall.append(item[o])
                        result.append(tuple(oinstall))
                else:
                    if isinstance(collection, list):
                        for col in collection:
                            install.append(item[col])
                        result.append(install)
                    elif isinstance(collection, str):
                        result.append(item[col])
        except Exception as e:
            raise e
        finally:
            self.close_mongo()
        return result

    def S_Mongodb_One(self, collection=None, where=None, match=None):
        try:
            col = self.conn_db_coll()
            if where is not None:
                coll = col.find_one(where)
            elif match is not None:
                coll = col.find_one(match)
            else:
                coll = col.find_one()
            self.close_mongo()
        except Exception as e:
            raise e
        finally:
            self.close_mongo()
        return coll

    def I_Mongodb(self, data):

        op = '%s.insert(%s)' % ('self.conn_db_coll()', data)
        try:
            status = self.reconnect(op=op, method='insert', data=data)
        except Exception as e:
            raise e
        finally:
            self.close_mongo()
        return status

    def U_Mongodb(self, query, update, upsert=False, multi=False):
        '''
        query : update的查询条件，类似sql update查询内where后面的。
        update : update的对象和一些更新的操作符（如$,$inc...）等，也可以理解为sql update查询内set后面的
        upsert : 可选，这个参数的意思是，如果不存在update的记录，是否插入objNew,true为插入，默认是false，不插入。
        multi : 可选，mongodb 默认是false,只更新找到的第一条记录，如果这个参数为true,就把按条件查出来多条记录全部更新。
        writeConcern :可选，抛出异常的级别。
        :param query:
        :param update:
        :param upsert:
        :return:
        '''
        op = '%s.update(%s, %s, %s, %s)' % ('self.conn_db_coll()', query, update, upsert, multi)
        try:
            result = self.reconnect(op=op, method='update')
        except Exception as e:
            raise e
        finally:
            self.close_mongo()

        return result

        # try:
        #   coll.update(query ,update,upsert,multi)
        # except Exception as e:
        #     print(e)
        #     print('str(Exception):', str(Exception))
        #     print('str(e):', str(e))
        #     print('repr(e):', repr(e))
        #     print('e.message:', e.message)
        #     print('traceback.print_exc():',traceback.print_exc())
        #     print('traceback.format_exc():\n%s' % traceback.format_exc())

    def R_Mongodb(self, condition):
        coll = self.conn_db_coll()
        try:
            coll.remove(condition)
        except Exception as e:
            raise e
        finally:
            self.close_mongo()

    def S_Mongodb_List(self, collection=None, output=None, where=None, match=None):
        try:
            col = self.conn_db_coll()
            result = []
            if where is not None:
                coll = col.find(where)
            elif match is not None:
                coll = col.find(match)
            else:
                coll = col.find()
            for item in coll:
                install = []
                oinstall = []
                if (collection is None and output is None and where is None) or output == 'all' or (
                        collection is None and output is None):
                    result.append(item)
                elif output is not None:
                    if isinstance(output, str):
                        result.append(item[output])
                    elif isinstance(output, list):
                        for o in output:
                            oinstall.append(item[o])
                        result.append(oinstall)
                else:
                    if isinstance(collection, list):
                        for col in collection:
                            install.append(item[col])
                        result.append(install)
                    elif isinstance(collection, str):
                        result.append(item[col])
        except Exception as e:
            raise e
        finally:
            self.close_mongo()
        return result

    def Rename_Mongodb(self, newdb):
        col = self.conn_db_coll()
        try:
            col.rename(new_name=newdb)
            return True
        except:
            return False
        finally:
            self.close_mongo()


if __name__ == '__main__':
    do_mongo = Op_MongoDB()

    do_mongo.S_Mongodb_One(where={'userid': 1})
    # do_mongo.I_Mongodb(data={'one': 1, 'two': 2})
    # o = DBConfigParser().get_config(server='mongodb', key='73-81-102conn')
    # print(o)
    # print(type(o))
    # print(["{}:{}".format(i, '21017')for i in o['host'].split('|')])
