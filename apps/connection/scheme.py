# coding=utf-8
# data：2023/3/9-11:33

from pydantic import BaseModel
from typing import Optional


class SqlBaseScheme(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str
    charset: str = "utf8"


class MysqlScheme(SqlBaseScheme):
    port: int = 3306


class RedisScheme(BaseModel):
    host: str
    port: int
    db: int = 0
    username: Optional[str]
    password: Optional[str]
    socket_timeout: int = 3
