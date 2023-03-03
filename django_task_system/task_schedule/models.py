from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import models
from .choices import TaskStatus, TaskScheduleStatus, TaskScheduleType, TaskCallbackStatus, \
    TaskCallbackEvent, ScheduleTimingType
from common_objects.models import CommonTag, CommonCategory, get_default_config
from common_objects import fields as common_fields
from utils.cron_utils import get_next_cron_time
from utils import foreign_key
from datetime import datetime, timedelta
from . import fields
from django.forms import ValidationError


__all__ = ['Task', 'TaskSchedule', 'TaskScheduleCallback', 'TaskScheduleLog']


UserModel = get_user_model()


class Task(models.Model):
    id = models.AutoField(primary_key=True)
    parent = models.ForeignKey('self', db_constraint=False, on_delete=models.DO_NOTHING,
                               null=True, blank=True, verbose_name='父任务')
    name = models.CharField(max_length=100, verbose_name='任务名')
    category = models.ForeignKey(CommonCategory, db_constraint=False, on_delete=models.DO_NOTHING, verbose_name='类别')
    tags = models.ManyToManyField(CommonTag, blank=True, db_constraint=False, verbose_name='标签')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    config = common_fields.ConfigField(default=get_default_config('Task'),
                                       blank=True, null=True, verbose_name='参数')
    status = common_fields.CharField(max_length=1, default=TaskStatus.ENABLE.value, verbose_name='状态',
                                     choices=TaskStatus.choices)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, db_constraint=False, verbose_name='用户')
    create_time = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    @property
    def associated_tasks_ids(self):
        return foreign_key.get_related_object_ids(self)

    class Meta:
        db_table = 'taskhub'
        verbose_name = verbose_name_plural = '任务中心'
        unique_together = ('name', 'user', 'parent')

    def __str__(self):
        return self.name

    __repr__ = __str__


class TaskScheduleCallback(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='回调')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    trigger_event = common_fields.CharField(default=TaskCallbackEvent.DONE, choices=TaskCallbackEvent.choices,
                                            verbose_name='触发事件')
    status = common_fields.CharField(default=TaskCallbackStatus.ENABLE.value, verbose_name='状态',
                                     choices=TaskCallbackStatus.choices)
    config = common_fields.ConfigField(default=get_default_config('TaskCallback'), blank=True, null=True,
                                       verbose_name='参数')
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, db_constraint=False, verbose_name='用户')
    create_time = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'task_schedule_callback'
        verbose_name = verbose_name_plural = '任务回调'
        unique_together = ('name', 'user')

    def __str__(self):
        return self.name

    __repr__ = __str__


class ScheduleConfig:

    def __init__(self, schedule_type=None, crontab=None,
                 period_schedule=None, timings_type=None,
                 timings_period=None, timings_time=None, weekdays=None, **kwargs):
        self.schedule_type = schedule_type
        self.period_schedule = period_schedule
        self.crontab = crontab
        self.timings_type = timings_type
        self.timings_period = timings_period
        self.timings_time = timings_time
        self.weekdays = weekdays
        self.kwargs = kwargs
        self._config = self.to_config()

    def from_config(self, config):
        self._config = config

    def to_config(self):
        config = {
            'schedule_type': self.schedule_type
        }
        schedule_type = self.schedule_type
        type_config: dict = config.setdefault(self.schedule_type, {})
        if schedule_type == TaskScheduleType.CRONTAB:
            if not self.crontab:
                raise ValidationError('crontab is required while type is crontab')
            type_config['crontab'] = self.crontab
        elif schedule_type == TaskScheduleType.CONTINUOUS:
            schedule_time, period = self.period_schedule
            if period == 0:
                raise ValidationError("period can't be 0 while type is continuous")
            type_config['period'] = period
            type_config['schedule_start_time'] = schedule_time
        elif schedule_type == TaskScheduleType.TIMINGS:
            timings_type = self.timings_type
            type_config['time'] = self.timings_time.strftime('%H:%M:%S')
            type_config['type'] = timings_type
            timings_config = type_config.setdefault(timings_type, {})
            if timings_type == ScheduleTimingType.DAYS:
                if self.timings_period == 0:
                    raise ValidationError("period can't be 0 while type is timings")
                timings_config.setdefault('period', self.timings_period)
            elif timings_type == ScheduleTimingType.WEEKDAYS:
                if not self.weekdays:
                    raise ValidationError("weekdays is required while type is timings")
                timings_config.setdefault('period', self.timings_period)
                timings_config.setdefault('weekdays', self.weekdays)
            elif timings_type == ScheduleTimingType.MONTHDAYS:
                timings_config.setdefault('period', self.timings_period)
            elif timings_type == ScheduleTimingType.DATETIMES:
                pass
            else:
                raise ValidationError("timings_type is invalid")
        else:
            raise ValidationError("type<%s> is invalid" % schedule_type)
        return config

    def get_current_time(self):
        now = timezone.now()
        schedule_type = self.schedule_type
        type_config = self._config[schedule_type]
        schedule_time = None
        if schedule_type == TaskScheduleType.CONTINUOUS.value:
            schedule_time, period = self.period_schedule
            while schedule_time < now:
                schedule_time += timedelta(seconds=period)
        elif schedule_type == TaskScheduleType.CRONTAB.value:
            schedule_time = get_next_cron_time(type_config['crontab'], now)
        elif schedule_type == TaskScheduleType.TIMINGS:
            timings_type = type_config['type']
            hour, minute, second = type_config['time'].split(':')
            hour, minute, second = int(hour), int(minute), int(second)
            if timings_type == ScheduleTimingType.DAYS:
                schedule_time = datetime(now.year, now.month, now.day, hour, minute, second)
                while schedule_time < now:
                    schedule_time += timedelta(days=type_config['period'])
            elif timings_type == ScheduleTimingType.WEEKDAYS:
                weekdays_config = type_config["WEEKDAYS"]
                weekdays = weekdays_config['weekdays']
                weekday = now.isoweekday()
                schedule_again = weekday not in weekdays
                if weekday in weekdays:
                    schedule_time = datetime(now.year, now.month, now.day, hour, minute, second)
                    if now > schedule_time:
                        schedule_again = True
                if schedule_again:
                    for i in weekdays:
                        if i > weekday:
                            days = i - weekday
                            delta = timedelta(days=days)
                            break
                    else:
                        days = weekday - weekdays[0]
                        delta = timedelta(days=weekdays_config['period'] * 7 - days)
                    schedule_time = datetime(now.year, now.month, now.day, hour, minute, second) + delta
            else:
                raise ValueError('timings_type error')
        elif schedule_type == TaskScheduleType.ONCE:
            schedule_time = type_config['schedule_start_time']
        return schedule_time

    def get_next_time(self, last_time: datetime):
        now = datetime.now()
        schedule_type = self.schedule_type
        type_config = self._config[schedule_type]
        next_time = last_time
        if schedule_type == TaskScheduleType.CONTINUOUS.value:
            while next_time < now:
                next_time += timedelta(seconds=self.period_schedule[1])
        elif schedule_type == TaskScheduleType.CRONTAB.value:
            next_time = get_next_cron_time(type_config['crontab'], now)
        elif schedule_type == TaskScheduleType.TIMINGS:
            timings_type = type_config['type']
            if timings_type == ScheduleTimingType.DAYS:
                while next_time < now:
                    next_time += timedelta(days=type_config['period'])
            elif timings_type == ScheduleTimingType.WEEKDAYS:
                weekdays_config = type_config["WEEKDAYS"]
                weekdays = weekdays_config['weekdays']
                weekday = next_time.isoweekday()
                for i in weekdays:
                    if i > weekday:
                        days = i - weekday
                        delta = timedelta(days=days)
                        break
                else:
                    days = weekday - weekdays[0]
                    delta = timedelta(days=weekdays_config['period'] * 7 - days)
                next_time = next_time + delta
            else:
                raise ValueError("unsupported timings type: %s" % schedule_type)
        elif schedule_type == TaskScheduleType.ONCE:
            next_time = datetime.max
        else:
            raise ValueError("unsupported schedule type: %s" % schedule_type)
        return next_time


class TaskSchedule(models.Model):
    id = models.AutoField(primary_key=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, db_constraint=False, verbose_name='任务')
    schedule_type = common_fields.CharField(default=TaskScheduleType.CONTINUOUS.value, verbose_name='计划类型',
                                            choices=TaskScheduleType.choices)
    priority = models.IntegerField(default=0, verbose_name='优先级')
    next_schedule_time = models.DateTimeField(default=timezone.now, verbose_name='下次运行时间', db_index=True)
    schedule_start_time = models.DateTimeField(default=datetime.min, verbose_name='开始时间')
    schedule_end_time = models.DateTimeField(default=datetime.max, verbose_name='结束时间')
    config = fields.ScheduleConfigField(default=dict, verbose_name='参数')
    status = common_fields.CharField(default=TaskScheduleStatus.OPENING.value, verbose_name='状态',
                                     choices=TaskScheduleStatus.choices)
    callback = models.ForeignKey(TaskScheduleCallback, on_delete=models.CASCADE,
                                 null=True, blank=True, db_constraint=False, verbose_name='回调')
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, db_constraint=False, verbose_name='用户')
    create_time = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def generate_next_schedule(self, now=None):
        # now = now or timezone.now()
        # type_config = self.config[self.type]
        # start, end = self.config.get('date_range', (None, None))
        # if self.type == TaskScheduleType.CONTINUOUS.value:
        #     self.next_schedule_time = now + timedelta(seconds=type_config['period'])
        # elif self.type == TaskScheduleType.CRONTAB.value:
        #     self.next_schedule_time = get_next_cron_time(type_config['crontab'], now)
        # elif self.type == TaskScheduleType.TIMINGS:
        #     timings_type = type_config['type']
        #     if timings_type == ScheduleTimingType.DAYS:
        #         n = now + timedelta(days=type_config['period'])
        #         hour, minute, second = type_config['DAYS'].split(':')
        #         self.next_schedule_time = datetime(n.year, n.month, n.day, int(hour), int(minute), int(second))
        #     elif timings_type == ScheduleTimingType.WEEKDAYS:
        #         weekdays_config = type_config["WEEKDAYS"]
        #         weekdays = weekdays_config['weekdays']
        #         weekday = now.isoweekday()
        #         for i in weekdays:
        #             if i > weekday:
        #                 days = i - weekday
        #                 n = now + timedelta(days=days)
        #                 break
        #         else:
        #             days = weekday - weekdays[0]
        #             n = now + timedelta(days=weekdays_config['period'] * 7 - days)
        #         hour, minute, second = type_config['time'].split(':')
        #         self.next_schedule_time = datetime(n.year, n.month, n.day, int(hour), int(minute), int(second))
        #
        #     else:
        #         raise ValueError('timings_type error')
        # else:
        #     self.next_schedule_time = datetime.max
        #     self.status = TaskScheduleStatus.DONE.value
        self.next_schedule_time = ScheduleConfig(**self.config).get_next_time(self.next_schedule_time)
        if self.next_schedule_time > self.schedule_end_time:
            self.next_schedule_time = datetime.max
            self.status = TaskScheduleStatus.DONE.value
        self.save(update_fields=('next_schedule_time', 'status'))
        return self

    class Meta:
        db_table = 'task_schedule'
        verbose_name = verbose_name_plural = '任务计划'
        ordering = ('-priority', 'next_schedule_time')

    def __str__(self):
        return self.task.name

    __repr__ = __str__

    def __lt__(self, other):
        return self.priority < other.priority

    def __gt__(self, other):
        return self.priority > other.priority


class TaskScheduleLog(models.Model):
    id = models.AutoField(primary_key=True)
    schedule = models.ForeignKey(TaskSchedule, db_constraint=False, on_delete=models.CASCADE, verbose_name='任务计划')
    status = common_fields.CharField(verbose_name='运行状态')
    result = common_fields.ConfigField(blank=True, null=True, verbose_name='结果')
    schedule_time = models.DateTimeField(verbose_name='计划时间')
    create_time = models.DateTimeField(default=timezone.now, verbose_name='创建时间')

    @property
    def finish_time(self):
        return self.create_time

    class Meta:
        db_table = 'task_schedule_log'
        verbose_name = verbose_name_plural = '任务日志'

    def __str__(self):
        return "schedule: %s, status: %s" % (self.schedule, self.status)

    __repr__ = __str__
