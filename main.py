import os
from pydash import get
from flask_cors import CORS
from copy_factory import CopyFactory
from db import create_table, insert_data, call
from tools import replace_fo, extract_html_text, md5
from flask import Flask, redirect, abort, make_response, jsonify, send_file, request, render_template, send_from_directory

app = Flask(__name__, template_folder='dist', static_folder='/dist')
CORS(app, supports_credentials=True)
CORS(app, resources=r'/*')
create_table('data', 'id-id,path,text,title,cover,description')
root = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "dist")  # html是个文件夹


def init_folder(href):
    name = md5(href)
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
    cover = get(api_param, 'cover', '')
    description = get(api_param, 'description', '')
    if isinstance(value, str) != True:
        return {'msg': 'html必须为字符串', 'code': '1'}
    else:
        p = init_folder(href)
        c = CopyFactory(value, p, href)
        c.main()
        data = {
            'id': c.id,
            'path': c.path,
            "title": title,
            "cover": cover,
            "description": description,
            'text': extract_html_text(c.soup),
        }
        insert_data('data', data)
        return {'msg': '成功', 'code': '0'}


@app.route('/search')
def search():
    api_param = request.args
    value = get(api_param, 'value', '')
    commad = f"select * from data where text like '%{value}%'"
    data = call(commad)
    res = []
    for item in data:
        d = {
            "id": item[0],
            'path': item[1],
            "title": item[3],
            "cover": item[4],
            "description": item[5],
        }
        res.append(d)
    return {"list": res}


@app.route('/html/<code>/', methods=['get'])
def html(code):
    return send_from_directory(f'./dist/{code}', 'index.html')


@app.route('/html/<code>/<file_name>', methods=['get'])
def link(code, file_name=None):
    return send_from_directory(f'./dist/{code}/', file_name)


@app.route('/', methods=['get'])
def main(code=None):
    remote = search()
    return render_template('index.html', remote=remote)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=9080,
        debug=True
    )
