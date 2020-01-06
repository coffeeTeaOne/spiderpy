import json
import random
import redis
import sys
import time

from rediscluster import StrictRedisCluster

from Env.parse_yaml import DBConfigParser


class RedisClient(object):

    def __init__(self, name='common', db=0, host=None, port=None):
        if host is None and port is None:
            # self.config = DBConfigParser().get_config(server='redis_common', key='localhostconn')
            # self.config = DBConfigParser().get_config(server='redis_common', key='41conn')
            # self.config = DBConfigParser().get_config(server='redis_wechat', key='localhostconn')
            # self.config = DBConfigParser().get_config(server='redis_wechat', key='41conn')
            self.config = DBConfigParser().get_config(server='redis_common_colony', key='colony')
            # self.config = DBConfigParser().get_config(server='redis_common_colony', key='105-62-93colony')
            self.host = self.config.get('host')
            self.port = self.config.get('port')
            self.db = self.config.get('db')
            if '|' in self.host:
                host_list = self.host.split('|')
                redis_nodes = []
                for ho in host_list:
                    redis_nodes.append({'host': str(ho), 'port': self.port, 'db': self.db})
                self.conn = StrictRedisCluster(startup_nodes=redis_nodes)
            else:
                self.conn = redis.Redis(host=self.host, port=self.port, db=self.db)

        else:
            self.host = host
            self.port = port
            self.db = db
            self.conn = redis.Redis(host=self.host, port=self.port, db=self.db)
        self.name = name

    def get(self):
        """
        随机从redis里获取一个ip
        :return:
        """
        key = self.conn.hgetall(name=self.name)
        # print(key)
        rkey = random.choice(list(key.keys())) if key else None
        if isinstance(rkey, bytes):
            return rkey.decode('utf-8')
        else:
            return rkey

    def save(self, key):
        """
        保存ip
        :param key:
        :return:
        """
        key = json.dumps(key) if isinstance(key, (dict, list)) else key
        return self.conn.hincrby(self.name, key, str(int(time.time())))

    def get_value(self, key):
        """
        获取ip的值
        :param key:
        :return:
        """
        value = self.conn.hget(self.name, key)
        return value if value else None

    def pop(self):
        """
        获取一个ip并从池中删除
        :return:
        """
        key = self.get()
        if key:
            self.conn.hdel(self.name, key)
        return key

    def del_ip(self, key):
        """
        删除指定ip
        :param key:
        :return:
        """
        self.conn.hdel(self.name, key)

    def del_all(self):
        """
        删除该表所有ip
        :return:
        """
        self.conn.flushdb()

    def get_all(self):
        """
        获取所有的ip
        :return:
        """
        if sys.version_info.major == 3:
            return [key.decode('utf-8') for key in self.conn.hgetall(self.name).keys()]
        else:
            return self.conn.hgetall(self.name).keys()

    def get_count(self):
        """
        获取池里ip数量
        :return:
        """
        return self.conn.hlen(self.name)


if __name__ == '__main__':
    # redis_con = RedisClient('proxy', '172.22.69.41', 6379,db=0)
    redis_con = RedisClient()
    print(redis_con.get())
