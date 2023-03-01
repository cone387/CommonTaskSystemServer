from django.db import models
from .choices import TaskScheduleType
import json
from django.forms import ValidationError


class ScheduleConfigField(models.JSONField):
    _default_json_encoder = json.JSONEncoder(allow_nan=False, indent=4)

    def clean(self, value, model_instance: 'TaskSchedule'):
        value = super(ScheduleConfigField, self).clean(value, model_instance)
        t = model_instance.type
        config = value.setdefault(t, {})
        if t == TaskScheduleType.CRONTAB:
            if not config.get('crontab'):
                raise ValidationError('crontab is required when type is crontab')
        elif t == TaskScheduleType.CONTINUOUS:
            if not config.get('period'):
                raise ValidationError('period is required when type is continuous')
        elif t == TaskScheduleType.ONCE:
            config.setdefault('timing', model_instance.next_schedule_time.strftime('%Y-%m-%d %H:%M:%S'))
        return value
