from django.apps import AppConfig


class CommonObjectsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_task_system.common_objects'
    verbose_name = '通用对象'
