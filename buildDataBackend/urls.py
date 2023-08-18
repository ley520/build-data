"""buildDataBackend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from config.LoggerConfig import logger

# 不要删除，在此初始化日志配置
logger.debug("项目启动，初始化URL配置")

schema_view = get_schema_view(
    openapi.Info(
        title="Build data API",
        default_version="v1",
        description="数据构造工具平台",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="112233@admin.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^docs/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
    path("debug/", include("debug_toolbar.urls")),
    path("silk/", include("silk.urls", namespace="silk")),
    path("connection/", include("apps.connection.urls")),
    path("user/", include("apps.user.urls")),
    path("task/", include("apps.task.urls")),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('mylogin/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
]
