import datetime
import json
import os

from PIL import ImageDraw, Image, ImageFont
import textwrap

# 生成海报
from app.utils.common_utils import upload_file_to_qiniu, get_ran_dom

_path0 = os.getcwd()
_path_assets = _path0 + '/app/utils/image/face/assets/'
_path_output = _path0 + '/app/utils/image/face/output/'


# 制作海报
def make_face_post(info):
    background = _path_assets + 'background.jpg'
    font = _path_assets + 'simhei.ttf'
    p_maker = PostMaker(backImg=background, font=font)
    post_pic = _path_assets + 'base.jpg'

    qrImg = _path_assets + 'wxapp.jpg'
    p_maker.create(
        postPic=post_pic,
        qrImg=qrImg,
        info=info)
    post_url = upload_file_to_qiniu(str(get_ran_dom()) + '.jpg', _path_output + 'post.jpg')
    return post_url


class PostMaker(object):
    def __init__(self, backImg, font):
        self.backImg = backImg
        self.font = font

    def create(self, postPic, qrImg, info):
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
            font = ImageFont.truetype(self.font, 28, encoding="utf-8")
            # 获取需要添加的文字
            share_text = json.loads(str(info))['shareMsg']

            bg_w, bg_h = backImg.size
            postPic.thumbnail((bg_w, bg_h / 2))
            pic_w, pic_h = postPic.size

            # 文字换行设置
            astr = share_text

            para = textwrap.wrap(astr, width=13)

            # 将封面图粘贴到背景图的指定位置，第二个参数为坐标
            backImg.paste(postPic, (int((bg_w - pic_w) / 2), 80))

            draw = ImageDraw.Draw(backImg)

            h = pic_h + 80 + 150

            draw.text([40, h - 60], "经测试，我的标签为：", font=font, fill=(180, 180, 180))

            for postTitle in para:
                textWidth, textHeight = font.getsize(postTitle)
                draw.text([40, h], postTitle, font=font, fill=(0, 0, 0))
                h += (textHeight + 15)

            draw.text([40, h + 20], "你也快来试试吧～", font=font, fill=(0, 0, 0))

            qrImg = Image.open(qrImg)
            qrImg.thumbnail((180, 180))
            backImg.paste(qrImg, (bg_w - 220, pic_h + 180))
            font = ImageFont.truetype(self.font, 21, encoding="utf-8")
            draw.text([bg_w - 220, pic_h + 380], "微信扫码或长按识别", font=font, fill=(0, 0, 0))

            # today = datetime.date.today()
            # folder_path = 'output/' + str(today)

            backImg.save(_path_output + '/post.jpg')
        except Exception as e:
            raise e
