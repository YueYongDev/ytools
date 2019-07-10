from sqlalchemy import Column, Integer, String

from app.model import db
from app.utils import common_utils

__author__ = 'lyy'


class One(db.Model):
    # 表的名字:
    __tablename__ = 'one'

    # 日志记录的id
    id = Column(Integer, primary_key=True, autoincrement=True)

    date = Column(String(50), nullable=False)

    img_url = Column(String(1024), nullable=False)

    title = Column(String(50), nullable=False)

    pic_info = Column(String(1024), nullable=False)

    forward = Column(String(50), nullable=False)

    words_info = Column(String(50), nullable=False)

    post_url = Column(String(1024), nullable=False)

    created_time = Column(String(50), nullable=False)

    def __init__(self, date, img_url, title, pic_info, forward, words_info, post_url):
        self.date = date
        self.img_url = img_url
        self.title = title
        self.pic_info = pic_info
        self.forward = forward
        self.words_info = words_info
        self.post_url = post_url
        self.created_time = common_utils.get_date_now()
