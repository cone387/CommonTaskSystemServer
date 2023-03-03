import json

from django import forms
from django.contrib.admin import widgets
from .choices import TaskScheduleType, ScheduleTimingType
from common_objects.widgets import JSONWidget, JSJsonWidget
from utils import cron_utils, foreign_key
from datetime import datetime
from . import models


class TaskForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        task: models.Task = self.instance
        if task.id:
            self.fields['parent'].queryset = models.Task.objects.filter(
                user=task.user
            ).exclude(id__in=foreign_key.get_related_object_ids(task))


class DateTimeRangeWidget(forms.widgets.MultiWidget):
    template_name = 'task_schedule/datetime_range.html'

    def __init__(self, attrs=None):
        st = widgets.AdminSplitDateTime()
        et = widgets.AdminSplitDateTime()
        super().__init__([st, et], attrs=attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["start_datetime"] = "开始时间:"
        context["end_datetime"] = "结束时间:"
        return context

    def decompress(self, value):
        if value:
            return value
        return [None, None]


class PeriodWidget(widgets.AdminIntegerFieldWidget):
    template_name = 'task_schedule/period.html'

    def __init__(self, unit=ScheduleTimingType.DAYS.value, attrs=None):
        self.unit = unit
        super().__init__(attrs=attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["unit"] = self.unit
        return context


class NullableSplitDateTimeField(forms.SplitDateTimeField):

    def clean(self, value):
        if value[0] and not value[1]:
            value[1] = '00:00:00'
        elif not value[0] and value[1]:
            value[0] = datetime.now().strftime('%Y-%m-%d')
        return super(NullableSplitDateTimeField, self).clean(value)


class MultiWeekdayChoiceFiled(forms.MultipleChoiceField):
    _choices = [
                  (1, "星期一"),
                  (2, "星期二"),
                  (3, "星期三"),
                  (4, "星期四"),
                  (5, "星期五"),
                  (6, "星期六"),
                  (7, "星期日"),
              ]
    widget = forms.CheckboxSelectMultiple

    def __init__(self, *, choices=(), label="星期", widget=None, **kwargs):
        super(MultiWeekdayChoiceFiled, self).__init__(
            choices=choices or self._choices,
            label=label,
            widget=widget or self.widget,
            **kwargs)
        
    def to_python(self, value):
        if not value:
            return []
        elif not isinstance(value, (list, tuple)):
            raise forms.ValidationError(
                self.error_messages["invalid_list"], code="invalid_list"
            )
        return [int(val) for val in value]


class PeriodScheduleWidget(forms.MultiWidget):

    template_name = 'task_schedule/period_schedule.html'

    def __init__(self, default_time=datetime.now, default_period=60, attrs=None):
        ws = (
            widgets.AdminSplitDateTime(),
            widgets.AdminIntegerFieldWidget()
        )
        self.default_time = default_time() if callable(default_time) else default_time
        self.default_period = default_period
        super().__init__(ws)

    def decompress(self, value):
        if value:
            return value
        return [self.default_time, self.default_period]


class PeriodScheduleFiled(forms.MultiValueField):

    widget = PeriodScheduleWidget

    def __init__(self, label="持续计划", **kwargs):
        fs = (
            forms.SplitDateTimeField(help_text="下次开始时间"),
            forms.IntegerField(help_text="周期/每(秒)")
        )
        super(PeriodScheduleFiled, self).__init__(fs, label=label, **kwargs)

    def to_python(self, value):
        if not value:
            return []
        elif not isinstance(value, (list, tuple)):
            raise forms.ValidationError(
                self.error_messages["invalid_list"], code="invalid_list"
            )
        return [int(val) for val in value]

    def decompress(self, value):
        if value:
            return value
        return [None, 60]

    def compress(self, data_list):
        return data_list


class DatetimeJsonEncoder(json.JSONEncoder):

    def encode(self, o) -> str:
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        return super(DatetimeJsonEncoder, self).encode(o)


class TaskScheduleForm(forms.ModelForm):
    crontab = forms.CharField(required=False, label="Crontab表达式", help_text="crontab表达式，如：* * * * *")
    period_schedule = PeriodScheduleFiled()
    once_schedule = forms.SplitDateTimeField(required=False, label="开始时间", widget=widgets.AdminSplitDateTime)
    timing_type = forms.ChoiceField(required=False, label="指定时间", choices=ScheduleTimingType.choices)
    timing_weekdays = MultiWeekdayChoiceFiled(required=False)
    timing_period = forms.IntegerField(required=False, min_value=1, initial=1, label='频率', widget=PeriodWidget)
    timing_time = forms.TimeField(required=False, initial='00:00', label="时间", widget=widgets.AdminTimeWidget)
    config = forms.JSONField(required=False, initial={}, label="配置",
                             encoder=DatetimeJsonEncoder,
                             widget=JSONWidget(attrs={'readonly': 'readonly'})
                             )

    def __init__(self, *args, **kwargs):
        super(TaskScheduleForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            config = self.instance.config
            schedule_type = config.get('schedule_type')
            self.initial['schedule_type'] = schedule_type
            type_config = config[schedule_type]
            if schedule_type == TaskScheduleType.CRONTAB:
                self.initial['crontab'] = type_config['crontab']
            elif schedule_type == TaskScheduleType.TIMINGS:
                timing_type = type_config.get('type')
                self.initial['timing_type'] = timing_type
                self.initial['timing_time'] = type_config['time']
                if timing_type == ScheduleTimingType.WEEKDAYS:
                    self.initial['weekdays'] = type_config.get(timing_type).get('weekdays')
                self.initial['timing_period'] = type_config.get(timing_type).get('period', 1)

    def clean(self):
        cleaned_data = super(TaskScheduleForm, self).clean()
        schedule = models.ScheduleConfig(**cleaned_data)
        cleaned_data['config'] = schedule.to_config()
        cleaned_data['next_schedule_time'] = schedule.get_current_time()
        return cleaned_data

    class Meta:
        model = models.TaskSchedule
        fields = "__all__"
