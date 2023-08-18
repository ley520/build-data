# coding=utf-8
# data：2023/1/5-14:31


from django.urls import path
from . import views

# from rest_framework.routers import DefaultRouter
# router = DefaultRouter()
# router.register(r'', views.ConnectionView)

urlpatterns = [
    path("connection/", views.ConnectionViewApi.as_view(), name="连接信息"),
    path("connection/<int:pk>/", views.ConnectionViewDetailApi.as_view(), name="链接详情"),
]
# urlpatterns += router.urls
