# coding=utf-8
# data：2023/2/13-09:08

from django.conf import settings
from loguru import logger
import sys

# 去除默认控制台输出
logger.remove()
# 输出日志格式
logger_format = "{time:YYYY-MM-DD HH:mm:ss,SSS} [{process}] {level} {file} {module} {function} {line} - {message}"

# 控制台输出
logger.add(sys.stderr)

config_map = {
    # "format": logger_format,
    "rotation": "00:00",
    "encoding": "utf-8",
    "enqueue": True,
    "retention": "30 days",
    "serialize": False,
    "compression": "zip",
}


def only_level(level):
    def is_level(record):
        return record["level"].name == level

    return is_level


logger.add(
    str(settings.BASE_DIR) + "/log/info.{time:YYYY-MM-DD}.log",
    level="INFO",
    filter=only_level("INFO"),
    **config_map
)
logger.add(
    str(settings.BASE_DIR) + "/log/error.{time:YYYY-MM-DD}.log",
    level="ERROR",
    **config_map
)

logger.add(
    str(settings.BASE_DIR) + "/log/debug.{time:YYYY-MM-DD}.log",
    level="DEBUG",
    **config_map
)
