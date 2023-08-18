# coding=utf-8
# data：2023/2/7-20:43
from typing import Union, List

from guardian.shortcuts import get_objects_for_user, remove_perm, get_users_with_perms
from rest_framework.request import Request
from django.db.models import Model
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import User
from guardian.shortcuts import assign_perm
from loguru import logger


def user_have_permission(request: Request, instance, permission: str):
    """
    request: 请求
    instance: 要操作的对象，是一个model实例
    permission: 要判断的权限
    """
    user = request.user
    if not user.has_perm(permission, instance):
        raise PermissionDenied
    return True


def add_permission_when_create(
    request, app_name: str, model_name: str, instance: Union[Model, List[Model]]
):
    """
    @param request: 请求信息，必须包含用户信息
    @param app_name: model所在的app名称
    @param model_name: 定义的数据库表，填写类名即可，注意全部小写
    @param instance: model_name对应表的实例
    @return:
    """
    try:
        add_change_permission(request.user, app_name, model_name, instance)
        add_delete_permission(request.user, app_name, model_name, instance)
    except Exception as e:
        logger.error(f"赋予权限失败:\n{e}")


def add_change_permission(
    user: User, app_name: str, model_name: str, instance: Union[Model, List[Model]]
):
    """
    @param user: 用户实例
    @param app_name: model所在的app名称
    @param model_name: 定义数据库表的类名，全小写
    @param instance: model_name的实例
    @return:
    """
    assign_perm(f"{app_name}.change_{model_name}", user, instance)
    logger.info(f"为当前用户{user}添加对{instance}的修改权限")


def add_delete_permission(
    user: User, app_name: str, model_name: str, instance: Union[Model, List[Model]]
):
    """
    @param user: 用户实例
    @param app_name: model所在的app名称
    @param model_name: 定义数据库表的类名，全小写
    @param instance: model_name的实例
    @return:
    """
    assign_perm(f"{app_name}.delete_{model_name}", user, instance)
    logger.info(f"为当前用户{user}添加对{instance}的删除权限")


def remove_all_permission(instance: Model, permission_dict: dict):
    user_query_set = get_users_with_perms(instance)
    for user in user_query_set:
        for permission in permission_dict.values():
            remove_perm(permission, user, instance)


if __name__ == "__main__":
    pass
