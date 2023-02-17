from django.contrib import admin
from django.contrib.auth import get_user_model
from . import models
from . import forms

UserModel = get_user_model()


class UserAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs['initial'] = request.user.id
            kwargs["queryset"] = UserModel.objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_form(self, request, form, change):
        if not change:
            form.instance.user = request.user
        return super().save_form(request, form, change)


class FieldConfigAdmin(UserAdmin):
    form = forms.FieldConfigForm

    list_display = ('id', 'model', 'key', 'value', 'type', 'is_required', 'update_time')
    fields = (
        "model",
        "type",
        ("key", "is_required",),
        "value"
    )


class CategoryAdmin(UserAdmin):
    form = forms.CategoryForm
    list_display = ('id', 'model', 'parent', 'name', 'user', 'update_time')
    fields = (
        ("model", "parent"),
        "name",
        "config"
    )


class TagAdmin(UserAdmin):
    form = forms.TagForm
    list_display = ('id', 'model', 'name', 'user', 'update_time')
    fields = (
        "model",
        "name",
        "config"
    )


admin.site.register(models.CommonFieldConfig, FieldConfigAdmin)
admin.site.register(models.CommonCategory, CategoryAdmin)
admin.site.register(models.CommonTag, TagAdmin)
