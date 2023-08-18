import uuid

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView, GenericAPIView, ListCreateAPIView
from loguru import logger
from config.pagination import Pagination
from utils.permissionUtil import (
    add_permission_when_create,
    user_have_permission,
    remove_all_permission,
)
from .tasks import run_task_job
from .execute import run_http_step, run_task
from .models import Task, TaskResult, Step, task_permission_dict, TaskRunStatus
from .serializers import (
    TaskSerializer,
    TaskResultSerializer,
    StepSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    StepCreateSerializer,
    StepUpdateSerializer,
)
from .services import (
    create_task,
    delete_task,
    create_step,
    query_task,
    update_step,
    delete_step,
    query_task_result,
)


class TaskViewApi(GenericAPIView):
    serializer_class = TaskCreateSerializer
    queryset = Task.objects.all()
    pagination_class = Pagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["id", "name", "mark", "status", "user_id"]
    output_serializer = TaskSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().order_by("id"))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.output_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.output_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        result = create_task(request)
        result["can_edit"] = True
        return Response(result, status=status.HTTP_201_CREATED)


class TaskDetailViewApi(GenericAPIView):
    serializer_class = TaskUpdateSerializer
    queryset = Task.objects.all()
    pagination_class = Pagination
    output_serializer = TaskSerializer

    def get(self, request, pk):
        result = query_task(request, pk)
        return Response(result, status=status.HTTP_200_OK)

    def put(self, request):
        instance = self.get_object()
        user_have_permission(request, instance, task_permission_dict.get("change"))
        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        delete_task(pk)
        Response(status=status.HTTP_204_NO_CONTENT)


class StepViewAPI(GenericAPIView):
    queryset = Step.objects.filter().all()
    serializer_class = StepCreateSerializer
    pagination_class = Pagination

    def post(self, request, pre_step_id, *args, **kwargss):
        step_info = create_step(request, pre_step_id)
        return Response(step_info, status=status.HTTP_201_CREATED)


class StepDetailViewAPI(GenericAPIView):
    queryset = Step.objects.filter().all()
    serializer_class = StepUpdateSerializer
    pagination_class = Pagination
    lookup_url_kwarg = "step_id"
    query_serializer = StepSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.get_object()
        serializer = self.query_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        data = update_step(request, *args, **kwargs)
        return Response(data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        delete_step(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskResultView(ListAPIView, GenericAPIView):
    queryset = TaskResult.objects.filter().all()
    serializer_class = TaskResultSerializer
    pagination_class = Pagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["plan_id", "task_id"]


class TaskExecuteApi(GenericAPIView):
    class InputSerializer(serializers.Serializer):
        params = serializers.JSONField(allow_null=True)
        debug = serializers.BooleanField(default=False)

    serializer_class = InputSerializer

    def post(self, request, task_id):
        logger.info("开始执行")
        plan_id = str(uuid.uuid1())
        run_task(
            **{
                "task_id": task_id,
                "params": request.data.get("params"),
                "plan_id": plan_id,
            }
        )
        # run_task_job.apply_async()
        # run_task_job.delay(
        #     **{
        #         "task_id": task_id,
        #         "params": request.data.get("params"),
        #         "plan_id": plan_id,
        #     }
        # )
        logger.info("执行结束")
        return Response({"planId": plan_id}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_task_result(request, task_id, plan_id):
    return Response(query_task_result(task_id, plan_id), status=status.HTTP_200_OK)