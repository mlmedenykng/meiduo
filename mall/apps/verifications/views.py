from django.shortcuts import render

from libs.captcha.captcha import captcha
# 能够连接 redis
from django_redis import get_redis_connection

from . import constants

from django.http import HttpResponse

from rest_framework.views import APIView
# Create your views here.

class RegisterImageCodeView(APIView):

    """
    我们生成验证码的接口

    GET      /verifications/imagecodes/(?P<image_code_id>.+)/



    1. 要不要进行参数的传递.  需要传递参数, 因为我们获取了验证码图片之后,肯定是需要进行校验
        所以我们需要传递一个 能够确保校验的时候能够找到对应的比对对象
    2. 验证码生成图片的同时需要 把生成的校验码 保存起来 -->redis


    """

    def get(self,request,image_code_id):

        # 1.生成图片和验证码
        text,image = captcha.generate_captcha()
        #把验证码保存到redis中

        # 2.1 连接reidis, get_redis_connection 参数 是 setting中 reids的
        redid_conn = get_redis_connection('code')
        # 2.2 把验证码保存起来
        redid_conn.setex('img_%s'%image_code_id,constants.IMAGE_CODE_EXPIRE_TIME,text)

        # 3.返回图片
        # content_type =  mime
        # text/javascript image/jpeg
        return HttpResponse(image,content_type='image/jpeg')

