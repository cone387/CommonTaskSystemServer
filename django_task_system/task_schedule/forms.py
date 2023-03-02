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


class TaskScheduleForm(forms.ModelForm):
    crontab = forms.CharField(required=False, label="Crontab表达式", help_text="crontab表达式，如：* * * * *")
    period = forms.IntegerField(initial=60, label="周期", help_text="间隔时间，单位：秒",
                                widget=widgets.AdminIntegerFieldWidget)
    timings_type = forms.ChoiceField(required=False, label="指定时间", choices=ScheduleTimingType.choices)
    date_range_start = NullableSplitDateTimeField(required=False, require_all_fields=False, label="时间范围",
                                                  help_text="开始时间", widget=widgets.AdminSplitDateTime)
    date_range_end = NullableSplitDateTimeField(required=False, require_all_fields=False, label="",
                                                help_text="结束时间", widget=widgets.AdminSplitDateTime)
    weekdays = forms.MultipleChoiceField(
        required=False,
        label="星期",
        choices=[
            (1, "星期一"),
            (2, "星期二"),
            (3, "星期三"),
            (4, "星期四"),
            (5, "星期五"),
            (6, "星期六"),
            (7, "星期日"),
        ],
        widget=forms.CheckboxSelectMultiple()
    )

    timings_period = forms.IntegerField(required=False, initial=1, label='频率', widget=PeriodWidget)
    timing_time = forms.TimeField(required=False, initial='00:00', label="时间", widget=widgets.AdminTimeWidget)
    config = forms.JSONField(required=False, initial={}, label="配置", widget=JSONWidget(
        attrs={'readonly': 'readonly'}
    ))

    def __init__(self, *args, **kwargs):
        super(TaskScheduleForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            config = self.instance.config
            schedule_type = config.get('type')
            self.initial['type'] = schedule_type
            type_config = config[schedule_type]
            if schedule_type == TaskScheduleType.CRONTAB:
                self.initial['crontab'] = type_config['crontab']
            elif schedule_type == TaskScheduleType.TIMINGS:
                timings_type = type_config.get('type')
                self.initial['timings_type'] = timings_type
                self.initial['timing_time'] = type_config['time']
                if timings_type == ScheduleTimingType.WEEKDAYS:
                    self.initial['weekdays'] = type_config.get(timings_type).get('weekdays')
                self.initial['timings_period'] = type_config.get(timings_type).get('period', 1)
            st, et = config.get('datetime_range', (None, None))
            self.fields['date_range_start'].initial = datetime.strptime(st, '%Y-%m-%d %H:%M:%S') if st else None
            self.fields['date_range_end'].initial = datetime.strptime(et, '%Y-%m-%d %H:%M:%S') if et else None

    def clean(self):
        cleaned_data = super(TaskScheduleForm, self).clean()
        schedule_type = cleaned_data.get('type')
        crontab = cleaned_data.pop('crontab')
        period = cleaned_data.pop('period')
        date_range_start = cleaned_data.pop('date_range_start')
        date_range_end = cleaned_data.pop('date_range_end')
        timings_type = cleaned_data.pop('timings_type')
        weekdays = cleaned_data.pop('weekdays')
        timings_period = cleaned_data.pop('timings_period')
        timing_time = cleaned_data.pop('timing_time')
        config = cleaned_data['config'] = {
            'type': schedule_type,
            'datetime_range': [
                date_range_start.strftime('%Y-%m-%d %H:%M:%S') if date_range_start else None,
                date_range_end.strftime('%Y-%m-%d %H:%M:%S') if date_range_end else None
            ]
        }
        type_config: dict = config.setdefault(schedule_type, {})
        if schedule_type == TaskScheduleType.CRONTAB:
            if not crontab:
                raise forms.ValidationError('crontab is required while type is crontab')
            type_config['crontab'] = crontab
            cleaned_data['next_schedule_time'] = cron_utils.get_next_cron_time(crontab)
        elif schedule_type == TaskScheduleType.CONTINUOUS:
            if period == 0:
                raise forms.ValidationError("period can't be 0 while type is continuous")
            type_config['period'] = period
        elif schedule_type == TaskScheduleType.TIMINGS:
            type_config['time'] = timing_time.strftime('%H:%M:%S')
            type_config['type'] = timings_type
            if timings_type == ScheduleTimingType.DAYS:
                if timings_period == 0:
                    raise forms.ValidationError("period can't be 0 while type is timings")
                type_config.setdefault(timings_type, {}).setdefault('period', timings_period)
            elif timings_type == ScheduleTimingType.WEEKDAYS:
                if not weekdays:
                    raise forms.ValidationError("weekdays is required while type is timings")
                type_config.setdefault(timings_type, {}).setdefault('period', timings_period)
                type_config.setdefault(timings_type, {}).setdefault('weekdays', weekdays)
            elif timings_type == ScheduleTimingType.MONTHDAYS:
                type_config.setdefault(timings_type, {}).setdefault('period', timings_period)
            elif timings_type == ScheduleTimingType.DATETIMES:
                if not date_range_start or not date_range_end:
                    raise forms.ValidationError("date_range_start and date_range_end is required while type is timings")
                type_config.setdefault(timings_type, {}).setdefault('start', date_range_start)
                type_config.setdefault(timings_type, {}).setdefault('end', date_range_end)
            else:
                raise forms.ValidationError("timings_type is invalid")
        else:
            raise forms.ValidationError("type<%s> is invalid" % schedule_type)
        return cleaned_data

    class Meta:
        model = models.TaskSchedule
        fields = "__all__"
