from flask_cors import CORS
from flask import Flask, redirect, abort, make_response, jsonify, send_file, request
from pydash import get

app = Flask(__name__)
CORS(app, supports_credentials=True)
CORS(app, resources=r'/*')


@app.route('/copy_html', methods=['POST'])
def copy_html():
    api_param = request.get_json()
    value = get(api_param, 'html', None)
    title = get(api_param, 'title', '未定义')
    if value is None:
        return {'msg': 'html不许为空', 'code': '1'}
    else:
        with open('./dist/{}.html'.format(title), 'w') as f:
            f.write(value)
        return {'msg': '成功', 'code': '0'}


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=9080,
        debug=True
    )
