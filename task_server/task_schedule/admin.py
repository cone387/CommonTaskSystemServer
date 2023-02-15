from django.contrib import admin
from common_objects.admin import UserAdmin
from . import models


class TaskAdmin(UserAdmin):
    list_display = ('id', 'parent', 'name', 'category', 'status', 'user', 'update_time')
    fields = (
        ("parent", 'category',),
        ("name", "status",),
        "config",
        "tags",
        'description',

    )
    filter_horizontal = ('tags',)


class TaskCallbackAdmin(UserAdmin):
    pass


class TaskScheduleAdmin(UserAdmin):
    list_display = ('id', 'task', 'type', 'crontab', 'next_schedule_time', 'period', 'status', 'user', 'update_time')
    fields = (
        "task",
        ("type", 'priority', "status"),
        'crontab',
        ("next_schedule_time", 'period'),
        'callback'
    )


class TaskScheduleLogAdmin(UserAdmin):
    # list_display = ('id', 'status', 'create_time')
    fields = (
        "status",
    )


admin.site.register(models.Task, TaskAdmin)
admin.site.register(models.TaskSchedule, TaskScheduleAdmin)
admin.site.register(models.TaskCallback, TaskCallbackAdmin)
admin.site.register(models.TaskScheduleLog, TaskScheduleLogAdmin)
