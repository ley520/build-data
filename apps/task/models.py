from django.db import models
from ..BaseModel import BaseModel
from django.utils.translation import gettext_lazy as _


class Task(BaseModel):
    name = models.CharField(
        verbose_name="名称",
        max_length=128,
        null=False,
        blank=False,
        unique=True,
        db_index=True,
    )
    mark = models.CharField(
        verbose_name="标识",
        max_length=128,
        null=False,
        blank=False,
        unique=True,
        db_index=True,
    )
    desc = models.TextField(null=True, blank=True)
    steps = models.JSONField(verbose_name="任务包含的步骤信息", null=True, blank=True)
    nums = models.IntegerField(verbose_name="执行次数", default=0)
    status = models.BooleanField(verbose_name="上下线状态", default=False)
    user_id = models.IntegerField(verbose_name="创建人ID")

    class Meta:
        db_table = "task"


task_permission_dict = {
    "view": f"task.view_{Task.__name__.lower()}",
    "change": f"task.change_{Task.__name__.lower()}",
    "add": f"task.add_{Task.__name__.lower()}",
    "delete": f"task.delete_{Task.__name__.lower()}",
}


class StepTypeEnum(models.TextChoices):
    """
    步骤类型：
    PARAMS = 参数步骤
    RESULT = 结果步骤
    HTTP：http网络请求
    SQL：数据库请求
    REDIS：redis操作
    TASK：嵌套的task任务
    TOOLS：系统提供的方法
    """

    PARAMS = 10, _("参数")
    RESULT = 20, _("结果")
    HTTP = 30, _("http请求")
    SQL = 40, _("SQL执行")
    REDIS = 50, _("redis操作")
    TASK = 60, _("工具引用")
    TOOLS = 70, _("自定义工具")


class Step(BaseModel):
    name = models.CharField(verbose_name="名称", max_length=128, null=False, blank=False)
    type = models.CharField(
        verbose_name="步骤类型",
        max_length=32,
        choices=StepTypeEnum.choices,
        null=False,
        blank=False,
    )
    content = models.JSONField(verbose_name="步骤内容", null=True, blank=True)
    task_id = models.IntegerField(
        verbose_name="taskId", null=False, blank=False, db_index=True
    )

    class Meta:
        db_table = "step"


step_permission_dict = {
    "view": f"task.view_{Step.__name__.lower()}",
    "change": f"task.change_{Step.__name__.lower()}",
    "add": f"task.add_{Step.__name__.lower()}",
    "delete": f"task.delete_{Step.__name__.lower()}",
}


class TaskRunStatus(BaseModel):
    plan_id = models.CharField(
        verbose_name="本次执行唯一id",
        max_length=128,
        null=False,
        blank=False,
    )
    task_id = models.IntegerField(verbose_name="taskId", null=False, blank=False)
    status = models.BooleanField(
        verbose_name="是否执行完成", default=False, null=False, blank=False
    )

    class Meta:
        db_table = "task_status"
        index_together = ["plan_id", "task_id"]


class TaskResult(BaseModel):
    plan_id = models.CharField(
        verbose_name="本次执行唯一id",
        max_length=128,
        null=False,
        blank=False,
    )
    content = models.TextField(verbose_name="执行结果", null=False, blank=True)
    task_id = models.IntegerField(verbose_name="taskId", null=False, blank=False)
    step_id = models.IntegerField(verbose_name="stepId", null=False, blank=False)
    step_type = models.CharField(
        verbose_name="步骤类型",
        max_length=32,
        choices=StepTypeEnum.choices,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = "task_result"
        index_together = ["plan_id", "task_id"]
