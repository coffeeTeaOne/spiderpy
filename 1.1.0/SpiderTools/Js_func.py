# coding=utf-8
# coding=gbk
# import execjs
from OperateDB.conn_mysql import Op_Mysql
import js2py


class JsFunc(object):
    def __init__(self, code, value):
        self.entrance_func = None
        self.js_script = None
        self.code = code
        self.value = value

    def get_data_from_sql(self):
        # 从数据库调取入口函数和js函数
        func_data = Op_Mysql().Select_Query(tablename="spi_js_function", output=["ENTRANCE_", "SCRIPT_"],
                                            where='CODE_="%s"' % self.code)[0]

        # 将所取数据存入字典，便于传参
        data_dict = dict()
        data_dict["ENTRANCE"] = func_data[0]
        data_dict["SCRIPT_"] = func_data[1]

        return data_dict

    # 执行js函数
    def js_func(self, *args, **kwargs):
        # 初始化参数
        js_script = kwargs["kwargs"]["SCRIPT_"]
        entrance = kwargs["kwargs"]["ENTRANCE"]

        # 编译js函数
        # ctx = execjs.compile(js_script)

        # 通过入口函数调用js
        # result = ctx.call(entrance,self.value)
        result = str(js2py.eval_js(js_script)(self.value))

        return result

    @property
    def text(self, *args, **kwargs):
        data_dict = self.get_data_from_sql()
        result = self.js_func(*args, kwargs=data_dict)
        return result
