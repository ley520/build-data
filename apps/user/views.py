from django.contrib.auth.hashers import make_password, check_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    UpdateAPIView,
    RetrieveAPIView,
)
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenViewBase
from rest_framework.decorators import api_view
from rest_framework.response import Response

# from .models import User
from django.contrib.auth.models import User
from .serializers import UserSerializer, MyTokenObtainPairSerializer
from config.pagination import Pagination


@api_view(["get"])
def test_api(request):
    return Response({"message": {"id": "id", "name": "name"}})


@api_view(["get"])
def test_api_1(request):
    return Response("success")


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        pwd = request.POST.get("password")
        user = User.objects.filter(user_name=username)
        User.objects.create_user()


class UserView(ModelViewSet):
    queryset = User.objects.filter()
    serializer_class = UserSerializer
    pagination_class = Pagination

    def post(self, request, *args, **kwargs):
        request.data["password"] = make_password(request.data["password"])
        return self.create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        request.data["password"] = make_password(request.data["password"])
        return self.update(request, *args, **kwargs)

    # @swagger_auto_schema(query_serializer=UserSerializer(fields=('id', 'username')), responses={200: UserSerializer()})
    # def get(self, request):
    #     query_params = request.query_params
    #     query_set = self.get_queryset().filter(Q(username=query_params.get('username')) | Q(id=query_params.get('id')))
    #     serializer = self.get_serializer(instance=query_set, many=True)
    #     return Response(serializer.data)
    #
    # @swagger_auto_schema(request_body=UserSerializer, responses={200: UserSerializer()})
    # def post(self, request, *args, **kwargs):
    #     body = request.data
    #     serializer = self.get_serializer(data=body)
    #     serializer.is_valid()
    #     serializer.save()
    #     return Response(serializer.data)


class MyTokenObtainPairView(TokenObtainPairView):
    """
    自定义得到token username: 账号或者密码 password: 密码或者验证码
    """

    serializer_class = MyTokenObtainPairSerializer


class MyTokenRefreshView(TokenViewBase):
    """
    自定义刷新token refresh: 刷新token的元素
    """

    serializer_class = TokenRefreshSerializer
