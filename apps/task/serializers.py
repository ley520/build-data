# coding=utf-8
# data：2023/1/5-20:13
from rest_framework import serializers

from .models import Task, Step, TaskResult, StepTypeEnum
from .scheme import (
    HttpContentScheme,
    SqlContentScheme,
    TaskContentScheme,
    RedisContentScheme,
)
from apps.BaseModel import SelfBaseSerializers


class TaskSerializer(SelfBaseSerializers):
    class Meta:
        model = Task
        fields = "__all__"
        exclude = []
        depth = 1


class TaskCreateSerializer(SelfBaseSerializers):
    class Meta:
        model = Task
        fields = ["name", "mark", "desc"]
        exclude = []
        depth = 1


class TaskUpdateSerializer(SelfBaseSerializers):
    class Meta:
        model = Task
        fields = ["name", "desc", "status"]
        exclude = []
        depth = 1


class StepSerializer(SelfBaseSerializers):
    class Meta:
        model = Step
        fields = "__all__"
        exclude = []
        depth = 1


class StepCreateSerializer(SelfBaseSerializers):
    class Meta:
        model = Step
        fields = ["name", "type", "content", "task_id"]
        exclude = []
        depth = 1

        def validate(self, attrs):
            step_type = attrs.get("type")
            step_content = attrs.get("content")

            if step_type not in StepTypeEnum.value:
                raise serializers.ValidationError("链接类型错误")

            if step_type == StepTypeEnum.HTTP.value:
                HttpContentScheme(**step_content)
            elif step_type == StepTypeEnum.SQL.value:
                SqlContentScheme(**step_content)
            elif step_type == StepTypeEnum.REDIS.value:
                RedisContentScheme(**step_content)
            elif step_type == StepTypeEnum.TASK.value:
                TaskContentScheme(**step_content)
            else:
                raise serializers.ValidationError("未定义的步骤类型，请联系开发者确认")

            return attrs


class StepUpdateSerializer(SelfBaseSerializers):
    class Meta:
        model = Step
        fields = ["name", "type", "content"]
        exclude = []
        depth = 1


class TaskResultSerializer(SelfBaseSerializers):
    class Meta:
        model = TaskResult
        fields = "__all__"
        exclude = []
        depth = 1
