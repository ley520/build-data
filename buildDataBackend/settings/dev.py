# coding=utf-8
# data：2023/2/27-11:00

from .base import *

DEBUG = True
# BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(os.path.join(__file__, os.pardir)))
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "build-data",
        "USER": "root",
        "PASSWORD": "123456",
        "HOST": "127.0.0.1",
        "PORT": "33006",
    }
}
test = {
    "poiId": "",
    "merchantId": "",
    "channel": "",
    "outId": "",
    "details": [{"code": "", "quantity": ""}],
    "environment": {"uuid": "", "ip": "", "latitude": "", "longitude": "", "ua": ""},
}
