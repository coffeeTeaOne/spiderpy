# encoding: utf-8
import urllib
import os
import re
import jsonpath
import json
import platform
import base64
import time
import requests
import random
from urllib.parse import urlparse
from ICrawlerSpiders.useragent import user_agent_list

#下载
from OperateDB.conn_redis import RedisClient
from SpiderTools.sougou_wechat_api import WechatSogouAPI


def Download(url,dir,name):
    import ssl
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    ssl._create_default_https_context = ssl._create_unverified_context

    try:
        r = requests.get(url,headers={'User-Agent':random.choice(user_agent_list)},verify=False)
        with open('%s%s' %(dir,name), 'wb') as f:
            f.write(r.content)
    except Exception as e:
        raise e
    '''
    try:
         #conn = urllib.request.urlopen(url)
         urllib.request.urlretrieve(url,'%s%s' %(img_dir, img_name))#如果网站开了反爬这个就不行了
    except Exception as e:
         print(e)
         print(url)
         print('无法下载请检查路径')
         return None
    '''

def re_text(str):
    '''
    替换特殊字符
    :param str:
    :return:
    '''
    regular = ['\xa0','\u3000','\t','\n',' ','\r','\r\n','"','&nbsp']
    for r in regular:
        str = str.replace(r,'')
    str = str.strip()
    return str

def re_blank_text(str):
    '''替换空格字符
    :param str:
    :return:
    '''
    regular = ['\xa0','\u3000','\t',' ']
    for r in regular:
        str = str.replace(r,'')
    str = str.strip()
    return str

def deal_text(s):
    '''把文本的换行等换成|，其它的去掉
    :param str:
    :return:
    '''
    regular = ['\xa0', '\u3000', '\t', ' ']
    huiche = ['\n','\r','\r\n','\n\r']
    special = [{'code':'"','expr':'\\"'}]
    for r in huiche:
        s = s.replace(r,'|')
    for r in regular:
        s = s.replace(r,'')
    for r in special:
        str = s.replace(r['code'], r['expr'])
    s = s.strip()
    return s

def deal_img_special_symbol(s):
    regular = ['\xa0', '\u3000', '\t', ' ','?','#',';',':',',','"','\'','=']
    for r in regular:
        s = s.replace(r,'')
    return s

def replace_special_text(str):
    '''替换多个|
    :param str:
    :return:
    '''
    expr1 = '[|]+'
    str = re.sub(expr1, '|', str)  # 把连续的\r\n（1个到多个连续的）替换为|
    expr2 = '^[|]'
    str = re.sub(expr2, '', str)  # 替换最开头|为空
    return str

def join_group(group,lengroup):
    '''  [('','b')，('a','')] 这种合并成['a','b']
    :param group:
    :return:
    '''
    l = ['']*lengroup
    #for i_ in group:

    for i in group:
        for j in i:
            if j != '':
                index = i.index(j)
                #l.insert(index, j)
                l[index] = j
    return l

def str_encode(s):
    '''将一个字符串转换为相应的二进制串（01形式表示）
    :param s:
    :return:
    '''
    return ' '.join([bin(ord(c)).replace('0b', '') for c in s])

def str_decode(s):
    '''够将这个二进制串再转换回原来的字符串
    :param s:
    :return:
    '''
    return ''.join([chr(i) for i in [int(b, 2) for b in s.split(' ')]])


def get_jp_value(data, expr):
    if isinstance(data,str):
        try:
            data =json.loads(data)
        except:
            string = 'jsonpath获取数据有问题,%s' % str(expr)
            raise Exception(string)
    return jsonpath.jsonpath(data, expr)


def get_dict_bak(conf, data):
    '''
    正则匹配
    :param conf:
    :param data:
    :return:
    '''
    tempdict = {}
    if len(conf) > 0:
        for expr in conf:
            matchdata = []
            exprconf = eval(expr[1])
            # textdatalist = list(map(lambda x:''.join(x),re.findall(ex_[0],text_date)))
            if '[}' in expr[0]:
                for expr in expr[0].split('[}'):
                    tempdata = re.findall(expr, data)
                    if len(tempdata) > 0:
                        if isinstance(tempdata[0], tuple):
                            for i in tempdata[0]:
                                if i != '':
                                    matchdata.append(i)
                        else:
                            matchdata.append(tempdata[0])
                    else:
                        matchdata.append('')
            else:
                tempdata = re.findall(expr[0], data)
                if len(tempdata) > 0:
                    if isinstance(tempdata[0], tuple):
                        for i in tempdata[0]:
                            if i != '':
                                matchdata.append(i)
                    else:
                        matchdata.append(tempdata[0])
                else:
                    matchdata.append('')

            # matchdata = txttool.join_group(exprdata, len(exprconf))

            # for i in range(len(matchdata)):
            #     if len(tempdata)<=i:
            #         tempdata.insert(i,matchdata[i])
            #     else:
            #         if matchdata[i] != '':
            #             tempdata[i] = matchdata[i]

            for conf in exprconf:
                code = conf['code']
                name = conf['name']
                index = exprconf.index(conf)
                # unit.append('{"code":"%s","name":"%s","value":"%s"}' %(code,name,txttool.re_text(tempdata[index])))
                # unit.append('"%s":"%s"' % (code, txttool.re_text(tempdata[index])))
                if code not in tempdict:
                    tempdict[code] = re_text(matchdata[index])
                else:
                    if tempdict[code] == '':
                        tempdict[code] = re_text(matchdata[index])
    return tempdict


def itemrepace(str):
    return str.replace('{', '').replace('}', '')


def get_node(lcs,str):
    # 先使用两个算出最大公约数，再依次匹配
    newstr = str.replace(lcs,'')
    if newstr == str or ('/' != lcs[-1] and newstr != str):
        lcs = lcs[:-1]
        node = get_node(lcs,str)
        return node
    else:
        return lcs


def get_dict(conf, data):
    '''
    正则匹配
    :param conf: 正则表达式(集,以[}隔开)
    :param data: 字符串
    :return:
    '''
    tempdict = {}
    matchdata = []
    if len(conf) > 0:
        # single_code单个类信息(名称,内容,时间等)
        for single_code in conf:
            # 正则匹配
            tempdata = re.findall(single_code['expr_'], data)
            if len(tempdata) > 0:
                if isinstance(tempdata[0], tuple):
                    for i in tempdata[0]:
                        if i != '':
                            matchdata.append(i)
                else:
                    matchdata.append(tempdata[0])
            else:
                matchdata.append('')

        # 所有匹配信息整理
        for c in conf:
            code = c['item_code']
            name = c['name_']
            index = conf.index(c)
            try:
                if code not in tempdict:
                    tempdict[code] = re_text(matchdata[index])
                else:
                    if tempdict[code] == '':
                        tempdict[code] = re_text(matchdata[index])
            except:
                pass

    return tempdict

def complement_url(complement,url,prefix_url=None):
    '''
    补全url功能
    :param complement: 网站的url，从当前url中补全
    :param url:
    :return: 返回补全的url
    '''
    if prefix_url and prefix_url[-1] != '/':
        prefix_url = prefix_url + '/'

    if url[0] == '.':
        url = complement.replace(complement.split('/')[-1], '') + url.replace('./', '')
    elif url[0] == '/':
        url = complement.split('//')[0] + '//' + complement.split('//')[1].split('/')[0] + url
    elif prefix_url:
        url = prefix_url + url
    else:
        url = url
    return url

def platform_system():

    sysstr = platform.system()

    if(sysstr =="Windows"):
        return 'Windows'
    elif(sysstr == "Linux"):
        return 'Linux'
    elif(sysstr == 'Darwin'):
        return 'Linux'
    else:
        return 'Other System'

def get_base64(dir,name):
    with open("%s%s" % (dir, name), "rb") as f:
        # b64encode是编码，b64decode是解码
        base64_data = base64.b64encode(f.read())
    return str(base64_data,encoding='utf-8')

def get_date_time():
    time_local = time.localtime(int(time.time()))
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    return dt


def get_top_host(url):
    topHostPostfix = [
        '.com', '.la', '.io', '.co', '.cn', '.info', '.net', '.org', '.me', '.mobi', '.us', '.biz', '.xxx', '.ca',
        '.co.jp', '.com.cn', '.net.cn', '.org.cn', '.mx', '.tv', '.ws', '.ag', '.com.ag', '.net.ag', '.org.ag',
        '.am', '.asia', '.at', '.be', '.com.br', '.net.br', '.name', '.live', '.news', '.bz', '.tech', '.pub', '.wang',
        '.space', '.top', '.xin', '.social', '.date', '.site', '.red', '.studio', '.link', '.online', '.help', '.kr',
        '.club', '.com.bz', '.net.bz', '.cc', '.band', '.market', '.com.co', '.net.co', '.nom.co', '.lawyer', '.de',
        '.es', '.com.es', '.nom.es', '.org.es', '.eu', '.wiki', '.design', '.software', '.fm', '.fr', '.gs', '.in',
        '.co.in', '.firm.in', '.gen.in', '.ind.in', '.net.in', '.org.in', '.it', '.jobs', '.jp', '.ms', '.com.mx',
        '.nl', '.nu', '.co.nz', '.net.nz', '.org.nz', '.se', '.tc', '.tk', '.tw', '.com.tw', '.idv.tw', '.org.tw',
        '.hk', '.co.uk', '.me.uk', '.org.uk', '.vg', 'gov.cn','.edu.cn','.73.4.152','.73.25.79']

    # extractPattern = r'[\.](' + '|'.join([h.replace('.', r'\.') for h in topHostPostfix]) + ')$'
    # pattern = re.compile(extractPattern, re.IGNORECASE)
    extractRule = r'([\w\-\d]*\.?)%s(' + '|'.join([h.replace('.', r'\.') for h in topHostPostfix]) + ')$'
    level = '{1}'
    extractRule = extractRule % (level)
    parts = urlparse(url)
    host = parts.netloc
    pattern = re.compile(extractRule, re.IGNORECASE)
    m = pattern.search(host)
    top_host = m.group() if m else host

    if len(top_host.split('.')) == 4:
        top_host = top_host.split('.')
        top_host.pop(0)
        top_host = '.'.join(top_host)

    return top_host

def get_username():
    import pwd
    return str(pwd.getpwuid(os.getuid())[0])

def diff_url(url, last_url):
    """
    处理不同的url
    :param url:
    :param last_url:
    :return:
    """
    # 完整的url
    if url[:4] == 'http':
        return url
    # 缺少http
    elif url[:2] == '//':
        return 'http:' + url
    # 当前路径下
    elif url[:2] == './':
        new_url = '/'.join(last_url.split('/')[:-1])
        return new_url + '/' + url.split('./')[-1]
    # 缺少域名
    elif url[:1] == '/' and url[:2] != '//':
        domain_url = last_url.split('/')[2]
        return 'http://' + domain_url + url
    # 返回多层级上级相对路径
    elif url[:3] == '../':
        temp_url_list = url.split('/')
        count = 0
        for ur in temp_url_list:
            if ur == '..':
                count += 1
            else:
                break
        now_url = '/'.join(last_url.split('/')[:-(count + 1)])
        return now_url + url.split('..')[-1]

    else:
        domain_url = last_url.split('/')[2]
        return 'http://' + domain_url + '/' + url

def wash_url(url):
    from SpidersLog.icrwler_log import ICrawlerLog
    log = ICrawlerLog('spider').save
    type_ = ['SOURCE_TYPE_=%E5%AE%98%E7%BD%91%E5%8A%A8%E6%80%81', 'SALE_SOURCE_=%E8%B4%A2%E7%BB%8F%E6%96%B0%E9%97%BB',
             'SOURCE_TYPE_=%E8%B4%A2%E7%BB%8F%E6%96%B0%E9%97%BB', 'SALE_SOURCE_=%E6%94%BF%E7%AD%96%E5%85%AC%E5%91%8A'
             ]
    for type in type_:
        try:
            view_url = re.sub(r'\?{}'.format(type), '', url) if re.sub(
                r'\?{}'.format(type), '', url) != url else re.sub(
                r'\&{}'.format(type), '', url) if re.sub(
                r'\&{}'.format(type), '', url) != url else re.sub(
                r'{}\&'.format(type), '', url)
            if view_url != url:
                break
        except:
            # log('url清洗')
            pass
    return view_url


def wash_form(form):
    from SpidersLog.icrwler_log import ICrawlerLog
    log = ICrawlerLog('spider').save
    type_ = ['SOURCE_TYPE_', 'SALE_SOURCE_',]
    for type in type_:
        try:
            if type in form.keys():
                form.pop(type)
        except:
            pass
    return form


class SpiderException(BaseException):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class ResponseHTML(object):

    def __init__(self, url, text, content, status_code, encoding='utf-8',):

        self.url = url
        self.status_code = status_code
        self.text = text
        self.content = content
        self.encoding = encoding


def get_ip():
    session = requests.Session()
    ip_data = session.get('http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?spiderId=c3f82dd44bd64498a56ab74559752251&orderno=YZ20191309527RD9e72&returnType=2&count=1').json()
    ip_list = []
    for ip in ip_data.get('RESULT'):  # {'port': '22445', 'ip': '125.105.18.116'}
        ip_list.append(str(ip['ip']) + ':' + str(ip['port']))
    return ip_list[0]


def get_kuai_ip():
    session = requests.Session()
    ip_data = session.get('http://dps.kdlapi.com/api/getdps/?orderid=984423689516359&num=1&pt=1&sep=1').text
    return ip_data


class WeixinVerifiy(object):
    '''可配置参数
    直连
    ws_api = wechatsogou.WechatSogouAPI()

    验证码输入错误的重试次数，默认为1
    ws_api = wechatsogou.WechatSogouAPI(captcha_break_time=3)

    所有requests库的参数都能在这用
    如 配置代理，代理列表中至少需包含1个 HTTPS 协议的代理, 并确保代理可用
    ws_api = wechatsogou.WechatSogouAPI(proxies={
        "http": "127.0.0.1:8888",
        "https": "127.0.0.1:8888",
    })
    如 设置超时
    ws_api = wechatsogou.WechatSogouAPI(timeout=0.1)'''
    def __init__(self):
        ip = RedisClient().get()
        # ip = self.get_ip()
        self.ws_api = WechatSogouAPI(captcha_break_time=10, proxies={
            "http": ip,
            "https": ip,
        })
        # self.proxies={"http": ip,"https": ip}

    def get_ip(self, ):
        session = requests.Session()
        ip_data = session.get('http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?spiderId=c3f82dd44bd64498a56ab74559752251&orderno=YZ20191309527RD9e72&returnType=2&count=1').json()
        ip_list = []
        for ip in ip_data.get('RESULT'):  # {'port': '22445', 'ip': '125.105.18.116'}
            ip_list.append(str(ip['ip']) + ':' + str(ip['port']))
        return ip_list[0]

    def identify_image(self, img):

        base64_picture = base64.b64encode(img)

        # verificat = requests.post(url='http://192.168.1.12:8081/wechat', data={'base64': base64_picture}).text
        verificat = requests.post(url='http://onestopdata.pactera.com:9999/wechat', data={'base64': base64_picture}).text
        return verificat

    def main(self, words):
        result = self.ws_api.search_gzh(words, page=3, identify_image_callback=self.identify_image)
        if result:
            return result
        else:
            return False


def ip_proxy():
    """
    从ip代理池获取ip代理
    :return:
    """
    try:
        ip = RedisClient().get()
        proxies = {
                   'http': 'http://' + ip,
                   'https': 'https://' + ip
                   }
        return proxies
    except Exception as e:
        print(6)
        return False

if __name__ == '__main__':
    url = 'http://www.ennweekly.com/finance/2019/0301/10918.html'
    print(get_top_host(url))