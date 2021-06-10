#coding:utf8
from rest_framework import serializers
from django_redis import get_redis_connection

#ModelSerializer
#Serializer

# 我们的序列化器没有关联的模型
class RegisterSMSCodeSerializer(serializers.Serializer):

    text = serializers.CharField(label='验证码',max_length=4,min_length=4)
    image_code_id = serializers.UUIDField(label='uuid')



    #字段的类型 UUIDField
    #字段的选项 max_length=4
    # 单个字段校验
    # 多个字段校验

    def validate(self, attrs):

        # 我们需要把redis中的验证码获取出来之后 进行校验

        # 1. 用户提交的验证码拿到
        text = attrs.get('text')
        image_code_id = attrs.get('image_code_id')
        # 2. 获取redis中验证码
        # 2.1 连接
        redis_conn = get_redis_connection('code')
        # 2.2 获取
        redis_text = redis_conn.get('img_%s'%image_code_id)
        # 2.3过期 判断 redis_text 是否过期
        if redis_text is None:
            raise serializers.ValidationError('验证码以过期')
        # 2.4 主动删除已经获取到的 redis中数据
        redis_conn.delete('img_%s'%image_code_id)

        # 2.5 进行比对
        # rdis获取的数据是 bytes类型
        # 我们需要将字符串都转换为小写lower()
        if redis_text.decode().lower() != text.lower():
            raise serializers.ValidationError('验证码不正确')


        return attrs