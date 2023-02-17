import json
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from utils import foreign_key
from .choices import CommonFieldConfigType
from . import validator


UserModel = get_user_model()


class ConfigField(models.JSONField):
    _default_json_encoder = json.JSONEncoder(allow_nan=False, indent=4)

    def clean(self, value, model_instance):
        value = super().clean(value, model_instance)
        queryset = CommonFieldConfig.objects.filter(model=model_instance.__class__.__name__)
        model_fields = {field.key: field for field in queryset}
        for k, v in value.items():
            model_filed = model_fields.get(k)
            validator.is_not_empty(model_filed, f'字段{k}不存在')
            validator.is_false(model_filed.is_required and not v, f'字段{k}不能为空')
            if model_filed.type == CommonFieldConfigType.INT:
                validator.is_int(f'字段{k}必须为整数')
            elif model_filed.type == CommonFieldConfigType.FLOAT:
                validator.is_float(f'字段{k}必须为浮点数')
            elif model_filed.type == CommonFieldConfigType.LIST:
                validator.is_list(f'字段{k}必须为列表')
            elif model_filed.type == CommonFieldConfigType.DICT:
                validator.is_dict(f'字段{k}必须为字典')
        return value


@deconstructible
class get_default_config:

    def __init__(self, model):
        self.model = model

    def __call__(self):
        fields = CommonFieldConfig.objects.filter(model=self.model).values_list('key', 'value')
        return {k: v for k, v in fields}


class CommonFieldConfig(models.Model):
    id = models.AutoField(primary_key=True)
    model = models.CharField(max_length=30, verbose_name='所属模型')
    key = models.CharField(max_length=20, verbose_name='字段')
    value = models.CharField(max_length=200, null=True, blank=True, verbose_name='值')
    type = models.CharField(max_length=10, default=CommonFieldConfigType.STR, verbose_name='类型',
                            choices=CommonFieldConfigType.choices)
    is_required = models.BooleanField(default=False, verbose_name='是否必填')
    create_time = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'common_field_config'
        verbose_name_plural = verbose_name = '字段配置'

    def __str__(self):
        return self.key

    __repr__ = __str__


class CommonCategory(models.Model):
    id = models.AutoField(primary_key=True)
    model = models.CharField(max_length=30, verbose_name='所属模型')
    parent = models.ForeignKey('self', blank=True, null=True, db_constraint=False, on_delete=models.CASCADE,
                               related_name='children', verbose_name='父类别')
    name = models.CharField(max_length=50, verbose_name='名称')
    config = ConfigField(default=get_default_config('CommonCategory'), blank=True, null=True, verbose_name='详细')
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, db_constraint=False, verbose_name='用户')
    create_time = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    @property
    def associated_categories_ids(self):
        return foreign_key.get_related_object_ids(self)

    class Meta:
        db_table = 'common_category'
        verbose_name = verbose_name_plural = '任务类别'
        unique_together = ('user', 'name', 'parent')

    def __str__(self):
        return self.name

    __repr__ = __str__


class CommonTag(models.Model):
    id = models.AutoField(primary_key=True)
    model = models.CharField(max_length=30, verbose_name='所属模型')
    name = models.CharField(max_length=50, verbose_name='标签名')
    config = ConfigField(default=get_default_config('CommonTag'), blank=True, null=True, verbose_name='详细')
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, db_constraint=False, verbose_name='用户')
    create_time = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'common_tag'
        verbose_name = verbose_name_plural = '任务标签'
        unique_together = ('user', 'name')

    def __str__(self):
        return self.name

    __repr__ = __str__
