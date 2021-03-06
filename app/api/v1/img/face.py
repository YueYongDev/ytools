import datetime
import os
from concurrent.futures import ThreadPoolExecutor

from flask import request, jsonify

from app import create_app
from app.api.v1.img import img
from app.model import db
from app.model.face import Face
from app.model.res import Res
from app.utils.image.face.ai_face_beauty import faceIdentity
from app.utils.common_utils import get_date_now, upload_file_to_qiniu, get_ran_dom
from app.utils.image.face.face_share import make_face_post

__author__ = 'lyy'

path = os.getcwd() + '/app/utils/image/face'

executor = ThreadPoolExecutor(1)


# 测颜值
@img.route('/face/mark', methods=['POST'])
def face_mark():
    try:
        start = datetime.datetime.now()
        uid = request.form['uid']
        img = request.files.get('img')
        save_path = path + '/temp/' + 'face.jpg'
        img.save(save_path)

        result = faceIdentity(save_path)

        if result['error_code'] == 222304 or result['error_code'] == 222204:
            status = 500
            err_msg = '图片过大'
        elif result['error_code'] == 222202:
            status = 500
            err_msg = '没有发现人脸'
        elif result['error_code'] is not 0:
            status = 500
            err_msg = '服务器异常'
        else:
            save_face_to_db(result, uid, save_path)

            status = 200
            msg = '颜值打分成功'

            end = datetime.datetime.now()

            info = {
                'query_time': get_date_now(),
                'finish_time': (end - start).seconds,
                'result': result['result']
            }
            res_json = Res(status, msg, info)
            return jsonify(res_json.__dict__)

        info = {}
        res_json = Res(status, err_msg, info)
        return jsonify(res_json.__dict__)

    except Exception as e:
        print(e)
        status = 500
        info = {}
        msg = '服务器罢工了，请联系管理员'

        res_json = Res(status, msg, info)

        return jsonify(res_json.__dict__)


# 生成颜值检测结果的分享图片
@img.route('/face/share', methods=['POST'])
def get_face_share():
    start = datetime.datetime.now()
    img = request.files.get('img')
    info = request.form['info']
    save_path = path + '/assets/' + 'base.jpg'
    img.save(save_path)
    post_url = make_face_post(info)
    end = datetime.datetime.now()

    status = 200
    msg = '海报生成成功'
    info = {
        'query_time': get_date_now(),
        'finish_time': (end - start).seconds,
        'post_url': post_url
    }
    res_json = Res(status, msg, info)
    return jsonify(res_json.__dict__)


# 返回一定数量的人脸数据
@img.route('/face/get')
def get_face():
    page = request.args.get("page", default=1, type=int)

    faces = get_face_by_page(page)
    info = {
        'query_time': get_date_now(),
        'result': to_json(faces)
    }
    status = 200
    msg = '获取成功'
    res_json = Res(status, msg, info)
    return jsonify(res_json.__dict__)


# 保存人脸信息
def save_face(uid, filepath, face_age, face_gender, face_beauty):
    filename = str('face_' + get_ran_dom() + '.jpg').lower()
    face_url = upload_file_to_qiniu(filename, filepath)
    face = Face(uid, face_url, face_age, face_gender, face_beauty)
    try:
        app = create_app()
        with app.app_context():
            db.session.add(face)
            db.session.commit()
    except Exception as e:
        print(e)


# 将人脸数据存到数据库(异步)
def save_face_to_db(result, uid, save_path):
    result = result['result']
    face_age = result['face_list'][0]['age']
    face_gender = result['face_list'][0]['gender']['type']
    face_beauty = result['face_list'][0]['beauty']
    # save_face(uid, save_path, face_age, face_gender, face_beauty)
    executor.submit(save_face, uid, save_path, face_age, face_gender, face_beauty)


# 配合多个对象使用的函数
def to_json(all_vendors):
    v = [ven.dobule_to_dict() for ven in all_vendors]
    return v


# 根据page获取人脸数据
def get_face_by_page(page):
    index = [i for i in range(page * 20 - 19, page * 20)]
    faces = Face.query.filter(Face.id.in_(index)).all()
    return faces
