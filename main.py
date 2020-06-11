from copy_factory import CopyFactory
import os
from tools import replace_fo
from pydash import get
from flask_cors import CORS
from flask import Flask, redirect, abort, make_response, jsonify, send_file, request

app = Flask(__name__)
CORS(app, supports_credentials=True)
CORS(app, resources=r'/*')


def init_folder(name):
    p = './dist/{}'.format(name)
    try:
        os.makedirs(p)
    except BaseException as e:
        print('异常', e)
    return p


@app.route('/copy_html', methods=['POST'])
def copy_html():
    api_param = request.get_json()
    value = get(api_param, 'html', None)
    title = get(api_param, 'title', '未定义')
    title = replace_fo(title)
    href = get(api_param, 'href', '')
    if isinstance(value, str) != True:
        return {'msg': 'html必须为字符串', 'code': '1'}
    else:
        p = init_folder(title)
        CopyFactory(value, p, href).main()
        return {'msg': '成功', 'code': '0'}


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=9080,
        debug=True
    )
