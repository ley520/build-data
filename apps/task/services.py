# coding=utf-8
# data：2023/2/13-22:35
from django.db import transaction
from django.db.models import Case, When
from django.forms import model_to_dict
from loguru import logger
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request

from .serializers import StepSerializer, TaskSerializer, StepUpdateSerializer
from .models import (
    Step,
    Task,
    task_permission_dict,
    StepTypeEnum,
    TaskResult,
    TaskRunStatus,
)
from utils.permissionUtil import (
    add_permission_when_create,
    remove_all_permission,
    user_have_permission,
)


@transaction.atomic
def create_task(request: Request):
    """
    创建一个数据构造任务
    @param request:
    @return:
    """
    # 构造task信息，并插入数据库
    task_info = request.data
    task_info["user_id"] = request.user.id
    task_serializer = TaskSerializer(data=task_info)
    task_serializer.is_valid(raise_exception=True)
    task_instance = task_serializer.save()
    add_permission_when_create(request, "task", "task", task_instance)
    # 初始化步骤信息，请求入参和结果模板
    params_step = {"name": "参数", "type": 10, "content": {}, "task_id": task_instance.id}
    result_step = {"name": "结果", "type": 20, "content": {}, "task_id": task_instance.id}
    step_serializer = StepSerializer(data=[params_step, result_step], many=True)
    step_serializer.is_valid(raise_exception=True)
    step_serializer.save()
    # for step in step_serializer.instance:
    #     add_permission_when_create(request, 'task', 'step', step)
    # 步骤信息添加到task
    update_task_steps = task_serializer.data
    update_task_steps["steps"] = {
        "step_list": [step["id"] for step in step_serializer.data]
    }
    update_task_serializer = TaskSerializer(
        instance=task_instance, data=update_task_steps
    )
    update_task_serializer.is_valid(raise_exception=True)
    update_task_serializer.save()
    logger.info(
        f"创建task初始化成功\ntask:{update_task_serializer.data}\nsteps:{step_serializer.data}"
    )
    result = update_task_serializer.data
    result["step_list"] = step_serializer.data
    return result


def query_task_info(task_id: int):
    """
    查询任务的信息并返回
    @param task_id:
    @return:
    """
    query_set = Task.objects.get(id=task_id)
    task_serializer = TaskSerializer(instance=query_set)
    pk_list = query_set.steps["step_list"]
    logger.info(f"task中的步骤顺序：{pk_list}")
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])
    step_query_set_list = Step.objects.filter(pk__in=pk_list).order_by(preserved)
    step_serializer = StepSerializer(instance=step_query_set_list, many=True)
    result = task_serializer.data
    result["steps"] = step_serializer.data
    return result, query_set


def query_task(request: Request, pk):
    """
    查询任务信息，并判断当前用户是否可编辑
    @param request:
    @param pk:
    @return:
    """
    result, query_set = query_task_info(pk)
    result["can_edit"] = user_have_permission(
        request, query_set, task_permission_dict["change"]
    )
    logger.info(result)
    return result


@transaction.atomic
def delete_task(pk: int):
    """
    删除数据构造任务
    @param pk:
    @return:
    """
    # 查询task及其关联的step
    task = Task.objects.get(id=pk)
    steps = Step.objects.filter(task_id=pk)
    # 移除该task所有的权限
    remove_all_permission(task, task_permission_dict)
    # 执行删除
    task.delete()
    steps.delete()


def create_step(request: Request, pre_step_id: int):
    """
    给指定task添加步骤
    @param request:
    @param pre_step_id:当前步骤的前一步骤id
    @return:
    """
    # 查询要修改的task信息
    task_info = Task.objects.get(id=request.data["task_id"])
    if not user_have_permission(request, task_info, task_permission_dict.get("change")):
        raise PermissionDenied
    # 保存step信息
    step_serializer = StepSerializer(data=request.data)
    step_serializer.is_valid(raise_exception=True)
    step_serializer.save()
    # 更新task中的步骤信息
    # 通过前置step的id，判断新增step的位置
    pre_index = task_info.steps["step_list"].index(pre_step_id)
    task_info.steps["step_list"].insert(pre_index + 1, step_serializer.instance.id)
    task_info.save()
    return step_serializer.data


@transaction.atomic
def update_step(request: Request, *args, **kwargs):
    step_id = kwargs.get("step_id")
    task_id = kwargs.get("task_id")
    task_info = Task.objects.get(id=task_id)
    step_info = Step.objects.get(id=step_id)
    if not user_have_permission(request, task_info, task_permission_dict.get("change")):
        raise PermissionDenied
    serializer = StepUpdateSerializer(instance=step_info, data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.data


@transaction.atomic
def delete_step(request: Request, *args, **kwargs):
    step_id = kwargs.get("step_id")
    # step_info = Step.objects.get(id=step_id)
    task_id = kwargs.get("task_id")
    task_info = Task.objects.get(id=task_id)
    if not user_have_permission(request, task_info, task_permission_dict.get("change")):
        raise PermissionDenied
    for _step_id in task_info.steps["step_list"]:
        if _step_id == step_id:
            task_info.steps["step_list"].remove()
            break
    task_info.save()
    Step.objects.get(pk=step_id).delete()


def build_result(step_info, query_result_dict):
    if step_info["type"] == StepTypeEnum.TASK.value:
        task_info, query_set = query_task_info(step_info["content"]["task_id"])
        result = []
        for step in task_info["steps"]:
            result.append(build_result(step, query_result_dict))
        return result
    else:
        return query_result_dict[f"{step_info['task_id']}+{step_info['id']}"]


def query_task_result(task_id, plan_id):
    task = Task.objects.get(id=task_id)
    step_id_list = task.steps["step_list"]
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(step_id_list)])
    step_query_set_list = TaskResult.objects.filter(step_id__in=step_id_list).order_by(
        preserved
    )
    step_serializer = StepSerializer(instance=step_query_set_list, many=True)

    task_info, query_set = query_task_info(task_id)
    query_result: list[TaskResult] = TaskResult.objects.filter(plan_id=plan_id)
    query_result_dict = {}
    for taskResult in query_result:
        query_result_dict[
            f"{taskResult.task_id}+{taskResult.step_id}"
        ] = taskResult.content

    result = []
    for step in task_info["steps"]:
        step["result"] = query_result_dict[f"{step['task_id']}+{step['id']}"]
        if step["type"] == StepTypeEnum.TASK.value:
            result.append(
                {
                    "name": step["name"],
                    "result": build_result(step, query_result_dict),
                }
            )
    resp_dict = {
        "data": result,
        "status": TaskRunStatus.objects.get(plan_id=plan_id).status,
    }
    return resp_dict
