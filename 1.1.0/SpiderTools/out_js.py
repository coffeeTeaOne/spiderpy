# encoding: utf-8
import execjs
import json
import os

path = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/') + "/js/"


# 执行本地的js
# class Js_Path:

class Fun_Js:

    def __init__(self, cookie_path=None):
        self.cookie_path = cookie_path

    def Get_Js(self, funname=None, data=None, param=None):
        jsstr = self.Conn_Js()
        ctx = execjs.compile(jsstr)
        if data is None and param is not None:
            c_ = ctx.call(funname, param)
        elif data is None and param is None:
            c_ = ctx.call(funname)
        else:
            c_ = ctx.call(funname, data, param)
        return c_

    def Conn_Js(self):

        htmlstr = ''

        file = [path + 'json.js', path + 'jsonPath.js', path + 'function.js']
        # File = []
        if self.cookie_path != None:
            file.append(self.cookie_path)

        for filename in file:
            with open(filename, 'r', encoding='UTF-8') as f:
                for line in f:
                    htmlstr = htmlstr + line
                htmlstr = htmlstr + '\n'

        return htmlstr

        # f = open(path+"function.js", 'r', encoding='UTF-8')
        # a = open(path+"json.js", 'r', encoding='UTF-8')
        # b = open(path+"jsonPath.js", 'r', encoding='UTF-8')
        # d = open(path + "jquery-1.11.1.min.js", 'r', encoding='UTF-8')
        # e = open(path + "jquery-ui.min.js", 'r', encoding='UTF-8')
        #
        # line = f.readline()
        # line_a = a.readline()
        # line_b = b.readline()
        # line_d = d.readline()
        # line_e = e.readline()
        #
        # htmlstr = ''
        # while line_a:
        #     htmlstr = htmlstr + line_a
        #     line_a = a.readline()
        # while line_b:
        #     htmlstr = htmlstr + line_b
        #     line_b = b.readline()
        # while line:
        #     htmlstr = htmlstr + line
        #     line = f.readline()
        # while line:
        #     htmlstr = htmlstr + line_d
        #     line_d = d.readline()
        # while line:
        #     htmlstr = htmlstr + line_e
        #     line_e = e.readline()
        #
        # if self.cookie_path != None:
        #     c = open(self.cookie_path, 'r', encoding='UTF-8')
        #     line_c = c.readline()
        #     while line_c:
        #         htmlstr = htmlstr + line_c
        #         line_c = c.readline()
        # print(htmlstr)
        # return htmlstr


if __name__ == '__main__':
    a = {"qxrUp": "Y", "pageSize": "12", "CATEGORY": "02", "channelIds[]": "ygzxl", "Accept": "text/html, */*; q=0.01",
         "Accept_Language": "en-US,en;q=0.9", "Host": "www.cebbank.com"}
    for i in range(10000):
        data = Fun_Js().Get_Js(funname='Templet', data=a, param="reference['Host']")
        print(data)
