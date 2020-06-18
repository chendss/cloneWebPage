import os
from pydash import get
from flask_cors import CORS
from copy_factory import CopyFactory
from db import create_table, insert_data, call
from tools import replace_fo, extract_html_text, md5
from flask import Flask, redirect, abort, make_response, jsonify, send_file, request, render_template, send_from_directory

create_table('data', 'id-id,path,text,title,cover,description')  # 创建一张表

app = Flask(__name__, template_folder='template', static_folder='/dist')
CORS(app, supports_credentials=True)
CORS(app, resources=r'/*')
root = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "dist")  # html是个文件夹


def init_folder(href):
    """
    初始化文件夹，如果不存在，则递归创建
    """
    name = md5(href)
    p = './dist/{}'.format(name)
    try:
        os.makedirs(p)
    except BaseException as e:
        print('异常', e)
    return p


def insert_db(href, html):
    p = init_folder(href)
    c = CopyFactory(html, p, href).main()
    data = {
        'id': c.id,
        'path': c.path,
        "title": c.title,
        "cover": c.cover,
        "description": c.description,
        'text': extract_html_text(c.soup),
    }
    insert_data('data', data)  # 插入数据到数据库


@app.route('/copy_html', methods=['POST'])
def copy_html():
    api_param = request.get_json()
    value = get(api_param, 'html', None)
    href = get(api_param, 'href', '')
    if isinstance(value, str) != True:
        return {'msg': 'html必须为字符串', 'code': '1'}
    else:
        insert_db(href, value)
        return {'msg': '成功', 'code': '0'}


# @app.route('/copy_html', methods=['get'])
# def copy_html_url():
#     """
#     通过url保存网页
#     """
#     api_param = request.args()
#     url = get(api_param, 'url', None)
#     if isinstance(value, str) != True:
#         return {'msg': 'html必须为字符串', 'code': '1'}
#     else:
#         p = init_folder(href)
#         c = CopyFactory(value, p, href)
#         c.main()
#         data = {
#             'id': c.id,
#             'path': c.path,
#             "title": title,
#             "cover": cover,
#             "description": description,
#             'text': extract_html_text(c.soup),
#         }
#         insert_data('data', data)  # 插入数据到数据库
#         return {'msg': '成功', 'code': '0'}


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
    """
    返回html文件 code->url转成的md5码
    """
    p = f'./dist/{code}/index.html'
    if os.path.exists(p):
        return send_from_directory(f'./dist/{code}', 'index.html')
    else:
        return send_from_directory(f'./dist/{code}', 'index.mhtml')


@app.route('/html/<code>/<file_name>', methods=['get'])
def link(code, file_name=None):
    """
    返回对应html的静态资源文件
    """
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
