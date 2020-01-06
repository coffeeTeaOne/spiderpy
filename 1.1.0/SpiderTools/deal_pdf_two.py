import random
import ssl
import urllib.request
from urllib.request import urlopen
from urllib.request import Request
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal, LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed
from pdfminer.pdfparser import PDFParser, PDFDocument

from OperateDB.conn_redis import RedisClient
from SpiderTools.ocr import ocr
import fitz
import time
import re
import os
from staticparm import img_dir


class PDF(object):
    def __init__(self):
        """
        实例化请求头user_agent
        """
        self.user_agent = [
            'Mozilla/5.0 (Windows NT 10.0; WOW64)', 'Mozilla/5.0 (Windows NT 6.3; WOW64)',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; rv:11.0) like Gecko)',
            'Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1',
            'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070309 Firefox/2.0.0.3',
            'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070803 Firefox/1.5.0.12',
            'Opera/9.27 (Windows NT 5.2; U; zh-cn)',
            'Mozilla/5.0 (Macintosh; PPC Mac OS X; U; en) Opera 8.0',
            'Opera/8.0 (Macintosh; PPC Mac OS X; U; en)'
        ]

    def download_pdf(self, pdf_url, path_main, file_name):
        """
        下载pdf文件
        :param pdf_url: pdf文件的url
        :param file_name: 存储的文件名
        :param path_main: 存储路径
        :return:
        """
        try:
            context = ssl._create_unverified_context()
            # file_name = pdf_url.split('/')[-1]
            pdf_file = urllib.request.urlopen(url=pdf_url, context=context)
            # import requests
            #
            # requests.Request(method='get',url=pdf_url,headers=)
            with open(path_main + file_name, 'wb') as f:
                block_sz = 8192
                while True:
                    buffer = pdf_file.read(block_sz)
                    if not buffer:
                        break
                    f.write(buffer)
                # print('pdf下载完成！')
                return True
        except Exception as e:
            raise Exception(e)

    def img_change_word(self, dir, name):
        """
        图片转文本
        :param dir: 文件路径
        :param name: 文件名
        :return:
        """
        results = ocr(dir, name)
        if results:
            return results
        else:
            return None

    def noimgpdf_change_word(self, _path):
        """
        没有图片的pdf文件转word
        :param _path: pdf文件路径
        :return:
        """
        try:
            if 'http://www' in _path:
                re = Request(url=_path, headers={'User-Agent': random.choice(self.user_agent)})
                fp = urlopen(re)  # 打开在线PDF文档
            else:
                fp = open(_path, 'rb')  # 打开本地pdf文档
            praser_pdf = PDFParser(fp)
            doc = PDFDocument()
            praser_pdf.set_document(doc)
            doc.set_parser(praser_pdf)
            doc.initialize()
            if not doc.is_extractable:
                raise PDFTextExtractionNotAllowed
            else:
                rsrcmgr = PDFResourceManager()
                laparams = LAParams()
                device = PDFPageAggregator(rsrcmgr, laparams=laparams)
                interpreter = PDFPageInterpreter(rsrcmgr, device)
                all_results = ''
                for page in doc.get_pages():
                    interpreter.process_page(page)
                    layout = device.get_result()
                    for out in layout:
                        if isinstance(out, LTTextBoxHorizontal):
                            results = out.get_text()
                            all_results += results
                return all_results
        except:
            return None

    def imgpdf_change_img_local(self, path, pic_path=img_dir):
        """
        从pdf文件中提取图片
       :param path: pdf文件的路径
       :param pic_path: pdf里面图片保存的路径
       :return:

        """
        doc = fitz.open(path)
        # t0 = time.clock()
        checkXO = r"/Type(?= */XObject)"
        checkIM = r"/Subtype(?= */Image)"
        imgcount = 0
        lenXREF = doc._getXrefLength()
        # print("文件名:{}, 页数: {}, 对象: {}".format(path, len(doc), lenXREF - 1))
        try:
            all_results = ''
            for i in range(1, lenXREF):
                text = doc._getObjectString(i)
                isXObject = re.search(checkXO, text)
                isImage = re.search(checkIM, text)
                if not isXObject or not isImage:
                    continue
                imgcount += 1
                pix = fitz.Pixmap(doc, i)
                if '/' in path:
                    path.replace('/', '\\')
                name = path.split('\\')[-1].replace('.', '_')
                new_name = "{}_img_{}.png".format(name, imgcount)
                new_name = new_name.split('/')[-1]
                if pix.n < 5:
                    pix.writePNG(os.path.join(pic_path, new_name))
                else:
                    pix0 = fitz.Pixmap(fitz.csRGB, pix)
                    pix0.writePNG(os.path.join(pic_path, new_name))
                    pix0 = None
                pix = None

                results = ocr(pic_path, new_name)
                if results:
                    all_results += results[1]
                else:
                    return None
            # t1 = time.clock()
            # print("运行时间:{}s".format(t1 - t0))
            # print("提取了{}张图片".format(imgcount))
            # print('{}文件图片提取完成！'.format(path))
            return all_results
        except:
            # print('pdf文件转图片错误！')
            return None


if __name__ == '__main__':
    url = 'https://per.spdb.com.cn/bank_financing/financial_product/zxlc/201709/P020190404777135897809.pdf'
    path_main = r'C:\Users\lyial\Desktop\try_project\pdf_img_word\pdf_download'
    PDF().download_pdf(url, path_main, file_name='one.pdf')
    # PDF().noimgpdf_change_word(r'C:\Users\lyial\Desktop\asd\aaa.pdf')
    # url = 'http://www.czbank.com/cn/personal/investment/issue/201809/W020180926328177964461.pdf'
    # PDF().noimgpdf_change_word(url)
    # path = 'C:/Users/lyial/Desktop/asd/try.pdf'
    # PDF().imgpdf_change_img_local(path)
