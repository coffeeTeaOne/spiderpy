# encoding: utf-8
import os
import yaml


class DBConfigParser(object):
    config_file = os.path.dirname(os.path.realpath(__file__)) + '/EnvConfig/dbconfig.yaml'
    configs = yaml.load(open(config_file, 'r'))

    @classmethod
    def get_config(cls, server, key=None):
        if server == 'mysql':
            server = 'mysql.config'
        if server == 'mongodb':
            server = 'mongodb.config'
        if server == 'redis_common':
            server = 'redis.config.common'
        if server == 'redis_wechat':
            server = 'redis.config.wechat'
        if server == 'redis_common_colony':
            server = 'redis.config.colony'
        section = cls.configs.get(server, None)
        if section is None:
            raise NotImplementedError
        value = section.get(key, None)
        if value is None:
            raise NotImplementedError
        dbconfig = {}
        for v in value.split(' '):
            na = v.split(':')[0]
            va = v.split(':')[1]
            if na == 'port':
                va = int(va)
            dbconfig[na] = va
        return dbconfig

    @classmethod
    def get_data_db(cls):
        config = cls.get_config(server='mongodb', key='69conn')
        return config['datadb']

    @classmethod
    def get_fixed_db(cls):
        config = cls.get_config(server='mongodb', key='69conn')
        return config['fixeddb']

    @classmethod
    def get_temp_db(cls):
        config = cls.get_config(server='mongodb', key='69conn')
        return config['tempdb']


class FileConfigParser(object):
    config_file = os.path.dirname(os.path.realpath(__file__)) + '/EnvConfig/filepathconfig.yaml'
    configs = yaml.load(open(config_file, 'r'))

    @classmethod
    def get_config(cls, server, key=None):
        section = cls.configs.get(server, None)
        if section is None:
            raise NotImplementedError
        value = section.get(key, None)
        if value is None:
            raise NotImplementedError
        fileconfig = {}
        for v in value.split(' '):
            na = v.split(':')[0]
            va = v.split(':')[1]
            if na == 'port':
                va = int(va)
            fileconfig[na] = va
        return fileconfig

    @classmethod
    def get_path(cls, server, key):
        config = cls.get_config(server=server, key=key)
        return config['path']

# if __name__ == '__main__':
#     mysql_conn = ConfigParser().get_config(server='mongodb',key='69conn')
#     print(mysql_conn['host'])
