# coding=utf-8
'''
  Created by lyy on 2019-04-04
'''

__author__ = 'lyy'
from flask import render_template, jsonify
from app.model.res import Res
from app import create_app

app = create_app()


@app.route('/')
def index():
    return render_template('index.html')


# 捕获404异常
@app.errorhandler(404)
def error_404(e):
    status = 404
    msg = '服务器搬家了'
    info = ''
    res_json = Res(status, msg, info)
    return jsonify(res_json.__dict__)


# 捕获500异常
# @app.errorhandler(Exception)
# def error_500(e):
#     status = 500
#     msg = '服务器罢工了，请联系管理员'
#     info = {}
#     res_json = Res(status, msg, info)
#     return jsonify(res_json.__dict__)


if __name__ == '__main__':
    app.run(port=8000, debug=app.config['DEBUG'])
