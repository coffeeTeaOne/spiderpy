# coding=gbk
import js2py

js = """
function QUTZJGranchCut(str) {
    var reg = /window.open\('(.*)'\)/;
    var result = str.match(reg);
    if(result != null){
      return 'https://www.tzxm.gov.cn:8081/tzxmspweb' + result[1];
    }
 }
"""
js2 = """
function HBYHSYL(str){
       if(str.indexOf('/')!=-1) {
           return str.substring(0, str.indexOf('/')).replace('/','');
       }else {
           return str;
       }
   }"""

js3 = """
function GZSFGWFZGH(str){
       return 'http://fgw.gz.gov.cn' + str.split('..')[2]
   }"""

js4 = """
function YJSZF_ZWGK(str) {
if (str.indexOf('.TRS_EditorP') != -1) {
    var result = str.split('\}\|');
    return result[result.length-1]
 }else{
    return str
}
}
"""

js5 = """
function gdscjj_ggzs(str){
	if(str.indexOf('../')!=-1) {
           return 'http://igd.gdcom.gov.cn/' + str.split('../../')[1]
       }else {
           return 'http://igd.gdcom.gov.cn/rdxx/ggtz/' + str.split('./')[1];
       }
}"""


js6 ="""
function ZTB_ZZGJZBYXGS_url(str) {
    var reg = /showArticle\('(.*)'\).*/;
    var result = str.match(reg);
    if(result != null){
      return result[1];
    }
    }"""

js7 = """
function ZTBGZYH(str){
       return 'http://www.gzccb.com/bhgg/' + str.split('./')[1]
   }"""
# s = "1.9%/3.95%"
# s = "3%"
# s = ""
s = "./201811/t20181114_2227.html"

result = js2py.eval_js(js7)(str(s))
print(result)
