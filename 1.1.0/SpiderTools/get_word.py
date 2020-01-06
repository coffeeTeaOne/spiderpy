# encoding: utf-8
import docx
from staticparm import root_path
from SpiderTools.tool import platform_system


def get_word_content(dir, name):
    '''解析word内容并返回值
    :param dir: 路径
    :param name: 文件名
    :return:
    '''
    str = name.split('.')
    if str[1] == 'docx':
        # 获取文档对象
        file = docx.opendocx(dir + name)
        file = docx.getdocumenttext(file)
    else:
        # #window下
        if platform_system() == 'Windows':
            from win32com import client as wc
            word = wc.Dispatch('Word.Application')
            file = word.Documents.Open(dir + name)  # 目标路径下的文件
            file.SaveAs(dir + name + 'x', 12, False, "", True, "", False, False, False, False)  # 转化后路径下的文件
            file.Close()
            word.Quit()
            file = docx.opendocx(dir + name + 'x')
            file = docx.getdocumenttext(file)

        # linux下
        if platform_system() == 'Linux':
            import subprocess
            content = subprocess.check_output(["%s/AntiWord/antiword/antiword" % root_path, dir + name])
            file = content.decode()

    return '|'.join(file)
