# coding=utf-8
# data：2023/1/5-14:31
from django.urls import path

# from rest_framework.routers import DefaultRouter
from . import views

# router = DefaultRouter()
#
# router.register(r'', views.TaskView)
# router.register(r'step', views.StepView)
# router.register(r'', views.TaskResultView)

urlpatterns = [
    # path('result/', views.TaskResultView.as_view())
    path("", views.TaskViewApi.as_view(), name="任务"),
    path("<int:pk>/", views.TaskDetailViewApi.as_view(), name="任务详情"),
    path("step/<int:pre_step_id>", views.StepViewAPI.as_view(), name="新增step"),
    path(
        "<int:task_id>/step/<int:step_id>",
        views.StepDetailViewAPI.as_view(),
        name="step详情",
    ),
    path("<int:task_id>/execute", views.TaskExecuteApi.as_view(), name="执行任务"),
    path("result/<int:task_id>/<str:plan_id>", views.get_task_result, name="执行结果查询"),
]
# urlpatterns += router.urls
