import random

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random
import string  # string字符串


def get_valid_Code_img(request):

    # # 方式一：
    # with open('content1.png','rb')as f:
    #     data=f.read()
    # return HttpResponse(data)

    # 方式二 # pip install pillow # python下的图像处理模块
    # import random
    # def get_random_color():
    #     return (random.randint(0,255),random.randint(0,255),random.randint(0,255))
    # from PIL import Image
    # img=Image.new('RGB',(270,34),color=get_random_color())
    # with open('1.png','wb') as f:
    #      img.save(f,'png')
    # with open('1.png', 'rb') as f:
    #     data=f.read()
    #
    # return HttpResponse(data)

    # 方式三 内存处理
    # import random
    # def get_random_color():
    #     return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    #
    # from PIL import Image
    # from io import BytesIO
    # img = Image.new('RGB', (270, 34), color=get_random_color())
    # f=BytesIO()
    # img.save(f,'png')
    # data=f.getvalue()
    # return HttpResponse(data)

    # 方式四
    import random,string
    def get_random_color():
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO
    img = Image.new('RGB', (270, 34), color=get_random_color())
    # 画笔 draw
    draw = ImageDraw.Draw(img)
    kumo_font = ImageFont.truetype('static/font/kumo.ttf', size=32)
    code = ''
    valid_code_str = ''
    for i in range(5):
        random_num = random.randint(0, 9)
        random_low_alpha = chr(random.randint(65, 90))
        random_upper_alpha = chr(random.randint(97, 122))
        add = random.choice([random_num, random_low_alpha, random_upper_alpha])
        # add2=random.choice(string.ascii_letters+string.digits)
        # code = ''.join([code,str(add)])
        draw.text((i * 50 + 20, 5), str(add), get_random_color(), font=kumo_font)  # 画文字

        # 保存验证码字符串
        valid_code_str += str(add)

    # draw.line()#画线
    # draw.point()#画点

    # 补充噪点噪线 防止机器识别

    # 噪线
    width, height = 210, 35
    for i in range(1):
        x1 = random.randint(0, width)
        x2 = random.randint(0, width)
        y1 = random.randint(0, width)
        y2 = random.randint(0, width)
        draw.line((x1, y1, x2, y2), fill=get_random_color())

    # 噪点
    for i in range(25):
        draw.point([random.randint(0, width), random.randint(0, height)], fill=get_random_color())
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.arc((x, y, x + 4, y + 4), 0, 90, fill=get_random_color())

    print(valid_code_str)

    # 生成的字符串---验证码  valid_code_str
    request.session['valid_code_str'] = valid_code_str
    '''
    1 assdd
    2 COOKIE {'sessionid':assdd }
    session-key   session-data

    '''

    f = BytesIO()
    img.save(f, 'png')
    data = f.getvalue()
    return data
