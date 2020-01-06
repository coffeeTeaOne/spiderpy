
# from fontTools.ttLib import TTFont
# font = TTFont('movie.woff') # 打开当前目录的 movie.woff 文件
# font.saveXML('movie.xml') # 另存为 movie.xml

import re,requests
from parsel import Selector
from urllib import parse
from fontTools.ttLib import TTFont

base_font = {
 "font": [{"name": "uniEE76", "value": "0", "hex": "fc170db1563e66547e9100cf7784951f"},
 {"name": "uniF57B", "value": "1", "hex": "251357942c5160a003eec31c68a06f64"},
 {"name": "uniE7DF", "value": "2", "hex": "8a3ab2e9ca7db2b13ce198521010bde4"},
 {"name": "uniF19A", "value": "3", "hex": "712e4b5abd0ba2b09aff19be89e75146"},
 {"name": "uniF593", "value": "4", "hex": "e5764c45cf9de7f0a4ada6b0370b81a1"},
 {"name": "uniEA16", "value": "5", "hex": "c631abb5e408146eb1a17db4113f878f"},
 {"name": "uniE339", "value": "6", "hex": "0833d3b4f61f02258217421b4e4bde24"},
 {"name": "uniE9C7", "value": "7", "hex": "4aa5ac9a6741107dca4c5dd05176ec4c"},
 {"name": "uniEFD4", "value": "8", "hex": "c37e95c05e0dd147b47f3cb1e5ac60d7"},
 {"name": "uniE624", "value": "9", "hex": "704362b6e0feb6cd0b1303f10c000f95"}]
}

def download_font():
    url = 'http://www.porters.vip/confusion/movie.html'
    resp = requests.get(url)
    sel = Selector(resp.text)
    # 提取页面加载的所有 css 文件路径
    css_path = sel.css('link[rel=stylesheet]::attr(href)').extract()
    woffs = []
    for c in css_path:
       # 拼接正确的 css 文件路径
       css_url = parse.urljoin(url, c)
       # 向 css 文件发起请求
       css_resp = requests.get(css_url)
       # 匹配 css 文件中的 woff 文件路径
       # woff_path = re.findall(r"src:url('..(.*.woff)') format('woff');",css_resp.text)
       woff_path = re.findall("src:url\('\.\.(.*)'\) format\('woff'\)",css_resp.text)
       if woff_path:
           # 如故路径存在则添加到 woffs 列表中
           woffs += woff_path
    woff_url = 'http://www.porters.vip/confusion' + woffs.pop()
    woff = requests.get(woff_url)
    filename = 'target.woff'
    with open(filename, 'wb') as f:
       # 将文件保存到本地
       f.write(woff.content)
    # 使用 TTFont 库打开刚才下载的 woff 文件

    # return font


def ocr_font():
    web_code = '&#xe624.&#xe9c7'
    # 编码文字替换
    font = TTFont('target.woff')
    print(font)
    woff_code = [i.upper().replace('&#X', 'uni') for i in web_code.split('.')]
    import hashlib
    result = []
    for w in woff_code:
        # 从字体文件中取出对应编码的字形信息
        content = font['glyf'].glyphs.get(w).data
        # 字形信息 MD5
        glyph = hashlib.md5(content).hexdigest()
        for b in base_font.get('font'):
            # 与基准字形中的 MD5 值进行对比，如果相同则取出该字形描述的文字
            if b.get('hex') == glyph:
                result.append(b.get('value'))
                break
                # 打印映射结果
    print(result)

if __name__ == '__main__':
    ocr_font()
