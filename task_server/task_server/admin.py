
from django.contrib import admin
from collections import OrderedDict


apps_order_list = ['common_objects', 'task_schedule', 'auth']
apps_order_dict = {app: index for index, app in enumerate(apps_order_list)}


# 自定义网站APP显示顺序
class CommonTaskAdminSite(admin.AdminSite):

    site_title = '任务管理'
    site_header = '任务管理'

    def __init__(self, *args, **kwargs):
        super(CommonTaskAdminSite, self).__init__(*args, **kwargs)
        self._registry = OrderedDict()

    def get_app_list(self, request, app_label=None):
        app_dict = self._build_app_dict(request, app_label)
        app_list = sorted(app_dict.values(), key=lambda x: apps_order_dict[x["app_label"]])
        # Sort the models alphabetically within each app.
        # for app in app_list:
        #     app["models"].sort(key=lambda x: x["name"])
        return app_list
