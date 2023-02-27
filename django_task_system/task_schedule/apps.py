from django.apps import AppConfig


class TaskScheduleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_task_system.task_schedule'
    verbose_name = '任务计划'
