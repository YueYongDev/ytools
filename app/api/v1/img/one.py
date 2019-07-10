import datetime

from flask import jsonify

from app.api.v1.img import img
from app.model import db
from app.model.one import One
from app.model.res import Res
from app.utils.common_utils import get_date_now
from app.utils.image.one_share.one_share import make_post


@img.route('/one/share', methods=['GET'])
def one_share():
    start = datetime.datetime.now()
    img_url = get_post_url()
    end = datetime.datetime.now()

    msg = '日签获取成功'
    status = 200
    info = {
        'img_url': img_url,
        'query_time': get_date_now(),
        'finish_time': (end - start).seconds
    }
    res_json = Res(status, msg, info)

    return jsonify(res_json.__dict__)


# 获取每天的postUrl
def get_post_url():
    # 获取今天的日期
    today = str(datetime.date.today())
    # 根据日期从数据库中获取记录
    one = One.query.filter(One.date == today).first()
    # 如果记录不存在就执行生成操作
    if one is None:
        print("生成")
        post_url, one_info = make_post()
        date, img_url, title, pic_info, forward, words_info = one_info
        # 构造对象
        one = One(date=date, img_url=img_url, title=title, pic_info=pic_info, forward=forward, words_info=words_info,
                  post_url=post_url)
        # 插入数据
        insert(one)
        return post_url
    # 如果记录存在直接返回
    else:
        print("从数据库获取")
        return one.post_url


# 插入数据
def insert(one):
    db.session.add(one)
    db.session.commit()
    return one.id
