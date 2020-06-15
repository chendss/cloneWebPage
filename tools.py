import re
import os
import random
import hashlib
import binascii
from urllib.parse import urljoin


def replace_fo(s):
    """
    过滤掉window文件夹不支持的符号
    """
    pattern = r'[\\/:*?"<>|\r\n]+'
    result = re.sub(pattern, '-', s)
    return result


def ranstr(num):
    """
    生成随机字符串,并且保证开头不会为数字
    """
    H = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    H_ = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    salt = ''
    for _ in range(num-1):
        salt += random.choice(H)
    salt = random.choice(H_)+salt
    return salt


def suffix(s):
    st = os.path.splitext(s)[-1]
    result = st[1:]
    result = result.split('?')[0]
    return result


def is_base64_code(s):
    """
    判断是否是一个base64字符串
    """
    '''Check s is Base64.b64encode'''
    _base64_code = [
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
        'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
        'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a',
        'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
        'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
        't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1',
        '2', '3', '4', '5', '6', '7', '8', '9', '+',
        '/', '='
    ]

    # Check base64 OR codeCheck % 4
    code_fail = [i for i in s if i not in _base64_code]
    if code_fail or len(s) % 4 != 0:
        return False
    return True


def to_array(s):
    """
    转化成数组
    """
    if isinstance(s, list):
        return s
    else:
        return [s]


def extract_html_text(soup):
    """
    提取html文本内容，以便搜索
    """
    list_ = soup.find_all(True)
    result = ''
    l = ['script', 'style', 'link', 'img', 'link', 'meta']
    for ele in list_:
        s = ele.string
        name = ele.name
        if s == None or name in l:
            continue
        else:
            result += f' {s}'
    result = re.sub(r'\n', '', result)
    return result


def md5(s):
    """
    字符串加密成md5 - 为了解决中文路径访问的问题
    """
    hl = hashlib.md5()
    hl.update(s.encode(encoding='utf-8'))
    result = hl.hexdigest()
    return result


def completion_url(baseUrl, url_):
    """
    补全url
    """
    url = url_
    if 'http' not in url_:
        url = urljoin(baseUrl, url_)
    return url
