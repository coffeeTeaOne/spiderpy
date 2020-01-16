import xlrd
import xlwt
from xlutils.copy import copy
import os.path
rb = xlrd.open_workbook('C:/Users/lyial/Desktop/test_spiderpy/1.1.0/test/test_excel/example.xls',formatting_info=True)
r_sheet = rb.sheet_by_index(0)
wb = copy(rb)
sheet = wb.get_sheet(0)
sheet.write(5,12,"string")
wb.save('example.xls')