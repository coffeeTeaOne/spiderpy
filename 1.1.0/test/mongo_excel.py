import pymongo
import os
import xlrd
import xlwt
import time
import xlwings as xw
from xlutils.copy import copy


client = pymongo.MongoClient(host="localhost", port=27017)
# client = pymongo.MongoClient(host="172.22.69.35", port=20000)


def save_file(data):
    """
    保存excel文件
    :param filename:
    :param data:
    :return:
    """
    sheet_name = 'test'
    filepath_out = r'C:\Users\lyial\Desktop\test.xls'

    # 分文件存在和不存在的情况引用excel和sheet
    if os.path.exists(filepath_out):
        rexcel = xlrd.open_workbook(filepath_out, encoding_override=True,)
        wexcel = copy(rexcel)
        wsheet = wexcel.get_sheet(sheet_name)
        # data = {
        #     "序号": ["姓名", "语文", "数学", "英语"],
        #     "1": ["张三", 130, 120, 100],
        #     "2": ["李四", 100, 110, 120],
        #     "3": ["王五", 125, 135, 135]
        # }
        r = 0

        for i, j in data.items():  # i表示data中的key，j表示data中的value
            le = len(j)  # values返回的列表长度
            if r == 0:
                wsheet.write(r, 0, i)  # 添加第 0 行 0 列数据单元格背景设为黄色
            else:
                wsheet.write(r, 0, i, )  # 添加第 1 列的数据

            for c in range(1, le + 1):  # values列表中索引
                if r == 0:
                    wsheet.write(r, c, j[c - 1])  # 添加第 0 行，2 列到第 5 列的数据单元格背景设为黄色
                else:
                    wsheet.write(r, c, j[c - 1])

            r += 1  # 行数

        wexcel.save(r'C:\Users\lyial\Desktop\test.xls')


if __name__ == '__main__':
    datalocalhost = client["spider_data"]
    collection = datalocalhost['GOV_ZX_GDS_SZ']
    data = list(collection.find())
    d = {
        "序号": ["姓名", "语文", "数学", "英语"],
        "1": ["张三", 130, 120, 100],
        "2": ["李四", 100, 110, 120],
        "3": ["王五", 125, 135, 135]
    }

    da = {
        "序号": ["栏目", "文章标题", "发布时间", "来源", "链接","内容"],
    }
    print(data)
    count = 1
    for i in data:
        rktemp = []
        rktemp.append(i['ENTITY_NAME_'])
        rktemp.append(i['TITLE_'])
        rktemp.append(i['PUBLISH_TIME_'])
        rktemp.append(i['SOURCE_TYPE_'])
        rktemp.append(i['URL_'])
        rktemp.append(i['CONTENT_'][:100])
        da[str(count)] = rktemp
        count += 1

    print(da)
    save_file(da)
