# coding=utf-8
# data：2023/1/8-11:20

from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views

router = DefaultRouter()

router.register(r"", views.UserView)

urlpatterns = [
    path("test/", views.test_api),
    path("test1/", views.test_api_1),
]
urlpatterns += router.urls
