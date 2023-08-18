from django.contrib import admin
from .models import Connection
from guardian.admin import GuardedModelAdmin


# Register your models here.
# class ConnectionAdmin(admin.ModelAdmin):
class ConnectionAdmin(GuardedModelAdmin):
    # list_display = ('id', 'name', 'type', 'create_time')
    list_display = [field.name for field in Connection._meta.get_fields()]


admin.site.register(Connection, ConnectionAdmin)
