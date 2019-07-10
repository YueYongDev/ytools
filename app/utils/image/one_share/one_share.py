import datetime
import os
import textwrap

import requests
from PIL import ImageDraw, Image, ImageFont

from app.utils.common_utils import upload_file_to_qiniu

_path0 = os.getcwd()
_path_assets = _path0 + '/app/utils/image/one_share/assets/'
_path_output = _path0 + '/app/utils/image/one_share/output/'


# 生成海报
def make_post():
    one_info = get_one_info()
    background = _path_assets + 'background.jpg'
    font = _path_assets + 'simhei.ttf'
    p_maker = PostMaker(backImg=background, font=font)
    post_pic = _path_assets + 'base.jpg'

    qrImg = _path_assets + 'wxapp.jpg'
    p_maker.create(
        postPic=post_pic,
        qrImg=qrImg,
        one_info=one_info)
    today = datetime.date.today().strftime('%y%m%d')
    post_url = upload_file_to_qiniu('one_' + str(today) + '.jpg', _path_output + 'post.jpg')
    return post_url, one_info


# 获取one的信息
def get_one_info():
    res = requests.get("https://v1.itooi.cn/one/day").json()

    if res['code'] == 200:
        data = res['data']
        date = data['post_date'].split(' ')[0]
        img_url = data['img_url']
        title = data['title']
        pic_info = data['pic_info']
        forward = data['forward']
        words_info = data['words_info']

        download_img(img_url)

        one_info = (date, img_url, title, pic_info, forward, words_info)

    else:
        one_info = ('2019-07-01', "title", "title", "test", "test", "test")

    return one_info


# 下载图片函数
def download_img(url):
    """"
    下载指定url的图片
    url：图片的url；
    name:保存图片的名字
    """
    try:
        response = requests.get(url)
        f_img = response.content
        path = _path_assets + 'base.jpg'
        with open(path, "wb")as f:
            f.write(f_img)
    except Exception as e:
        raise e


class PostMaker(object):
    def __init__(self, backImg, font):
        self.backImg = backImg
        self.font = font

    def create(self, postPic, qrImg, one_info):
        """
        @postPic: 文章封面图
        @postTitle 文章标题
        @qrImg: 文章二维码
        """
        try:
            # 获取背景图
            backImg = Image.open(self.backImg)
            # 获取封面图
            postPic = Image.open(postPic)
            # 获取字体
            font = ImageFont.truetype(self.font, 36, encoding="utf-8")
            # 获取需要添加的文字
            date, img_url, title, pic_info, postTitle, words_info = one_info

            bg_w, bg_h = backImg.size
            pic_w, pic_h = postPic.size

            # 文字换行设置
            astr = postTitle

            para = textwrap.wrap(astr, width=23)

            # 将封面图粘贴到背景图的指定位置，第二个参数为坐标
            backImg.paste(postPic, (int((bg_w - pic_w) / 2), 200))

            draw = ImageDraw.Draw(backImg)

            h = 850
            for postTitle in para:
                textWidth, textHeight = font.getsize(postTitle)
                draw.text([(bg_w - textWidth) / 2, h], postTitle, font=font, fill=(0, 0, 0))
                h += textHeight

            date = str(date).replace('-', '/')

            font = ImageFont.truetype(_path_assets + 'simhei.ttf', 40, encoding="utf-8")
            text_color = (169, 169, 169)

            draw.text([(bg_w - font.getsize(date)[0]) / 2, 100], date, font=font, fill=text_color)

            kind = str(title) + " | " + str(pic_info)
            draw.text([(bg_w - font.getsize(kind)[0]) / 2, 750], kind, font=font, fill=text_color)

            draw.text([(bg_w - font.getsize(words_info)[0]) / 2, 1000], words_info, font=font, fill=text_color)

            qrImg = Image.open(qrImg)
            qrImg.thumbnail((200, 200))
            backImg.paste(qrImg, (bg_w - 280, bg_h - 280))

            # today = datetime.date.today()
            # folder_path = 'output/' + str(today)

            backImg.save(_path_output + '/post.jpg')
        except Exception as e:
            raise e


if __name__ == '__main__':
    make_post()
