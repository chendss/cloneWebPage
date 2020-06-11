import re
import base64
import requests
from pydash import get
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tools import ranstr, suffix, is_base64_code


class CopyFactory():
    def __init__(self, text, p, href):
        self.text = text
        self.path = p
        self.baseUrl = href
        self.soup = BeautifulSoup(text, 'html.parser')

    def wirte_file(self, text, p):
        with open('{}/index.html'.format(p), 'w', encoding='utf8') as f:
            f.write(text)

    def get_remote_text(self, url_):
        url = url_
        if 'data:image/' in url_:
            return url_
        if 'http' not in url_:
            url = urljoin(self.baseUrl, url_)
        try:
            r = requests.get(url)
            text = r.text
            return text
        except BaseException as e:
            print('请求异常啊', e, '-------------  {}  ------------'.format(url))
            return None

    def down_image(self, text):
        id_ = ranstr(12)
        print('base 64\n', text, '\n')
        imgdata = base64.b64decode(text)
        p = "./{}.jpg".format(id_)
        with open(p, 'wb') as f:
            f.write(imgdata)
        return p

    def replace_href(self, text):
        return text.replace('window.location.href', 'window.location.a')

    def down_file(self, url):
        text = self.get_remote_text(url)
        if text == None:
            return None
        if is_base64_code(text) and 'data:image/' in text:
            return self.down_image(text)
        name = ranstr(12)
        suffix_ = suffix(url)
        p = '{}/{}.{}'.format(self.path, name, suffix_)
        with open(p, 'w', encoding='utf8') as f:
            f.write(self.replace_href(text))
        return './{}.{}'.format(name, suffix_)

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
                local_path = self.down_file(address)
                if local_path == None:
                    continue
                e[arr] = local_path
        self.text = str(self.soup)

    def del_img(self):
        ele_list = self.soup.find_all('script')
        for ele in list(ele_list):
            ele.decompose()
        self.text = str(self.soup)

    def main(self):
        p = self.path
        self.parse_link('link', 'href')
        self.parse_link('img', 'src')
        self.del_img()
        self.wirte_file(self.text, p)
