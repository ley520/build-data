# coding=utf-8
# data：2023/1/5-20:13

from rest_framework import serializers
from .models import Connection, ConnectTypeEnum
from .scheme import MysqlScheme, RedisScheme


class ConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connection
        fields = "__all__"
        depth = 1

    def validate(self, attrs):
        connect_type = attrs.get("type")
        connect_param = attrs.get("connect_param")

        if connect_type not in ConnectTypeEnum.value:
            raise serializers.ValidationError("链接类型错误")

        if connect_type in [
            ConnectTypeEnum.mysql.value,
        ]:
            MysqlScheme(**connect_param)
        elif connect_type in [
            ConnectTypeEnum.redis.value,
        ]:
            RedisScheme(**connect_param)
        else:
            raise serializers.ValidationError("参数格式错误")

        return attrs


class ConnectionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connection
        fields = ["name", "type", "connect_param"]
        depth = 1
