
from django.contrib import admin


apps_order_list = ['common_objects', 'task_schedule', 'auth']
apps_order_dict = {app: index for index, app in enumerate(apps_order_list)}


# 自定义网站APP显示顺序
class CommonTaskAdminSite(admin.AdminSite):

    site_title = '任务管理'
    site_header = '任务管理'
    site_id = 1
    default_site = 'task_server.admin.CommonTaskAdminSite'

    def index(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}

        app_list = self.get_app_list(request)
        # app_dict = self._build_app_dict(request)
        # https://stackoverflow.com/questions/15650348/sorting-a-list-of-dictionaries-based-on-the-order-of-values-of-another-list
        # https://docs.python.org/3/howto/sorting.html
        # https://lvii.github.io/code/2018-11-21-sort-django-admin-index-dashboard-app-list-by-an-ordered-list/
        app_list.sort(key=lambda element_dict: apps_order_dict[element_dict["app_label"]])

        extra_context['app_list'] = app_list
        return super(CommonTaskAdminSite, self).index(request, extra_context)

