from .models import CommonTag, CommonCategory, CommonFieldConfig
from rest_framework import serializers


class CommonTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommonTag
        fields = ('name', 'config')


class CommonCategorySerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()

    def get_parent(self, obj):
        if obj.parent:
            return CommonCategorySerializer(obj.parent).data

    class Meta:
        model = CommonCategory
        fields = ('name', 'config', 'parent')


class CommonFieldConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommonFieldConfig
        fields = ('key', 'value')
