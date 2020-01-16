# coding:utf-8
from xlutils.copy import copy

import xlrd
import xlwt
import os
import pandas as pd
from pandas import DataFrame

class Excel_funtion:
    def __init__(self,excel_filename,sheet_name=''):
        self.excel_filename=excel_filename  # 要操作的excel，要给绝对路径
        self.mode = 1
        self.book = xlrd.open_workbook(self.excel_filename)
        self.handle = copy(self.book)
        if sheet_name == '':
            self.sheet = self.book.sheet_by_index(0)
            self.sheet_name = "sheet"
            self.handle_sheet = self.handle.get_sheet(0)
        else:
            try:
                self.sheet_name = sheet_name
                self.sheet = self.book.sheet_by_name(sheet_name)
                self.handle_sheet = self.handle.get_sheet(sheet_name)
            except:
                print("not "+sheet_name+" in "+ excel_filename) # 在ecxcl里不存在 sheet_name

    def xlsread_matching_data(self, matching_value):
        if self.mode == 1:
            # print("fond data : ", matching_value)
            seat_list = []
            for i in range(self.sheet.ncols):
                seat = []
                for n in range(self.sheet.nrows):
                    if matching_value == self.sheet.cell(n, i).value:
                        seat_value = n, i
                        seat.append(seat_value)
                if seat != []:
                    seat_list.append(seat)
            return seat_list
        else:
            return 'error: not file.'

class ExcelPandas:

    def read_all_excel(self):
        # pd.read_excel(io, sheet_name=0, header=0, names=None, index_col=None, usecols=None)
        """
        sheet_name：返回指定的sheet，如果将sheet_name指定为None，则返回全表，如果需要返回多个表，可以将sheet_name指定为一个列表，例如['sheet1', 'sheet2']
        header：指定数据表的表头，默认值为0，即将第一行作为表头。
        usecols：读取指定的列，例如想要读取第一列和第二列数据：
        pd.read_excel("example.xlsx", sheet_name=None, usecols=[0, 1])
        """
        data = pd.read_excel('example.xls', sheet_name='test')
        print(data)

    def update_excel(self):
        # 读取文件
        data = pd.read_excel("example.xls", sheet_name="test")
        # 找到gender这一列，修改
        # data['gender'][data['gender'] == 110] = 0
        # data['gender'][data['gender'] == 111] = 1
        # 添加一列并赋值
        # data['tea'] = [1,2,3]
        # 保存
        DataFrame(data).to_excel('example.xls', sheet_name='test', index=False, header=True)
        print(data)

    def insert_excel(self):
        data = pd.read_excel("example.xls", sheet_name="test")
        data.loc[1] = [1,2,3,4,5]
        DataFrame(data).to_excel('example.xls', sheet_name='test', index=False, header=True)
        print(data)

    def delete_excel(self):
        data = pd.read_excel("example.xls", sheet_name='test')

        # 删除gender列，需要指定axis为1，当删除行时，axis为0
        # data = data.drop('gender', axis=1)

        # 删除第3,4行，这里下表以0开始，并且标题行不算在类
        data = data.drop([0, 1], axis=0)

        # 保存
        DataFrame(data).to_excel('example.xls', sheet_name='test', index=False, header=True)


if __name__ == '__main__':
    filename = os.path.dirname(__file__) + '/mongo.xls'
    ex = Excel_funtion(excel_filename=filename, sheet_name='spider_data')