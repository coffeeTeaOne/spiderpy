from xlutils.copy import copy

import xlrd
import xlwt
import os


class Excel_funtion:
    def __init__(self,excel_filename,sheet_name=''):
        self.excel_filename=excel_filename#要操作的excel，要给绝对路径
        #存在两种模式：
        #1. 文件不存在，当文件不存在只能新建，初始操作只能为写; 为  mode=0
        #2. 文件存在,不能新建重名重位置的文件，能读写，增删改查; 为  mode=1
        if not os.path.exists(self.excel_filename):
            print("not file "+self.excel_filename)
            self.mode = 0
            self.new_book = xlwt.Workbook(encoding='utf-8')#, style_compression=0)
            #style_compression:表示是否压缩，不常用。
            # cell_overwrite_ok，表示是否可以覆盖单元格，其实是Worksheet实例化的一个参数，默认值是False
            if sheet_name == '':
                self.sheet_name = "sheet"#默认页名称 sheet
                self.sheet = self.new_book.add_sheet(self.sheet_name,cell_overwrite_ok=True)
            else:
                self.sheet_name = sheet_name
                self.sheet = self.new_book.add_sheet(self.sheet_name,cell_overwrite_ok=True)
        else:
            print("open file "+self.excel_filename)
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

    # 总行数和总列数
    def xlsread_info(self):
        if self.mode == 1:
            print("file: " + self.excel_filename)
            print("sheet name: " + self.book.sheet_names()[0])
            nrows = self.sheet.nrows  # 获取行总数
            print("nrows: ", nrows)
            ncols = self.sheet.ncols  # 获取列总数
            print("ncols: ", ncols)
            return nrows, ncols
        else:
            print(self.excel_filename + u" 不存在,无法进行操作!!!")
            return 'error: not file.'

    # 获取所有内容;返回 excel里所有数据
    def xlsread_data(self):
        if self.mode == 1:
            data_list = []
            for i in range(self.sheet.nrows):
                data_list.append(self.sheet.row_values(i))
            return data_list
        else:
            print(self.excel_filename + u" 不存在,无法进行操作!!!")
            return 'error: not file.'

    # 以行或者列返回数据,返回 excel里所有数据
    # 每行打印 return data
    def xlsread_allnrows(self):
        if self.mode == 1:
            data_list = []
            for i in range(self.sheet.nrows):
                data = []
                for n in range(self.sheet.ncols):
                    if self.sheet.cell(i, n).value != '':
                        data.append(self.sheet.cell(i, n).value)
                data_list.append(data)
            return data_list
        else:
            print(self.excel_filename + u" 不存在,无法进行操作!!!")
            return 'error: not file.'

    # 以行或者列返回数据,返回 excel里所有数据
    # 每列打印 return data
    def xlsread_allncols(self):
        if self.mode == 1:
            data_list = []
            for i in range(self.sheet.ncols):
                data = []
                for n in range(self.sheet.nrows):
                    if self.sheet.cell(n, i).value != '':
                        data.append(self.sheet.cell(n, i).value)
                data_list.append(data)
            return data_list
        else:
            print(self.excel_filename + u" 不存在,无法进行操作!!!")
            return 'error: not file.'

    # 每行打印 return data
    # 4.获取匹配指定位置的数据xls.xlsred(nrows_number, ncols_number)返回指定位置的数据
    def xlsred(self, nrows_number, ncols_number):
        if self.mode == 1:
            str = self.sheet.cell(nrows_number, ncols_number).value
            print("read data : ", str)
            print("Data-ncols: ", nrows_number)
            print("Data-number: ", ncols_number)
            return str
        else:
            print(self.excel_filename + u" 不存在,无法进行操作!!!")
            return 'error: not file.'

    # 4.查找指定数据在表中的哪些位置xls.xlsread_matching_data(matching_value)返回这个数据在哪些位置
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
            print(self.excel_filename + u" 不存在,无法进行操作!!!")
            return 'error: not file.'

    # 写操作 写入数据   return x,y
    def excelwrite(self, data, nrows_number, ncols_number):
        if self.mode == 0:
            self.sheet.row(nrows_number).write(ncols_number, data)
            self.new_book.save(self.excel_filename)
            return nrows_number + 1, ncols_number + 1
        else:
            print(self.excel_filename + u" 已存在,无法再次创建重名文件和写操作!!!")
            return 0, 0

    # 对指定行写入数据
    def nrows_write(self, data_list, nrows_number):
        if self.mode == 0:
            for i, item in enumerate(data_list):
                self.sheet.row(nrows_number).write(i, item)
            self.new_book.save(self.excel_filename)
            # return letter(nrows_number), i + 1
        else:
            print(self.excel_filename + u" 已存在,无法再次创建重名文件和写操作!!!")
            return 0, 0

    # 对指定列写入数据
    def ncols_write(self, data_list, ncols_number):
        if self.mode == 0:
            for i, item in enumerate(data_list):
                self.sheet.row(i).write(ncols_number, item)
            self.new_book.save(self.excel_filename)
            # return letter(i + 1), ncols_number + 1
        else:
            print(self.excel_filename + u" 已存在,无法再次创建重名文件和写操作!!!")
            return 0, 0

    # 对字典进行数据写入
    def dict_write(self, data_dict):
        if self.mode == 0:
            # 判断写入的数据类型是否为字典
            if type(data_dict).__name__ == 'dict':
                nrows_number = 0
                ncols_number = 0
                for key in data_dict:
                    # 一行一行的写
                    self.sheet.row(nrows_number).write(ncols_number, key)
                    self.sheet.row(nrows_number).write(ncols_number + 1, data_dict[key])
                    nrows_number += 1
                    ncols_number = 0
                self.new_book.save(self.excel_filename)
                # return nrows_number + 1, letter(ncols_number + 1)
            else:
                print("data not is dict type.")
                return 0, 0
        else:
            print(self.excel_filename + u" 已存在,无法再次创建重名文件和写操作!!!")
            return 0, 0

    # 增加数据， 找到最后一行进行增加一行数据，从第指定列开始增加
    def add_nrows(self, data, ncols_number):
        if self.mode == 1:
            # 找到最后一行
            nrows_number = self.sheet.nrows
            for i, item in enumerate(data):
                self.handle_sheet.write(nrows_number, i + ncols_number, item)
            self.handle.save(self.excel_filename)
            # return nrows_number + 1, letter(i + ncols_number + 1)
        else:
            print(self.excel_filename + u" 不存在,无法进行操作!!!")
            return 'error: not file.'

    # 增加数据， 最后位置行或列从指定开始位置增加字典数据
    # methods = nrows 每行开始增加
    # methods = ncols 每列开始增加
    def add_dict(self, data, methods="nrows", start_number=0):
        if self.mode == 1:
            # 找到最后一行一列
            nrows_number = self.sheet.nrows
            ncols_number = self.sheet.ncols
            if type(data).__name__ == 'dict':
                if methods == "nrows":
                    ncols_start = start_number
                    for key in data:
                        self.handle_sheet.write(nrows_number, ncols_start, key)
                        self.handle_sheet.write(nrows_number, ncols_start + 1, data[key])
                        nrows_number += 1
                        ncols_start = start_number
                    self.handle.save(self.excel_filename)
                    # return nrows_number, letter(ncols_start + 2)
                elif methods == "ncols":
                    nrows_start = start_number
                    for key in data:
                        self.handle_sheet.write(nrows_start, ncols_number, key)
                        self.handle_sheet.write(nrows_start + 1, ncols_number, data[key])
                        ncols_number += 1
                        nrows_start = start_number
                    self.handle.save(self.excel_filename)
                    # return nrows_start + 2, letter(ncols_number)
                else:
                    print("methods only be nrows or ncols.")
                    # return nrows_number, letter(ncols_number + 1)
            else:
                print("data not is dict type.")
                # return nrows_number, letter(ncols_number + 1)
        else:
            print(self.excel_filename + u" 不存在,无法进行操作!!!")
            return 'error: not file.'

    # 替换到全表的某个值
    # 首选找出这个值在表中的所有位置，再将其替换
    # 返回被更改的数据个数
    def replace_data(self, data, new_data):
        if self.mode == 1:
            replace_number = 0
            for i in range(self.sheet.ncols):
                for n in range(self.sheet.nrows):
                    if data == self.sheet.cell(n, i).value:
                        self.handle_sheet.write(n, i, new_data)
                        replace_number += 1
            self.handle.save(self.excel_filename)
            return replace_number
        else:
            print(self.excel_filename + u" 不存在,无法进行操作!!!")
            return 'error: not file.'

    # 删除指定数据
    def del_value(self, data):
        if self.mode == 1:
            replace_number = 0
            for i in range(self.sheet.ncols):
                for n in range(self.sheet.nrows):
                    if data == self.sheet.cell(n, i).value:
                        self.handle_sheet.write(n, i, '')
                        replace_number += 1
            self.handle.save(self.excel_filename)
            return replace_number
        else:
            print(self.excel_filename + u" 不存在,无法进行操作!!!")
            return 'error: not file.'

    # 删除行
    def del_nrows(self, data,condition):
        """
        :param data: 第一行的哪一列的值
        :param condition: 删除指定行的条件
        :return:
        """
        if self.mode == 1:
            all_nrows = ex.xlsread_data()  # 第一行
            # first_nrows = ex.xlsread_data()[0][0]  # 第一行
            # first_ncols = ex.xlsread_allncols()[0][0]  # 第一列
            all_ncols = ex.xlsread_allncols()  # 所有列
            ncols_index = all_nrows[0].index(data)
            result = all_ncols[ncols_index]
            for i in range(len(result)):
                if result[i] == condition:
                    del all_nrows[i]

            pass

            self.handle.save(self.excel_filename)

        else:
            print(self.excel_filename + u" 不存在,无法进行操作!!!")
            return 'error: not file.'

    # 删除列
    def del_ncols(self, data):
        if self.mode == 1:
           pass
        else:
            print(self.excel_filename + u" 不存在,无法进行操作!!!")
            return 'error: not file.'



if __name__ == '__main__':
    filename = os.path.dirname(__file__) + '/mongo.xls'
    ex = Excel_funtion(excel_filename=filename,sheet_name='spider_data')

    # 查询数据
    # print(ex.xlsread_info()) # 获取所有内容;返回 excel里所有数据
    # print(ex.xlsread_data())  # 获取所有内容;返回 excel里所有数据,按行打印
    # print(ex.xlsread_allncols())  # 获取所有内容;返回 excel里所有数据,按列打印
    # print(ex.xlsred(nrows_number=1, ncols_number=0))  # 返回指定位置的数据
    print(ex.xlsread_matching_data(matching_value='JRCP_BX'))  # 返回值的坐标

    # 没有excel表格，创建插入数据
    # ex.excelwrite(data='why', nrows_number=5, ncols_number=5)
    # ex.nrows_write(data_list=[1,2,3,4,5], nrows_number=5)

    # 已有表添加数据
    # ex.add_nrows(data=[1,2,3,4,5,6], ncols_number=5)  # 增加数据， 找到最后一行进行增加一行数据，从第指定列开始增加
    # ex.add_dict(data={'m':23,'n': 89}, methods="ncols", start_number=3) # 增加数据， 最后位置行或列从指定开始位置增加字典数据

    # 替换数据
    # ex.replace_data(data='new_string', new_data='string')  # 替换到全表的某个值,同一个表有这些值不予替换

    # 删除数据
    # ex.del_value(data='string')


