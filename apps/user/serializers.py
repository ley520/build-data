# coding=utf-8
# data：2023/1/5-20:13

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth.models import update_last_login

# from .models import User
from django.contrib.auth.models import User
from apps.BaseModel import SelfBaseSerializers


class UserSerializer(SelfBaseSerializers):
    class Meta:
        model = User
        fields = "__all__"
        exclude = []
        depth = 1
        # read_only_fields = ['id']
        extra_kwargs = {
            "id": {"read_only": True, "required": False},
            "username": {
                "allow_blank": False,
                "allow_null": False,
                "required": False,
                "error_messages": {"allow_blank": "用户名不能为空"},
            },
            "password": {
                "write_only": True,
                "min_length": 6,
                "max_length": 64,
            },
            "status": {
                "default": True,
                "read_only": True,
            },
        }


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        # 以下两个是自定义返回
        data["user_id"] = self.user.id
        data["username"] = self.user.username

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data
