from django import forms
from django.contrib.admin.widgets import AdminSplitDateTime, AdminTimeWidget
from .choices import TaskScheduleType, ScheduleTimingType
from utils import cron_utils, foreign_key
from . import models


class TaskForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        task: models.Task = self.instance
        if task.id:
            self.fields['parent'].queryset = models.Task.objects.filter(
                user=task.user
            ).exclude(id__in=foreign_key.get_related_object_ids(task))


class WeekdaysWidget(forms.widgets.MultiWidget):

    def __init__(self):
        widgets = (
            forms.widgets.CheckboxSelectMultiple(choices=[
                (1, "星期一"),
                (2, "星期二"),
                (3, "星期三"),
                (4, "星期四"),
                (5, "星期五"),
                (6, "星期六"),
                (7, "星期日"),
            ]),
            AdminTimeWidget(),
        )
        super().__init__(widgets, attrs=None)

    def decompress(self, value):
        if value:
            return value
        return [None, None]


class TaskScheduleForm(forms.ModelForm):
    crontab = forms.CharField(required=False, label="Crontab表达式", help_text="crontab表达式，如：* * * * *")
    period = forms.IntegerField(initial=60, label="周期", help_text="间隔时间，单位：秒")
    timings = forms.ChoiceField(required=False, label="指定时间", choices=ScheduleTimingType.choices)
    date_range_start = forms.DateTimeField(required=False, label="时间范围", help_text="开始时间", widget=AdminSplitDateTime)
    date_range_end = forms.DateTimeField(required=False, label="", help_text="结束时间", widget=AdminSplitDateTime)

    weekdays = forms.MultiValueField(
        fields=[
            forms.MultipleChoiceField(),
            forms.DateTimeField(),
        ],
        widget=WeekdaysWidget,
    )
    # weekdays = forms.MultiValueField(
    #     fields=[forms.MultipleChoiceField(
    #         required=False,
    #         label="星期",
    #         choices=[
    #             (1, "星期一"),
    #             (2, "星期二"),
    #             (3, "星期三"),
    #             (4, "星期四"),
    #             (5, "星期五"),
    #             (6, "星期六"),
    #             (7, "星期日"),
    #         ],
    #         widget=forms.CheckboxSelectMultiple(attrs={'style': 'display: inline;'})),
    #         forms.DateTimeField(widget=AdminSplitDateTime, required=False, label=""),
    #                 ],
    #     required=False,
    #
    # )


    def clean(self):
        cleaned_data = super(TaskScheduleForm, self).clean()
        t = cleaned_data.get('type')
        if t == TaskScheduleType.CRONTAB:
            if not cleaned_data.get('crontab'):
                raise forms.ValidationError('crontab is required while type is crontab')
            cleaned_data['next_schedule_time'] = cron_utils.get_next_cron_time(cleaned_data['crontab'])
        elif t == TaskScheduleType.CONTINUOUS:
            if cleaned_data.get('period') == 0:
                raise forms.ValidationError("period can't be 0")
        else:
            cleaned_data['period'] = 0
        return cleaned_data

    class Meta:
        model = models.TaskSchedule
        fields = "__all__"
