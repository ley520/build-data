from django.contrib import admin
from apps.task.models import Task, Step, TaskResult


# Register your models here.
class TaskModelAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Task._meta.get_fields()]


class StepModelAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Step._meta.get_fields()]


class TaskResultModelAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TaskResult._meta.get_fields()]


admin.site.register(Task, TaskModelAdmin)
admin.site.register(Step, StepModelAdmin)
admin.site.register(TaskResult, TaskResultModelAdmin)
