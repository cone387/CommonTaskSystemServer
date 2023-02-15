from django import forms
from .choices import SystemModelChoices


class FieldConfigForm(forms.ModelForm):
    model = forms.ChoiceField(choices=SystemModelChoices.choices, label="所属模型", required=True)


class CategoryForm(forms.ModelForm):
    model = forms.ChoiceField(choices=SystemModelChoices.choices, label="所属模型", required=True)


class TagForm(forms.ModelForm):
    model = forms.ChoiceField(choices=SystemModelChoices.choices, label="所属模型", required=True)
