from django.db.models import TextChoices
from django.contrib import admin
from django.db.models import ForeignKey, ManyToManyField

_SYS_MODELS = ['User', 'Group']
_MODULE_CHOICES = None


class CommonFieldConfigType(TextChoices):
    FIXED = 'fixed', '固定值'
    INT = 'int', '整数'
    FLOAT = 'float', '浮点数'
    STR = 'string', '字符串'
    LIST = 'list', '列表'
    DICT = 'dict', '字典'


class _SysModelChoicesMeta(type):
    _choices = None
    name = None
    field = None

    def _get_choices(cls):
        if not cls._choices:
            choices = []
            for x in cls.related_models:
                for field in x._meta.get_fields():
                    if field.__class__ == cls.field and field.related_model.__name__ == cls.name:
                        choices.append(("%s.%s" % (x._meta.app_label, x.__name__), x._meta.verbose_name))
                        break
            cls._choices = choices
        return cls._choices

    @property
    def related_models(cls):
        models = []
        for x in admin.site._registry:
            for field in x._meta.get_fields():
                if field.__class__ == cls.field and field.related_model.__name__ == cls.name:
                    models.append(x)
                    break
        return models

    @property
    def choices(cls):
        return cls._get_choices


class _SysConfigModelChoicesMeta(type):
    name = None
    _choices = None

    def _get_choices(cls):
        if not cls._choices:
            choices = []
            for x in cls.related_models:
                for field in x._meta.fields:
                    if field.__class__.__name__ == cls.name:
                        choices.append(("%s.%s" % (x._meta.app_label, x.__name__), x._meta.verbose_name))
                        break
            cls._choices = choices
        return cls._choices

    @property
    def related_models(cls):
        models = []
        for x in admin.site._registry:
            for field in x._meta.fields:
                if field.__class__.__name__ == cls.name:
                    models.append(x)
                    break
        return models

    @property
    def choices(cls):
        return cls._get_choices


class FieldConfigModelChoices(metaclass=_SysConfigModelChoicesMeta):
    name = 'ConfigField'


class CategoryModelChoices(metaclass=_SysModelChoicesMeta):
    name = 'CommonCategory'
    field = ForeignKey


class TagModelChoices(metaclass=_SysModelChoicesMeta):
    name = 'CommonTag'
    field = ManyToManyField

