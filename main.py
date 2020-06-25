import os
import requests
import shutil
from pydash import get
from flask_cors import CORS
from copy_factory import CopyFactory
from db import create_table, insert_data, call, del_data, search_data
from tools import replace_fo, extract_html_text, md5, request_get
from flask import Flask, redirect, abort, make_response, jsonify, send_file, request, render_template, send_from_directory

create_table('data', 'id-id,path,text,title,cover,description,url')  # 创建一张表
call('ALTER TABLE data ADD url TEXT')

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
        "url": href,
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


@app.route('/copy_html', methods=['get'])
def copy_html_url():
    """
    通过url保存网页
    """
    api_param = request.args
    url = get(api_param, 'url', None)
    headers = {
        "cookie": 'ESSIONID=GuyP8EwRLc154qIMC3InBeIwgyBduSh9fjLfLURLJxh; osd=U1sQAE_HDjIqt7WNP8VZJlECG_oqrkVEZOb08lH2P3lOwtPVakkb2XawsY0-dLj03eK24vJJvwFq0pccAaSqrqQ=; JOID=UVoRAEzFDzMqtLeMPsVaJFADG_kor0REZ-T181H1PXhPwtDXa0gb2nSxsI09drn13eG04_NJvANr05cfA6Wrrqc=; _zap=e4ddf4cf-dab4-4339-97d3-28e72ce038c9; d_c0="AGCkmXnMGQ-PTtimmVfY5D-UTklOSaS5zqQ=|1552209361"; _xsrf=W4vhcg426UTtYnnbSMbuYCQBz7l9tOOB; z_c0="2|1:0|10:1584634139|4:z_c0|92:Mi4xY1k4WkFBQUFBQUFBWUtTWmVjd1pEeVlBQUFCZ0FsVk5HLWRnWHdDT3dqNjRqdkNQRHY2bV9sd2hBVHVjTjRhYWNB|426b71d348e6ae3ad3e6f0bc27e68fc8092eae0971087a0835f597126e27cff7"; q_c1=0983cc9afbc141bb964f3f16a31ea50b|1590245539000|1552578753000; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1592017641; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1592017641; KLBRSID=975d56862ba86eb589d21e89c8d1e74e|1592498518|1592497242',
        "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    }
    text = request_get(url, headers)
    if text == None or url == None:
        return {'msg': '无法获得html内容', 'code': '1'}
    else:
        insert_db(url, text)
        return {'msg': '成功', 'code': '0'}


@app.route('/del_html', methods=['post'])
def del_html():
    api_param = request.get_json()
    id_ = get(api_param, 'data.id', None)
    db_data = search_data('data', {"id": id_})
    p = get(db_data, 'path', '')
    shutil.rmtree(p)
    del_data('data', {"id": id_})
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
            "url": item[6],
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
        result = send_from_directory(f'./dist/{code}', 'index.html')
    else:
        result = send_from_directory(f'./dist/{code}', 'index.mhtml')
    return result


@app.route('/html/<code>/<file_name>', methods=['get'])
def link(code, file_name=None):
    """
    返回对应html的静态资源文件
    """
    return send_from_directory(f'./dist/{code}/', file_name)


@app.route('/file/<file_name>', methods=['get'])
def file_get(file_name=None):
    return send_from_directory(f'./template/', file_name)


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
