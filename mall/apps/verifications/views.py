from django.shortcuts import render

from libs.captcha.captcha import captcha
# 能够连接 redis
from django_redis import get_redis_connection

from . import constants

from django.http import HttpResponse

from rest_framework.views import APIView

from rest_framework.generics import GenericAPIView

from .serializers import RegisterSMSCodeSerializer

from random import randint

from libs.yuntongxun.sms import CCP

from rest_framework.response import Response
from rest_framework import status
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

# APIView
# GenericAPIView
# ListAPIView,CreateAPIView
class RegisterSMSCodeView(GenericAPIView):

    """
    根据用户提交的验证码,发送短信验证码

    GET    /verifications/smscodes/(?P<mobile>1[345789]\d{9})/?text=xxxx & image_code_id=xxxx



    1. 当我们点击按钮的时候 ,首先应该把 验证码的内容发送给我 我进行校验
    2. 校验成功了,我们需要给手机发送短信验证码
    3. 把短信存起来,设置有效期
    4. 我们需要设置发送的标记,放置用户频繁操作

    """

    serializer_class = RegisterSMSCodeSerializer

    def get(self,request,mobile):

        # 1.验证码内容的校验(序列化器)
        # 反序列化里有一步是进行数据的校验
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        # 2.判断用户是否已经有发送记录,防止用户频繁操作
        redis_conn = get_redis_connection('code')

        flag = redis_conn.get('sms_flag_%s'%mobile)
        if flag:
            return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)

        # 3.生成短信验证码
        sms_code = '%06d'%randint(0,999999)
        # 4.记录发送状态

        #短信验证码记录
        redis_conn.setex('sms_%s'%mobile,constants.SMS_CODE_EXIPRE_TIME,sms_code)
        #记录 发送状态
        redis_conn.setex('sms_flag_%s'%mobile,60,1)

        # 发送
        ccp = CCP()
        ccp.send_template_sms(mobile,[sms_code,5],1)

        return Response({'message':'ok'})

