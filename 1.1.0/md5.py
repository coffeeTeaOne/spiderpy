# coding=gbk

import hashlib
import os


def GetFileMd5(filename):
    if not os.path.isfile(filename):
        return False
    myhash = hashlib.md5()
    f = open(filename, 'rb')
    while True:
        b = f.read(8096)
        if not b:
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()


def get_file_md5(file_path):
    """
    获取文件md5值
    :param file_path: 文件路径名
    :return: 文件md5值
    """
    with open(file_path, 'rb') as f:
        md5obj = hashlib.md5()
        md5obj.update(f.read())
        _hash = md5obj.hexdigest()
    return str(_hash).upper()


def traverse(f):
    fs = os.listdir(f)
    for f1 in fs:
        tmp_path = os.path.join(f, f1)
        if '__pycache__' not in tmp_path and \
            '.git' not in tmp_path and \
                'AntiWord' not in tmp_path and \
                '.idea' not in tmp_path and \
                '\File\\' not in tmp_path and \
                '\LICENSE' not in tmp_path and \
                'Logs\icrawlerspider' not in tmp_path and \
                '\md5' not in tmp_path and \
                '\README' not in tmp_path and \
                '\scrapy.cfg' not in tmp_path and \
                '\ThirdSource' not in tmp_path and \
                'wechat_title' not in tmp_path:
            if not os.path.isdir(tmp_path):
                print(tmp_path)
                md5 = get_file_md5(tmp_path)
                with open('./md5.txt', 'a') as w:
                    w.write('{}: {}'.format(tmp_path, md5) + '\n')
                    print('{}: {}'.format(tmp_path, md5))
            else:
                traverse(tmp_path)


if __name__ == '__main__':

    path = '.\\'
    traverse(path)
    # print(get_file_md5(path))




