# coding=utf-8
# data：2023/3/17-19:47

import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "buildDataBackend.settings.prod")

app = Celery("buildDataBackend")

#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
