from django.db import models
from .models import ConfigField, get_default_config


class CharField(models.Field):

    def __init__(self, **kwargs):
        kwargs['max_length'] = kwargs.pop('max_length', 1)
        super().__init__(**kwargs)

    def db_type(self, connection):
        return 'CHAR(%s)' % self.max_length
