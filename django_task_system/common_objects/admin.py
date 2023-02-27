from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Count, ForeignKey
from django.utils.html import format_html
from . import models
from . import forms
from .choices import CategoryModelChoices, TagModelChoices

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

    list_display = ('id', 'admin_app', 'admin_model', 'key', 'value', 'type', 'is_required', 'update_time')
    fields = (
        "model",
        "type",
        ("key", "is_required",),
        "value"
    )

    def admin_app(self, obj):
        app, model = obj.model.split('.')
        return format_html('<a href="/admin/%s/">%s</a>' % (app, app))
    admin_app.short_description = '所属APP'

    def admin_model(self, obj):
        app, model = obj.model.split('.')
        return format_html('<a href="/admin/%s/%s/">%s</a>' % (app, model.lower(), model))
    admin_model.short_description = '所属模型'


class CategoryAdmin(UserAdmin):
    form = forms.CategoryForm
    list_display = ('id', 'admin_app', 'admin_model', 'parent', 'name', 'user', 'update_time')
    fields = (
        ("model", "parent"),
        "name",
        "config"
    )

    def __init__(self, *args, **kwargs):
        super(CategoryAdmin, self).__init__(*args, **kwargs)
        self.extra_context = {'models': {}}

    def admin_app(self, obj):
        app, model = obj.model.split('.')
        return format_html('<a href="/admin/%s/">%s</a>' % (app, app))
    admin_app.short_description = '所属APP'

    def admin_model(self, obj):
        app, model = obj.model.split('.')
        return format_html('<a href="/admin/%s/%s/?category__id__exact=%s">%s(%s)</a>' % (
            app, model.lower(), obj.id, model, self.extra_context['models'].get(obj.model, {}).get(obj.id, 0)))
    admin_model.short_description = '所属模型'

    def changelist_view(self, request, extra_context=None):
        queryset = models.CommonCategory.objects.values('model', 'id').annotate(Count('id'))
        models_categories = {}
        for o in queryset:
            models_categories.setdefault(o['model'], []).append(o['id'])
        for x in CategoryModelChoices.related_models:
            x: models.models.Model
            m = "%s.%s" % (x._meta.app_label, x.__name__)
            x_categories = models_categories.get(m, [])
            column = None
            for f in x._meta.get_fields():
                if f.__class__ == ForeignKey and f.related_model == models.CommonCategory:
                    column = f.name + '__id'
                    break
            params = {column + '__in': x_categories}
            if x_categories:
                model_queryset = x.objects.filter(**params).values(column).annotate(Count(column))
                self.extra_context['models'][m] = {x[column]: x[column + '__count'] for x in model_queryset}
        return super().changelist_view(request, extra_context=self.extra_context)


class TagAdmin(UserAdmin):
    form = forms.TagForm
    list_display = ('id', 'admin_app', 'admin_model', 'name', 'user', 'update_time')
    fields = (
        "model",
        "name",
        "config"
    )

    def __init__(self, *args, **kwargs):
        super(TagAdmin, self).__init__(*args, **kwargs)
        self.extra_context = {'models': {}}

    def admin_app(self, obj):
        app, model = obj.model.split('.')
        return format_html('<a href="/admin/%s/">%s</a>' % (app, app))
    admin_app.short_description = '所属APP'

    def admin_model(self, obj):
        app, model = obj.model.split('.')
        return format_html('<a href="/admin/%s/%s/?tags__id__exact=%s">%s(%s)</a>' % (
            app, model.lower(), obj.id, model, self.extra_context['models'].get(obj.model, {}).get(obj.id, 0)))
    admin_model.short_description = '所属模型'

    def changelist_view(self, request, extra_context=None):
        queryset = models.CommonTag.objects.values('model', 'id').annotate(Count('id'))
        models_tags = {}
        for o in queryset:
            models_tags.setdefault(o['model'], []).append(o['id'])
        for x in TagModelChoices.related_models:
            x: models.models.Model
            m = "%s.%s" % (x._meta.app_label, x.__name__)
            x_tags = models_tags.get(m, [])
            if x_tags:
                model_queryset = x.objects.filter(tags__id__in=x_tags
                                                  ).values('tags__id').annotate(Count('tags__id'))
                self.extra_context['models'][m] = {x['tags__id']: x['tags__id__count'] for x in model_queryset}
        return super().changelist_view(request, extra_context=self.extra_context)


admin.site.register(models.CommonFieldConfig, FieldConfigAdmin)
admin.site.register(models.CommonCategory, CategoryAdmin)
admin.site.register(models.CommonTag, TagAdmin)
