# encoding: utf-8
# import execjs
import jsonpath
import json


class Js_Analyze:

    def __init__(self,jscontent=None,**kwargs):
        try:
            self.jscontent = json.loads(jscontent)
        except:
            self.jscontent = jscontent


class Return_Result(Js_Analyze):

    def An_Js_One(self, node, input=None, output=None):
        if input is None and output is None:
            jp = '$.%s' % node  # 组合jsonpath
        else:
            jp = '$.%s[?(@.code=="%s")].%s' % (node, input, output)

        value = jsonpath.jsonpath(self.jscontent, jp)

        values = []

        if not value:
            return False
        elif input is None and output is None:
            if isinstance(value[0], list):
                for v_ in value[0]:
                    if isinstance(v_, str):
                        v_ = eval(v_)
                    if 'example' in v_:
                        del v_['example']
                    values.append(v_)
                return values
            else:
                return value[0]
        else:
            type = jsonpath.jsonpath(self.jscontent, '$.%s[?(@.code=="%s")].type' % (node, input))
            values.append(value[0])
            values.append(type[0])
            return values

    def An_Js_List(self, jp):
        value = jsonpath.jsonpath(self.jscontent, jp)
        return value

# class An_Fun:
#
#     def Handle_Fun(fun):
#         ctx = execjs.compile("""
#               function Templet(fun) {
#                  function reference(a){
#                      return a;
#                  }
#
#               function jsonpath(b){
#                 try {
#                   if(b.indexOf(".") == 13 || b.indexOf(".") == 14){
#                         var bb = b.split('.');
#                         var cc = "reference('" + bb[0].split('(')[1].split(')')[0] +"')";
#                         var vv = eval(cc);
#                         return [vv,bb[1]];
#                     }
#               }catch (e){
#                 return b;
#               }
#               return b;
#               }
#
#               var aa = eval(fun);
#               return aa;
#              }
#           """)
#
#         result = ctx.call('Templet',fun)
#         return result

# fun1 = """reference('P11')"""'
# fun1 = "jsonpath('reference(P11).accpNo')"
# r = An_Fun.Handle_Fun(fun1)
# print(r)
# # result1 = execjs.eval("'red yellow blue'.split(' ')")
# # print(result1)
# #
# ctx = execjs.compile("""
#      function add(x, y, z) {
#          function aa(a){
#              return a;
#          }
#          function reference(b){
#          return b}
#          var aa = eval(z);
#          return aa;
#      }
#  """)
# result1 = ctx.call('add',1,2,'aa(z)')
# print(result1)
#
# #result2 = ctx.call("add", 1, 2,"x=10;y=20;x*y")
# #result2 = ctx.call("add", 1, 2,"123")
#
# result2 = ctx.call("add", 1, 2, "x+y+aa(100)")
#
# result3 = ctx.call("add", 1, 2, "'x'+'y'+aa('z')")
#
# print(result2)
#
# print(result3)
# a={"msg":{"total":0,"time":15.0,"isMore":'false',"rows":[]}}
# #a = {"msg":{"total":1,"time":4.0,"isMore":"false","rows":[{"idNo":"","id":"B2017042610370052677","unit":"4","items":[{"text":"","title":"负责人"},{"text":"","title":"业务主管单位"},{"text":"","title":"住所"}],"unitType":"1","isCollection":"N","name":"cdscsst009","subjectType":"社会团体","regNo":""}]}}
# r = jsonpath.jsonpath(a,"$.msg.rows[*]")
# print(r)
# for i in r:
#     print(i['id'])
