# coding=utf-8
'''
  Created by lyy on 2019-04-30
'''
import requests

from app.model.log import Log
from app.model.res import Res
from app.secure import WX_AID, WX_ASK

from app.model import db

from app.utils.common_utils import get_date_now, get_ip_info
from app.api.v1.user import user
from flask import request, jsonify

__author__ = 'lyy'


# 微信的登录接口
@user.route('/wx_login', methods=['POST'])
def wx_login():
    code = request.form['code']
    url = 'https://api.weixin.qq.com/sns/jscode2session?appid=' + WX_AID + '&secret=' + WX_ASK + '&js_code=' + code + '&grant_type=authorization_code'
    res = requests.get(url)
    return jsonify(res.json())


# 将用户的访问信息存储到数据库中
@user.route('/log/create', methods=['POST'])
def logd():
    uid = request.form['uid']
    ip = request.remote_addr
    try:
        _ip = request.headers["X-Real-IP"]
        if _ip is not None:
            ip = _ip
    except Exception as e:
        print(e)

    try:
        ip_info = get_ip_info(ip)['data']
        country = ip_info['country']
        region = ip_info['region']
        city = ip_info['city']
        isp = ip_info['isp']

        log = Log(uid, ip, country, region, city, isp)
        db.session.add(log)
        db.session.commit()

        status = 200
        msg = '记录成功'
        info = {
            'id': log.id,
            'created_time': get_date_now()
        }

        res_json = Res(status, msg, info)

        return jsonify(res_json.__dict__)
    except Exception as e:
        print(e)
        status = 500
        msg = '记录失败'
        info = {}

        res_json = Res(status, msg, info)

        return jsonify(res_json.__dict__)
