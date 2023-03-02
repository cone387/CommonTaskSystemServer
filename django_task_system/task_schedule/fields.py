from django.db import models
import json


class ScheduleConfigField(models.JSONField):
    _default_json_encoder = json.JSONEncoder(allow_nan=False, indent=4)

    def prepare_value(self, value):
        if value is None:
            return value
        return json.dumps(value, ensure_ascii=False, indent=4)

