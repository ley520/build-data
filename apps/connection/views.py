from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

# from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import GenericAPIView, ListCreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response

from .models import Connection, connection_permission_dict
from .serializers import ConnectionSerializer, ConnectionUpdateSerializer
from utils.permissionUtil import (
    add_permission_when_create,
    user_have_permission,
    remove_all_permission,
)
from config.pagination import Pagination


# class ConnectionView(ModelViewSet):
#     queryset = Connection.objects.filter().all()
#     serializer_class = ConnectionSerializer
#     pagination_class = Pagination
#     authentication_classes = [SessionAuthentication, BasicAuthentication]
#     permission_classes = [IsAuthenticated]


class ConnectionViewApi(ListCreateAPIView):
    serializer_class = ConnectionSerializer
    queryset = Connection.objects.all()
    pagination_class = Pagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["id", "name"]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        add_permission_when_create(request, "connection", "connection", instance)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class ConnectionViewDetailApi(GenericAPIView):
    serializer_class = ConnectionSerializer
    queryset = Connection.objects.all()
    pagination_class = Pagination

    def get(self, request, *args, **kwargs):
        queryset = self.get_object()
        serializer = ConnectionSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        if not user_have_permission(
            request, instance, connection_permission_dict.get("change")
        ):
            raise PermissionDenied
        serializer = ConnectionUpdateSerializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if not user_have_permission(
            request, instance, connection_permission_dict.get("delete")
        ):
            raise PermissionDenied
        remove_all_permission(instance, connection_permission_dict)
        instance.delete()
        Response(status=status.HTTP_204_NO_CONTENT)
