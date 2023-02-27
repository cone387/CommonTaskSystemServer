from django.contrib.admin.apps import AdminConfig


class CommonTaskAdminConfig(AdminConfig):
    default_site = 'task_server.admin.CommonTaskAdminSite'

