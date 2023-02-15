from django.core.exceptions import ValidationError


def is_not_empty(value, msg='不能为空'):
    if not value:
        raise ValidationError(msg)


def is_true(value, msg='必须为True'):
    if not value:
        raise ValidationError(msg)


def is_false(value, msg='必须为False'):
    if value:
        raise ValidationError(msg)


def is_int(value, msg='必须为整数'):
    try:
        int(value)
    except ValueError:
        raise ValidationError(msg)


def is_float(value, msg='必须为浮点数'):
    try:
        float(value)
    except ValueError:
        raise ValidationError(msg)


def is_list(value, msg='必须为列表'):
    if not isinstance(value, list):
        raise ValidationError(msg)


def is_dict(value, msg='必须为字典'):
    if not isinstance(value, dict):
        raise ValidationError(msg)
