from django.db import models
from ..BaseModel import BaseModel
from django.utils.translation import gettext_lazy as _


class ConnectTypeEnum(models.TextChoices):
    """
    连接类型：
    """

    mysql = 1, _("Mysql")
    # pgsql = 2, _('Postgresql')
    redis = 2, _("Redis")


class Connection(BaseModel):
    name = models.CharField(
        max_length=128, null=False, blank=False, unique=True, db_index=True
    )
    type = models.CharField(
        max_length=20, choices=ConnectTypeEnum.choices, null=False, blank=False
    )
    connect_param = models.JSONField(null=False, blank=False)
    user_id = models.IntegerField()

    class Meta:
        db_table = "connect"
        default_permissions = ("add", "change", "delete", "view")
        # permissions = ('add', 'change', 'delete', 'view')


connection_permission_dict = {
    "view": f"connection.view_{Connection.__name__.lower()}",
    "change": f"connection.change_{Connection.__name__.lower()}",
    "add": f"connection.add_{Connection.__name__.lower()}",
    "delete": f"connection.delete_{Connection.__name__.lower()}",
}
