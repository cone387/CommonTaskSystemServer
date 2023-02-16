from django import forms
from .choices import TaskScheduleType
from utils import cron_utils


class TaskScheduleForm(forms.ModelForm):

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
