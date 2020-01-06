# -*- coding:utf-8 -*-

import requests
import re
import json
import json

from fontTools.ttLib import TTFont
import time


class ParseFont(object):

    def __init__(self, ):
        # 数字字典
        self.num_url = 'http://s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/c211192063f29bdf0e57eb4a87ab80fd.svg'
        # 汉字字典
        self.addr_url = 'http://s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/320651710a8a76a25fe990bcc51ea651.svg'
        # css的x，y值
        self.css_url = 'https://s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/601523a27a9a3d535a57f59272e30bd9.css'

    def get_all_haizi(self, type):
        """
        汉字和数字字典存储
        :return:
        """
        res = requests.get(url=self.num_url).text
        pattern = re.compile(r'<text.*?y="(.*?)">(.*?)</text>')
        result = pattern.findall(res)
        msg = {}
        for i in range(1, len(result) + 1):
            d = dict()
            d['y'] = int(result[i - 1][0])
            d['data'] = result[i - 1][1]
            msg[i] = d
        with open('./config/{}.json'.format(type), 'w') as f:
            json.dump(msg, f)
        return True

    def get_css(self, ):
        """
        获取class_name对应的属性对应的x，y
        :return:
        """
        res = requests.get(
            url=self.css_url).text

        pattern = re.compile(r'.(.*?){background:(.+?)px (.+?)px;}')
        result = pattern.findall(res)

        data = dict()
        for i in result:
            one_data = dict()
            one_data['x'] = int(abs(float(i[1])))
            one_data['y'] = int(abs(float(i[2])))
            data[i[0]] = one_data
        with open('./css.json', 'w') as f:
            json.dump(data, f)

    def deal_xy(self, x, y, type):
        """
        利用x，y来寻找该属性对应的文本
        :param x: 横向px
        :param y: 纵向px
        :param type: 类别
        :return:
        """
        with open("./config/{}.json".format(type), 'r') as f:
            load_dict = json.load(f)
        # print(load_dict)
        for v in load_dict.values():
            if y <= v['y']:
                string = v['data'][x // 12]
                return string
            else:
                continue

    def search_css(self, class_name, type):
        """
        根据class属性查询css
        :param class_name:
        :return: x,y
        """
        with open("./config/{}.json".format(type), 'r') as f:
            css_dict = json.load(f)
        for k in css_dict.keys():
            if k == class_name:
                return css_dict.get(k)

    def request_url(self, ):
        """
        请求页面
        :return:
        """
        url = 'https://www.dianping.com/chengdu/ch0/r6301'
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36'
        }
        res = requests.get(url=url, headers=header, )
        return res

    def ana_content(self, html='', ):
        """
        解析html，获取数据
        :param response:
        :return:
        """
        from scrapy.selector import Selector
        result = Selector(text=html)
        # 获取所有的加密数字和汉字的class属性
        all_data = result.xpath('//svgmtsi[contains(text(),"")]/@class').extract()
        results = {}
        for c in all_data:
            xy = self.search_css(class_name=c, type='css')
            if c[:3] == 'zex':
                r = self.deal_xy(x=xy['x'], y=xy['y'], type='number')
                results['<svgmtsi class="{}"></svgmtsi>'.format(c)] = r
            elif c[:3] == 'jlx':
                r = self.deal_xy(x=xy['x'], y=xy['y'], type='addr')
                results['<svgmtsi class="{}"></svgmtsi>'.format(c)] = r
            else:
                pass

        def callback(regx, ):  # 替换策略
            return results.get(regx.group(0), regx.group(0))

        return callback

    def main(self, html):
        text = re.compile(r'<svgmtsi class="\w{5,8}"></svgmtsi>').sub(self.ana_content(html), html)
        return text


class ParseStaticFont(object):

    def __init__(self, *args, **kwargs):
        super(ParseStaticFont, self).__init__(*args, **kwargs)
        # self.deal_font()

    def deal_font(self, ):
        font_base = TTFont('f1c26632.woff')
        keys = font_base['glyf'].keys()
        values = list(
            u'''.11234567890店中美家馆小车大市公酒行国品发电金心业商司超生装园场食有新限天面工服海华水房饰城乐汽香部利子老艺花专东肉菜学福饭人百餐茶务通味所山区门药银农龙停尚安广鑫一容动南具源兴鲜记时机烤文康信果阳理锅宝达地儿衣特产西批坊州牛佳化五米修爱北养卖建材三会鸡室红站德王光名丽油院堂烧江社合星货型村自科快便日民营和活童明器烟育宾精屋经居庄石顺林尔县手厅销用好客火雅盛体旅之鞋辣作粉包楼校鱼平彩上吧保永万物教吃设医正造丰健点汤网庆技斯洗料配汇木缘加麻联卫川泰色世方寓风幼羊烫来高厂兰阿贝皮全女拉成云维贸道术运都口博河瑞宏京际路祥青镇厨培力惠连马鸿钢训影甲助窗布富牌头四多妆吉苑沙恒隆春干饼氏里二管诚制售嘉长轩杂副清计黄讯太鸭号街交与叉附近层旁对巷栋环省桥湖段乡厦府铺內侧元购前幢滨处向座下県凤港开关景泉塘放昌线湾政步宁解白田町溪十八古双胜本单同九迎第台玉锦底后七斜期武岭松角纪朝峰六振珠局岗洲横边济井办汉代临弄团外塔杨铁浦字年岛陵原梅进荣友虹央桂沿事津凯莲丁秀柳集紫旗张谷的是不了很还个也这我就在以可到错没去过感次要比觉看得说常真们但最喜哈么别位能较境非为欢然他挺着价那意种想出员两推做排实分间甜度起满给热完格荐喝等其再几只现朋候样直而买于般豆量选奶打每评少算又因情找些份置适什蛋师气你姐棒试总定啊足级整带虾如态且尝主话强当更板知己无酸让入啦式笑赞片酱差像提队走嫩才刚午接重串回晚微周值費性桌拍跟块调糕''')
        # 构建基准 {name: num}
        base_dict = dict((k, v) for k, v in zip(keys, values))
        font_new = TTFont('dianping.woff')
        new_dict = {}
        for key in font_new['glyf'].keys():
            for k, v in base_dict.items():
                # 通过比较 字形定义 填充新的name和num映射关系   <svgmtsi class="tagName"></svgmtsi>
                if font_base['glyf'][k] == font_new['glyf'][key]:
                    new_dict[
                        '<svgmtsi class="tagName">' + key.replace('uni', '&#x').lower() + ';</svgmtsi>'] = v.strip()
                    break
        with open('./font_json.json', 'w') as fp:
            json.dump(new_dict, fp)
        return new_dict

    def parse_font(self, ):
        with open(r'./font_json.json', 'r') as fp:
            mappings = json.load(fp)

        def callback(regx, ):  # 替换策略
            return mappings.get(regx.group(0), regx.group(0))

        return callback

    def main(self, html):
        text = re.compile('<svgmtsi class="tagName">&#x[0-9a-f]{4};</svgmtsi>').sub(self.parse_font(), html)
        return text


if __name__ == '__main__':
    with open('./dz.html', 'r', encoding='utf-8') as f:
        html = f.read()
    text = ParseFont().main(html)
    print(text)
    # text = ParseStaticFont().main(html)
    # # print(text)
    # from scrapy import Selector
    #
    # texts = Selector(text=text)
    # print(texts.xpath('//*[@id="shop-all-list"]/ul/li[1]/div[2]/div[3]/a[2]/span/text()').extract_first())
