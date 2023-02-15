from django.db.models import TextChoices
from django.contrib import admin

_SYS_MODELS = ['User', 'Group']
_MODULE_CHOICES = None


class CommonFieldConfigType(TextChoices):
    FIXED = 'fixed', '固定值'
    INT = 'int', '整数'
    FLOAT = 'float', '浮点数'
    STR = 'string', '字符串'
    LIST = 'list', '列表'
    DICT = 'dict', '字典'


class _SystemModelChoicesMeta(type):
    _choices = None

    def _get_choices(cls):
        if not cls._choices:
            cls._choices = {x.__name__: x._meta.verbose_name for x in admin.site._registry
                            if x.__name__ not in _SYS_MODELS and not x.__name__.startswith('Common')
                            }.items()
        return cls._choices

    @property
    def choices(cls):
        return cls._get_choices


class SystemModelChoices(metaclass=_SystemModelChoicesMeta):
    pass

