# coding=utf-8
# data：2023/3/14-22:58
from pydantic import BaseModel
from typing import Optional, Union
import inspect


class HttpContentScheme(BaseModel):
    """
    requests库中的requests.request()方法，只有method和url必传。
    只校验必传参数，其他选填参数不校验，直接入库
    """

    method: str
    url: str


class SqlContentScheme(BaseModel):
    connect_id: int
    sql: str
    database: str


class RedisContentScheme(BaseModel):
    connect_id: int
    action: str
    key: Union[str, int, None]
    value: Optional[dict]


class TaskContentScheme(BaseModel):
    task_id: int
    params: Optional[dict]
