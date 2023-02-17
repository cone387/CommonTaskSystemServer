from django import forms
from .choices import SystemModelChoices
from .models import CommonCategory
from utils import foreign_key


class FieldConfigForm(forms.ModelForm):
    model = forms.ChoiceField(choices=SystemModelChoices.choices, label="所属模型", required=True)


class CategoryForm(forms.ModelForm):
    model = forms.ChoiceField(choices=SystemModelChoices.choices, label="所属模型", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance: CommonCategory = self.instance
        if instance.id:
            self.fields['parent'].queryset = CommonCategory.objects.filter(
                model=instance.model, user=instance.user
            ).exclude(id__in=foreign_key.get_related_object_ids(instance))

    class Meta:
        model = CommonCategory
        fields = "__all__"


class TagForm(forms.ModelForm):
    model = forms.ChoiceField(choices=SystemModelChoices.choices, label="所属模型", required=True)
