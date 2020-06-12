import re
import base64
import requests
from pydash import get
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tools import ranstr, suffix, is_base64_code, to_array


class CopyFactory():
    def __init__(self, text, p, href):
        self.text = text
        self.path = p
        self.id = ranstr(16)
        self.baseUrl = href
        self.soup = BeautifulSoup(text, 'html.parser')

    def wirte_file(self, text, p):
        with open('{}/index.html'.format(p), 'w', encoding='utf8') as f:
            f.write(text)

    def get_remote_text(self, url_):
        url = url_
        if 'http' not in url_:
            url = urljoin(self.baseUrl, url_)
        try:
            r = requests.get(url)
            return r
        except BaseException as e:
            print('请求异常啊', e, '\n-------------\n  {} \n ------------\n'.format(url))
            return None

    def down_image_base(self, text):
        id_ = ranstr(12)
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
        r = self.get_remote_text(url)
        if r == None:
            return None
        text = r.text
        name = ranstr(12)
        suffix_ = suffix(url)
        p = '{}/{}.{}'.format(self.path, name, suffix_)
        with open(p, 'w', encoding='utf8') as f:
            f.write(self.replace_href(text))
        return './{}.{}'.format(name, suffix_)

    def down_image_url(self, url):
        r = self.get_remote_text(url)
        if r == None:
            return None
        id_ = ranstr(12)
        p = '{}/{}.jpg'.format(self.path, id_)
        with open(p, 'wb') as f:
            f.write(r.content)
        return "./{}.jpg".format(id_)

    def down_file(self, url, selector):
        if selector == 'link':
            return self.down_css(url)
        elif selector == 'img':
            if is_base64_code(url) or ('data:image/' in url and 'base64,' in url):
                text = url  # 图片以base64编码形式存在了src
                return self.down_image_base(text)
            else:
                return self.down_image_url(url)

    def parse_link(self, selector, arr):
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
