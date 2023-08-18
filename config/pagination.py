# coding=utf-8
# data：2023/1/6-15:46
from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    """自定义分页"""

    page_size = 10
    page_size_query_param = "size"
    max_page_size = 100
