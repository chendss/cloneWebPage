import math


def encrypt(content):
    result = ''
    for si in content:
        o = ord(si)
        result += str(o)
    print('10进制转16进制', result, hex(int(result)))
    return result
