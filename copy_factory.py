import re
import base64
import requests
import threading
from pydash import get, sort_by
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
        self.css_list = []
        self.title = self.soup.title.string
        self.cover = ''
        self.description = ''

    def set_cover(self):
        imgs = self.soup.find_all('img')
        for img in imgs:
            src = get(img, 'src', '')
            if len(src) > 5:
                self.cover = completion_url(self.baseUrl, src)
                break

    def set_description(self):
        d = self.soup.select_one("meta[name='description']")
        self.description = get(d, 'content', '')

    def wirte_file(self, text, p):
        """
        写入文件
        """
        with open('{}/index.html'.format(p), 'w', encoding='utf8') as f:
            f.write(text)

    def get_remote_text(self, url_, selector):
        """
        从远程获取数据
        """
        url = completion_url(self.baseUrl, url_)
        try:
            r = requests.get(url)
            return r
        except BaseException as e:
            print('请求异常啊', e,
                  f'\n-------------\n  {url} \n ------------  {selector}\n')
            return None

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

    def down_css(self, url, e, selector):
        """
        下载css文件到本地
        """
        rel = get(e, 'rel[0]', None)
        if 'data:image' in url or rel != 'stylesheet':
            return None
        r = self.get_remote_text(url, selector)
        if r == None:
            return None
        text = r.text
        self.css_list.append(text)
        return

    def down_image_url(self, url, selector):
        """
        将远程图片下载到本地
        """
        r = self.get_remote_text(url, selector)
        if r == None:
            return None
        id_ = md5(url)
        p = '{}/{}.jpg'.format(self.path, id_)
        with open(p, 'wb') as f:
            f.write(r.content)
        return "./{}.jpg".format(id_)

    def down_file(self, url, selector, e):
        """
        下载文件
        """
        if selector == 'link':
            return self.down_css(url, e, selector)
        elif selector == 'img':
            su = str(url)
            if is_base64_code(su) or ('data:image/' in su):
                return None
            else:
                return self.down_image_url(url, selector)

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
                local_path = self.down_file(address, selector, ele)
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

    def insert_css(self):
        for css in self.css_list:
            markup = f'<style>{css}</style>'
            soup = BeautifulSoup(markup, 'html.parser')
            style = soup.style
            self.soup.head.insert_after(style)
        self.text = str(self.soup)

    def insert_js(self):
        markup = f'<script src="/file/images.js"></script>'
        soup = BeautifulSoup(markup, 'html.parser')
        script = soup.script
        self.soup.head.insert_after(script)
        self.text = str(self.soup)

    def main(self):
        p = self.path
        self.set_cover()
        self.set_description()
        self.parse_link('link', 'href')
        self.parse_link('img', 'src')
        self.del_tag(['script', 'iframe', 'link'])
        self.insert_css()
        self.insert_js()
        text = re.sub(r'^\s*\n', '', self.text)
        self.wirte_file(text, p)
        return self
