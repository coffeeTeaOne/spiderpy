# encoding: utf-8
import os


class CookieMidderWare:
    def __init__(self, path):
        self.path = path

    def Get_Cookie(self):
        # os.system("python "+self.path)
        p = os.popen("python " + self.path)  # linux可能是python3
        return p.read()
