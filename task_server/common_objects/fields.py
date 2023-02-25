import json
from django.db import models
from . import validator


class CharField(models.Field):

    def __init__(self, **kwargs):
        kwargs['max_length'] = kwargs.pop('max_length', 1)
        super().__init__(**kwargs)

    def db_type(self, connection):
        return 'CHAR(%s)' % self.max_length



class ConfigField(models.JSONField):
    _default_json_encoder = json.JSONEncoder(allow_nan=False, indent=4)

    # def clean(self, value, model_instance):
    #     value = super().clean(value, model_instance)
    #     queryset = CommonFieldConfig.objects.filter(model=model_instance.__class__._meta.label)
    #     model_fields = {field.key: field for field in queryset}
    #     for k, v in value.items():
    #         model_filed = model_fields.get(k)
    #         validator.is_not_empty(model_filed, f'字段{k}不存在')
    #         validator.is_false(model_filed.is_required and not v, f'字段{k}不能为空')
    #         if model_filed.type == CommonFieldConfigType.INT:
    #             validator.is_int(f'字段{k}必须为整数')
    #         elif model_filed.type == CommonFieldConfigType.FLOAT:
    #             validator.is_float(f'字段{k}必须为浮点数')
    #         elif model_filed.type == CommonFieldConfigType.LIST:
    #             validator.is_list(f'字段{k}必须为列表')
    #         elif model_filed.type == CommonFieldConfigType.DICT:
    #             validator.is_dict(f'字段{k}必须为字典')
    #     return value
