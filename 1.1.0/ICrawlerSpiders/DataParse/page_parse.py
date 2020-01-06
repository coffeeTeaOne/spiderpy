# encoding: utf-8
import os

from Env.parse_yaml import FileConfigParser
from SpiderTools import ocr
from SpiderTools.tool import get_dict, platform_system, diff_url
from SpiderTools.get_word import get_word_content
from SpiderTools.tool import complement_url
from SpiderTools.tool import re_text
from SpiderTools.tool import deal_text
from SpiderTools.tool import Download
from SpiderTools.tool import replace_special_text
from SpiderTools.tool import deal_img_special_symbol
from SpiderTools.tool import get_date_time
from SpiderTools.pdf import PDF
from scrapy.selector import Selector
from pyquery import PyQuery
from SpidersLog.icrwler_log import ICrawlerLog
from SpiderTools.Js_func import JsFunc
from SpiderTools.tool import get_base64
from staticparm import img_dir, root_path
from staticparm import pdf_dir
from staticparm import word_dir
import time
import re


class Page_Parse:

    def __init__(self):

        self.log = ICrawlerLog('spider').save

    def page_content_parse(self, content_data, meta):
        """
        page模式解析网页内容
        :param content_data: 网页的response信息
        """
        def __get_content(group, type_, img_src=None, top_url=None):
            '''xpath解析
            :param group: xpath组（1,2,3）
            :param type_: 文本类型（文本，大文本等）
            :return: 返回xpath得到的信内容
            '''
            response = Selector(text=content_data)
            content = ''
            for tt_ in group:  # 循环xpath获取数据
                if tt_ == '':
                    return None

                # 处理采集该元素文本
                if type_ == 'TEXT':
                    if '/text()' not in tt_ and '@' != tt_.split('/')[-1][0]:  # 没有/text()和@，自动加上/text()，获取该元素文本
                        tt_ = tt_ + '/text()'
                    content = ''.join(response.xpath(tt_).extract())

                # 处理附件
                if type_ == 'FILE' or type_ == 'IMGURL' or type_ == 'IMG' or type_ == 'URL':
                    content = response.xpath(tt_).extract_first()

                # 处理图片解析
                if type_ == 'IMGOCR':
                    content = response.xpath(tt_).extract()

                # 处理大文本
                if type_ == 'BLOB':
                    style = re.findall('(<(?:script|style)[\s\S]*?>[\s\S]*?<(?:\/script|\/style)>)', content_data)
                    for s_ in style:
                        content_data.replace(s_, '')
                    response = Selector(text=content_data)
                    content = '|'.join(response.xpath(tt_.replace('/text()', '') + '//text()').extract())

                # 处理html(css)
                if type_ == 'HTMLCSS':
                    # content = response.xpath(tt_).extract_first()
                    img_dir = FileConfigParser().get_path(server=platform_system(), key='wechatimg')
                    img_dir = root_path + img_dir
                    new_css_text = ''

                    css_data = response.xpath('head/link')
                    for css in css_data:
                        # type_c = re.findall(r'<link(.*?)>', css.extract())[0]
                        # type_css = type_c.replace(re.findall(r'href=["|\'].*?["|\']', type_c)[0], '')
                        link = css.xpath('@href').extract_first()
                        if link and 'css' in link:
                            # 处理url，让其形成完整的url
                            link = diff_url(url=link, last_url=top_url)
                            try:
                                css_text = request_url(link)
                                # new_css_text += '<style{}>{}</style>'.format(type_css, str(css_text))
                                new_css_text += '<style type="text/css">{}</style>'.format(str(css_text))
                            except Exception as e:
                                self.log.error(e.args)
                                self.log.error('{}的css处理错误！'.format(top_url))
                                new_css_text = ''
                                # raise e

                    # 获取含标签正文
                    result = response.xpath(tt_).extract_first()
                    new_result = Selector(text=result)

                    # 处理图片替换
                    if img_src:
                        img_content = new_result.xpath('//img')
                        if img_content:
                            for img in img_content:
                                for img_sx in img_src.get('img_src_list'):
                                    if img_sx == 'src':
                                        src = img.xpath('@src').extract_first()
                                        if src:
                                            old = 'src="%s"' % src
                                            # 处理url，让其形成完整的url
                                            src = diff_url(url=src, last_url=top_url)
                                            break
                                    elif img_sx != 'src' and img_sx:
                                        src = img.xpath('@{}'.format(img_sx)).extract_first()
                                        if src:
                                            old = '%s="%s"' % (img_sx, src)
                                            # 处理url，让其形成完整的url
                                            src = diff_url(url=src, last_url=top_url)
                                            break
                                    else:
                                        src = ''
                                        continue
                                if src:
                                    img_name = src.split('/')[-1]
                                    # 下载图片
                                    time.sleep(1)
                                    Download(src, img_dir, img_name)
                                    # 图片base64编码
                                    img_base64 = get_base64(img_dir, img_name)
                                    os.remove(img_dir + img_name)
                                    # old = 'src="%s"' % src
                                    new = 'src="data:image/png;base64,%s"' % img_base64
                                    # 重新组装的内容，图片转为base64编码
                                    result = result.replace(old, new)
                                else:
                                    result = result
                        else:
                            result = result
                    else:
                        result = result
                    content = new_css_text + result

                if not content:
                    continue
                else:
                    break
            return content

        def request_url(url):
            """
            请求url
            :param url:
            :return:
            """
            import requests
            import ssl
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            ssl._create_default_https_context = ssl._create_unverified_context

            res = requests.get(url=url, verify=False)
            for i in ['utf-8', 'gbk', 'gb2312']:
                try:
                    result = res.content.decode(i)
                    break
                except:
                    result = None
                    continue
            if result:
                return result
            else:
                result = res.text
                return result

        flag = 0
        pattern = meta['pattern']       # 字段配置信息（数组）
        text_date = ''
        imgocr = []
        img = []
        longtext = []
        imgurl = []
        ttxt = []
        word = []
        pdf = []
        html_css = []
        yv = []
        child_url = []
        finalout = eval(pattern[0]['con_f'])  # 最后输出项（全部）
        final_list = []
        entity_name = meta['entity_name']
        entity_code = meta['entity_code']
        content_code = meta['content_code']
        algo = meta['algo']
        child_xpath = meta['child_xpath']
        child_prefix = meta['child_prefix']
        url = meta['url']

        # 循环各字段把他们分别装入指定类型的列表中
        for p_ in pattern:
            if p_['type2'] == 'TEXT':    # 采集该元素
                ttxt.append(p_)
            if p_['type2'] == 'IMGOCR':  # 图片解析
                imgocr.append(p_)
            if p_['type2'] == 'IMGURL':  # 采集该图片地址
                imgurl.append(p_)
            if p_['type2'] == 'IMG':     # 采集该图片
                img.append(p_)
            if p_['type2'] == 'BLOB':    # 大文本
                longtext.append(p_)
            if p_['type2'] == 'FILE':    # 采集该附件
                if p_['datatype'] == 'WORD':   # word处理
                    word.append(p_)
                if p_['datatype'] == 'PDF':    # pdf处理
                    pdf.append(p_)
            if p_['type2'] == 'HTMLCSS':   # 采集html（含css）
                html_css.append(p_)
            # 存放必填数据信息
            if p_['required'] == 'Y':
                yv.append(p_['code'].split('.')[-1])

        # 处理子模板xpath，前缀问题
        for c_x, c_p in list(zip(child_xpath, child_prefix)):
            c_url = __get_content(group=[c_x], type_='URL')
            if c_p:
                c_url = c_p + c_url
            child_url.append(c_url)

        # 处理采集该元素列表
        for t_ in ttxt:
            content = __get_content(group=t_['pattern'], type_=t_['type2'])  # 获取该字段的数据
            code = t_['code'].replace(content_code + '.', '')                # 获取该字段的编码

            if not content:
                finalout[code] = ''
                continue
            # 处理该字段的算法
            if code in algo:
                finalout[code] = JsFunc(algo[code], content).text
            else:
                finalout[code] = re_text(content)  # 处理数据的特殊字符

        # 处理html（css）列表
        for hc in html_css:
            content = __get_content(group=hc['pattern'], type_=hc['type2'], img_src=hc['img_src_list'], top_url=url)
            # print(content)
            code = hc['code'].replace(content_code + '.', '')
            if not content:
                finalout[code] = ''
                continue
            else:
                finalout[code] = content

        # 处理图片列表
        for im in img:
            content = __get_content(group=im['pattern'], type_=im['type2'])
            code = im['code'].replace(content_code + '.', '')

            if not content:
                finalout[code] = ''
                continue

            name = im['code'].split('.')[-1]
            if name in algo:
                content = JsFunc(algo[name], content).text

            img_name = deal_img_special_symbol(content.split('/')[-1])  # 分析拿到的图片地址信息，截取图片的名称
            img_url = complement_url(meta['url'], content)
            try:
                Download(img_url, img_dir, img_name)
            except Exception as e:
                self.log.error('下载图片错误，可能是配置问题, img url: %s,保存名字为:%s' % (img_url, img_name))
                self.log.error(e)
                return False

            img_base = get_base64(img_dir, img_name)

            finalout[code] = img_base

        # 处理采集图片地址列表
        for iu_ in imgurl:
            content = __get_content(group=iu_['pattern'], type_=iu_['type2'])
            code = iu_['code'].replace(content_code + '.', '')

            if not content:  # 当拿到的值为空时，跳出这一层
                finalout[code] = ''
                continue

            name = iu_['code'].split('.')[-1]
            if name in algo:
                content = JsFunc(algo[name], content).text

            img_name = deal_img_special_symbol(content.split('/')[-1])  # 分析拿到的图片地址信息，截取图片的名称
            img_url = complement_url(meta['url'], content)
            try:
                Download(img_url, img_dir, img_name)
            except Exception as e:
                self.log.error('下载图片错误，可能是配置问题, img url: %s,保存名字为:%s' % (img_url, img_name))
                self.log.error(e)
                return False

            finalout[code] = img_url

        # 处理图片解析列表
        for i_ in imgocr:
            content = __get_content(group=i_['pattern'], type_=i_['type2'])  # 通过xpath拿到图片的地址信息
            code = i_['code'].replace(content_code + '.', '')

            if not content:  # 当拿到的值为空时，跳出这一层
                finalout[code] = ''
                continue

            big_img_data = ''
            img_base64 = []
            for img_url in content:
                name = i_['code'].split('.')[-1]
                if name in algo:
                    img_url = JsFunc(algo[name], img_url).text
                img_name = deal_img_special_symbol(img_url.split('/')[-1])  # 分析拿到的图片地址信息，截取图片的名称
                img_url = complement_url(meta['url'], img_url)
                try:
                    Download(img_url, img_dir, img_name)
                except Exception as e:
                    self.log.error('下载图片错误，可能是配置问题, img url: %s,保存名字为:%s' % (img_url, img_name))
                    self.log.error(e)
                    # return False
                    continue

                base64_data, img_content = ocr.ocr(img_dir, img_name)  # 进行OCR识别，拿到base64和图片内容信息的值
                # if img_content is None:
                #     return None
                img_base64.append(base64_data)
                big_img_data = big_img_data + img_content

            finalout[code] = big_img_data
            if i_['expr']:
                tempdict = get_dict(i_['expr'][code], big_img_data)
                finalout.update(tempdict)

        # 处理大文本列表
        for l_ in longtext:
            content = __get_content(group=l_['pattern'], type_=l_['type2'])
            code = l_['code'].replace(content_code + '.', '')

            # if not content and l_['required'] == 'Y':
            #     self.log.error('大文本xpath有问题,返回内容为空，请检查有问题字段%s' %l_['code'])
            #     return False

            if not content:
                finalout[code] = ''
                continue

            # content = response.xpath(l_[2][0]).xpath('string()').re('(\w+)') #这个方式排版会有问题
            # text_date = ''.join(content).strip('\r\n').strip('\r').strip('\n').strip().strip(' ')
            text_date = ''.join(content)

            temp_text = []
            for c_ in content:
                temp_text.append(deal_text(c_))

            textdata = replace_special_text(''.join(temp_text))

            finalout[code] = textdata

            if l_['expr'] and code in l_['expr']:
                tempdict = get_dict(l_['expr'][code], text_date)
                finalout.update(tempdict)

            if code in algo:
                finalout[code] = JsFunc(algo[code], textdata).text

        # 处理word类型列表
        for w_ in word:
            file_url = __get_content(group=w_['pattern'], type_=w_['type2'])
            code = w_['code'].replace(content_code + '.', '')

            if not file_url:
                finalout[code] = ''
                continue

            name = entity_code + '_' + file_url.split('/')[-1]

            if file_url:
                file_url = complement_url(meta['url'], file_url)

            try:
                Download(file_url, word_dir, name)
            except Exception as e:
                self.log.error('下载word错误,word url: %s' % file_url)
                self.log.error(e)
                return False

            word_content = get_word_content(word_dir, name)

            finalout[code] = word_content

            if w_['expr']:
                tempdict = get_dict(w_['expr'][code], word_content)
                finalout.update(tempdict)

        # 处理pdf类型列表
        for p_ in pdf:
            pdf_url = __get_content(group=p_['pattern'], type_=p_['type2'])
            code = p_['code'].replace(content_code + '.', '')

            if not pdf_url:
                finalout[code] = ''
                continue

            if pdf_url:
                complement_url(meta['url'], pdf_url)

            pdf_content = PDF.get_pdf_content(pdf_url)

            finalout[code] = pdf_content

            if p_['expr']:
                tempdict = get_dict(p_['expr'][code], pdf_content)
                finalout.update(tempdict)

        # 最后组装其它信息并返回
        if isinstance(finalout, str):
            finalout = eval(finalout)
        finalout['URL_'] = meta['url']
        finalout['DEALTIME_'] = str(time.time())
        finalout['DATETIME_'] = get_date_time()
        finalout['ENTITY_NAME_'] = entity_name
        finalout['ENTITY_CODE_'] = entity_code
        final_list.append(finalout)
        final_list.append(yv)

        # if text_date != '' :
        return final_list, child_url
