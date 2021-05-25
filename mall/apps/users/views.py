from django.shortcuts import render
from rest_framework.views import APIView
from .models import User
from rest_framework.response import Response
# Create your views here.
# APIView
# GenericAPIView
# ListAPIView ,CreateAPIView
class RegisterUsernameView(APIView):

    """
    判断用户是否注册

    GET     /users/usernames/(?P<username>\w{5,20})/count/

    POST    序列化器

    我们需要把用户名发送过来, 接收用户,根据用户名进行判断
    用户是否注册


    """

    def get(self,request,username):

        # 通过用户名的个数
        count = User.objects.filter(username=username).count()
        # 组织数据,返回
        context = {
            'count':count,
            'username':username #可选
        }

        return Response(context)
