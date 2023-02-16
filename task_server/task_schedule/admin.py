from django.contrib import admin
from common_objects.admin import UserAdmin
from . import models, forms


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
    list_display = ('id', 'name', 'status', 'user', 'update_time')
    fields = (
        ("name", "status",),
        'description',
        "config",
    )


class TaskScheduleAdmin(UserAdmin):
    list_display = ('id', 'task', 'type', 'crontab', 'next_schedule_time', 'period', 'status', 'user', 'update_time')
    fields = (
        ("task", "status"),
        ("type", 'priority'),
        'crontab',
        ("next_schedule_time", 'period'),
        'callback'
    )
    form = forms.TaskScheduleForm

    class Media:
        js = (
            'https://cdn.bootcss.com/jquery/3.3.1/jquery.min.js',
            'https://cdn.bootcss.com/popper.js/1.14.3/umd/popper.min.js',
            'https://cdn.bootcss.com/bootstrap/4.1.3/js/bootstrap.min.js',
            # reverse('admin:jsi18n'),
            'task_schedule/js/task_schedule_admin.js',
        )


class TaskScheduleLogAdmin(UserAdmin):
    list_display = ('id', 'schedule', 'schedule_time', 'finish_time')

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]


admin.site.register(models.Task, TaskAdmin)
admin.site.register(models.TaskSchedule, TaskScheduleAdmin)
admin.site.register(models.TaskCallback, TaskCallbackAdmin)
admin.site.register(models.TaskScheduleLog, TaskScheduleLogAdmin)
