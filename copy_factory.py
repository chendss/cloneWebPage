import re
import base64
import requests
import threading
from pydash import get
from bs4 import BeautifulSoup
from tools import suffix, is_base64_code, to_array, md5, completion_url


class CopyFactory():
    """
    复制网页的工厂类
    """

    def __init__(self, text, p, href):
        self.text = text
        self.path = p
        self.id = md5(href)
        self.baseUrl = href
        self.soup = BeautifulSoup(text, 'html.parser')

    def wirte_file(self, text, p):
        """
        写入文件
        """
        with open('{}/index.html'.format(p), 'w', encoding='utf8') as f:
            f.write(text)

    def get_remote_text(self, url_):
        """
        从远程获取数据
        """
        url = completion_url(self.baseUrl, url_)
        try:
            r = requests.get(url)
            return r
        except BaseException as e:
            print('请求异常啊', e, '\n-------------\n  {} \n ------------\n'.format(url))
            return None

    def down_image_base(self, text):
        """
        将base64字符串转化成二进制，写入图片文件
        """
        id_ = md5(text)
        codes = text.split(';base64,')
        if len(codes) > 1:
            t = codes[1]
        else:
            t = codes[0]
        imgdata = base64.b64decode(t)
        p = '{}/{}.jpg'.format(self.path, id_)
        with open(p, 'wb') as f:
            f.write(imgdata)
        return "./{}.jpg".format(id_)

    def replace_href(self, text):
        """
        将脚本中有关于url操作的代码替换掉
        """
        ident_list = [
            "href", "ancestorOrigins", "origin", "protocol", "host", "hostname",
            "port", "pathname", "search", "hash", "assign", "reload", "toString", "replace"
        ]
        text = text.replace('window.location.href', 'window.location.a')
        base = 'window.location'
        for ident in ident_list:
            a = '{}.{}'.format(base, ident)
            b = '{}.a'.format(base)
            text = text.replace(a, b)
        return text

    def down_css(self, url):
        """
        下载css文件到本地
        """
        print('一个css都没有吗')
        if 'data:image' in url:
            return None
        r = self.get_remote_text(url)
        if r == None:
            return None
        text = r.text
        name = md5(url)
        suffix_ = suffix(url)
        p = '{}/{}.{}'.format(self.path, name, suffix_)
        with open(p, 'w', encoding='utf8') as f:
            f.write(self.replace_href(text))
        return './{}.{}'.format(name, suffix_)

    def down_image_url(self, url):
        """
        将远程图片下载到本地
        """
        r = self.get_remote_text(url)
        if r == None:
            return None
        id_ = md5(url)
        p = '{}/{}.jpg'.format(self.path, id_)
        with open(p, 'wb') as f:
            f.write(r.content)
        return "./{}.jpg".format(id_)

    def down_file(self, url, selector):
        """
        下载文件
        """
        if selector == 'link':
            return self.down_css(url)
        elif selector == 'img':
            su = str(url)
            if is_base64_code(su) or ('data:image' in su and 'base64,' in su):
                text = url  # 图片以base64编码形式存在了src
                return self.down_image_base(text)
            else:
                return self.down_image_url(url)

    def parse_link(self, selector, arr):
        """
        解析传入的dom元素tag，将它下载到本地
        """
        ele_list = self.soup.find_all(selector)
        for index, ele in enumerate(list(ele_list)):
            e = ele_list[index]
            address = get(ele, arr, None)
            if isinstance(address, str) and 'chrome-extension' in address:
                e.decompose()
            elif address == None:
                continue
            else:
                local_path = self.down_file(address, selector)
                if local_path == None:
                    continue
                e[arr] = local_path
        self.text = str(self.soup)

    def del_tag(self, tag):
        """
        从文档中删除对于的tag
        """
        tags = to_array(tag)
        for t in tags:
            ele_list = self.soup.find_all(t)
            for ele in list(ele_list):
                ele.decompose()
            self.text = str(self.soup)

    def main(self):
        p = self.path
        self.parse_link('link', 'href')
        self.parse_link('img', 'src')
        self.del_tag(['script', 'iframe'])
        self.wirte_file(self.text, p)
        return {"id": self.id, "path": p}
