import os
from pydash import get
from flask_cors import CORS
from db import create_table, insert_data, call
from copy_factory import CopyFactory
from tools import replace_fo, extract_html_text
from flask import Flask, redirect, abort, make_response, jsonify, send_file, request

app = Flask(__name__)
CORS(app, supports_credentials=True)
CORS(app, resources=r'/*')
create_table('data', 'id-id,path,text')


def init_folder(name):
    p = './dist/{}'.format(name)
    try:
        os.makedirs(p)
    except BaseException as e:
        print('异常', e)
    return p


def save_data(data):
    pass


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
        c = CopyFactory(value, p, href)
        c.main()
        data = {'id': c.id, 'path': c.path, 'text': extract_html_text(c.soup)}
        insert_data('data', data)
        return {'msg': '成功', 'code': '0'}


@app.route('/search', methods=['get'])
def search():
    api_param = request.args
    value = get(api_param, 'value', '')
    commad = f"select * from data where text like '{value}'"
    data = call(commad)
    return {"data": data}


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=9080,
        debug=True
    )
