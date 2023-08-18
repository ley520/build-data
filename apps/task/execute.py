# coding=utf-8
# data：2023/2/22-14:16
import orjson
import pymysql
import pymysql.cursors
from pymysql.cursors import DictCursor
import requests
import redis
from loguru import logger
from django.db.models import Case, When

from apps.connection.models import Connection, ConnectTypeEnum
from apps.task.models import Task, Step, StepTypeEnum, TaskResult, TaskRunStatus
from .parser import replace_values


class Context:
    def __init__(
        self,
        task_id: int,
        plan_id: str,
        variables_mapping=None,
    ):
        self.variables_mapping = variables_mapping or {}
        self.plan_id = plan_id
        self.task_id = task_id


def add_result_to_context_and_save(step_info: Step, context: Context, result):
    """
    执行结果添加到上下文中，并把结果保存到数据库
    @param step_info:
    @param context:
    @param result:
    @return:
    """
    context.variables_mapping[step_info.id] = result
    TaskResult(
        plan_id=context.plan_id,
        task_id=context.task_id,
        step_id=step_info.id,
        step_type=step_info.type,
        content=result,
    ).save()


def run_param_step(step_info: Step, context: Context):
    """
    @param step_info:
    @param context:
    @return:
    """
    logger.info("执行:run_param_step")
    # content = replace_values(step_info.content, context.variables_mapping)
    add_result_to_context_and_save(step_info, context, context.variables_mapping.get(0))


def run_http_step(step_info: Step, context: Context):
    """
    执行类型为http的step,并把响应结果转为JSON后存入数据库并添加context
    @param step_info:
    @param context:
    @return:
    """
    logger.info("执行:run_http_step")
    content = replace_values(step_info.content, context.variables_mapping)
    resp = requests.request(**content)
    add_result_to_context_and_save(step_info, context, resp.json())


def run_sql_with_mysql(connect_info: Connection, sql: str):
    """
    连接数据库并执行SQL，返回执行结果
    @param connect_info:
    @param sql:
    @return:
    """
    with pymysql.connect(
        cursorclass=DictCursor, **connect_info.connect_param
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            connection.commit()
            result = cursor.fetchall()
            return result


def run_sql_step(step_info: Step, context: Context):
    """
    执行类型为SQL的step,并把响应结果转为JSON后存入数据库并添加context
    @param step_info:
    @param context:
    @return:
    """
    logger.info("执行:run_sql_step")
    content = replace_values(step_info.content, context.variables_mapping)
    connect_id = content.get("connect_id")
    sql = content.get("sql")
    connect_info = Connection.objects.get(id=connect_id)
    result = None
    if connect_info.type == ConnectTypeEnum.mysql.value:
        result = run_sql_with_mysql(connect_info, sql)
    add_result_to_context_and_save(step_info, context, result)


def run_redis_step(step_info: Step, context: Context):
    """
    执行类型为Redis的step,并把响应结果转为JSON后存入数据库并添加context
    @param step_info:
    @param context:
    @return:
    """
    logger.info("执行:run_redis_step")
    content = replace_values(step_info.content, context.variables_mapping)
    connect_id = content.get("connect_id")
    connect_info = Connection.objects.get(id=connect_id)
    action = content.get("action")
    with redis.Redis(**connect_info.connect_param) as r:
        result = None
        key = content.get("key")
        value = content.get("value")
        if action == "get":
            get_result = r.get(key)
            if get_result is not None:
                result = get_result.decode()
        elif action == "set":
            result = r.set(key, **value)
        elif action == "delete":
            result = r.delete(key)
        else:
            result = f"暂不支持{action}操作"
        add_result_to_context_and_save(step_info, context, result)


def run_result_step(step_info: Step, context: Context):
    """
    执行类型为Result的step,并把响应结果转为JSON后存入数据库并添加context
    @param step_info:
    @param context:
    @return:
    """
    logger.info("执行:run_result_step")
    content = replace_values(step_info.content, context.variables_mapping)
    add_result_to_context_and_save(step_info, context, content)
    return content


def run_task_step(step_info: Step, context: Context):
    logger.info("执行:run_task_step")
    # 查询task信息
    task_id = step_info.content.get("task_id")
    # 替换给到的变量信息
    raw_params = step_info.content.get("params")
    params = replace_values(raw_params, context.variables_mapping)
    # 构建局部上下文
    local_context = Context(task_id, context.plan_id, variables_mapping={0: params})
    # 查询task以及task下面的step
    query_set = Task.objects.get(id=task_id)
    pk_list = query_set.steps["step_list"]
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])
    step_queryset_list = Step.objects.filter(pk__in=pk_list).order_by(preserved)

    # 顺序依次执行每个步骤
    for step in step_queryset_list:
        step_function = step_type_func.get(str(step.type))
        step_function(step, local_context)
    # 查询执行结果。这里查询的是task的Result节点中的内容，如果task未配置Result节点，这里插入的就是空
    task_result = TaskResult.objects.get(
        plan_id=context.plan_id, task_id=task_id, step_id=step_queryset_list.last().id
    )
    # 执行结果添加到全局变量
    context.variables_mapping[step_info.id] = orjson.loads(task_result.content)
    # 执行结果记录到数据库
    TaskResult(
        plan_id=context.plan_id,
        task_id=context.task_id,
        step_id=step_info.id,
        content=task_result.content,
    ).save()


step_type_func = {
    StepTypeEnum.PARAMS.value: run_param_step,
    StepTypeEnum.HTTP.value: run_http_step,
    StepTypeEnum.SQL.value: run_sql_step,
    StepTypeEnum.REDIS.value: run_redis_step,
    StepTypeEnum.TASK.value: run_task_step,
    StepTypeEnum.RESULT.value: run_result_step,
}


def run_task(task_id: int, params: dict, plan_id: str):
    """
    执行任务的主函数
    @param task_id:任务ID
    @param params:初始参数
    @param plan_id:本次执行唯一ID
    @return:
    """
    task_status = TaskRunStatus(task_id=task_id, plan_id=plan_id)
    task_status.save()
    # 构建全局变量
    context = Context(task_id, plan_id, variables_mapping={0: params})
    # 查询task以及task下面的step
    query_set = Task.objects.get(id=task_id)
    pk_list = query_set.steps["step_list"]
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])
    step_queryset_list = Step.objects.filter(pk__in=pk_list).order_by(preserved)
    for step in step_queryset_list:
        step_function = step_type_func.get(str(step.type))
        step_function(step, context)
    task_status.status = True
    task_status.save()
