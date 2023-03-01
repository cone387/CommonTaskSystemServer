from django.db.models import TextChoices


class TaskStatus(TextChoices):
    ENABLE = 'E', '启用'
    DISABLE = 'D', '禁用'


class TaskScheduleStatus(TextChoices):
    OPENING = 'O', '开启'
    CLOSED = 'C', '关闭'
    DONE = 'D', '已完成'
    TEST = 'T', '测试'


class TaskScheduleType(TextChoices):
    CRONTAB = 'C', 'Crontab'
    ONCE = 'O', '一次性'
    CONTINUOUS = 'S', '连续性'
    TIMINGS = 'T', '特定时间'


class ScheduleTimingType(TextChoices):
    DAYS = 'DAYS', '按天'
    WEEKDAYS = 'WEEKDAYS', '按周'
    MONTHDAYS = 'MONTHDAYS', '按月'
    HOURS = 'HOURS', '按小时'


class TaskCallbackStatus(TextChoices):
    ENABLE = 'E', '启用'
    DISABLE = 'D', '禁用'


class TaskCallbackEvent(TextChoices):
    SUCCEED = 'S', '成功'
    FAILED = 'F', '失败'
    DONE = 'D', '完成'
