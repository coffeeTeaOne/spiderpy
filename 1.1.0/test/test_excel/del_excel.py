from openpyxl import *
filename = './example.xls'
wb = load_workbook(filename)
ws = wb.active
ws.delete_rows(1,1) #删除index为2后面的2行
wb.save(filename)