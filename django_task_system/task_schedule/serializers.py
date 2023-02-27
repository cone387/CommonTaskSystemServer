from . import models
from django_task_system.common_objects.serializers import CommonCategorySerializer, CommonTagSerializer
from rest_framework import serializers

"""
id = models.AutoField(primary_key=True)
    parent = models.ForeignKey('self', db_constraint=False, on_delete=models.DO_NOTHING,
                               null=True, blank=True, verbose_name='父任务')
    name = models.CharField(max_length=100, verbose_name='任务名')
    category = models.ForeignKey(CommonCategory, db_constraint=False, on_delete=models.DO_NOTHING, verbose_name='类别')
    tags = models.ManyToManyField(CommonTag, blank=True, db_constraint=False, verbose_name='标签')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    config = common_fields.ConfigField(default=common_fields.get_default_config('Task'),
                                       blank=True, null=True, verbose_name='参数')
    status = common_fields.CharField(max_length=1, default=TaskStatus.ENABLE.value, verbose_name='状态',
                                     choices=TaskStatus.choices)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, db_constraint=False, verbose_name='用户')
    create_time = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
"""


class TaskSerializer(serializers.ModelSerializer):
    category = CommonCategorySerializer()
    tags = CommonTagSerializer(many=True)
    parent = serializers.SerializerMethodField()

    def get_parent(self, obj):
        if obj.parent:
            return self.__class__(obj.parent).data

    class Meta:
        model = models.Task
        exclude = ('update_time', )


class QueueTaskSerializer(TaskSerializer):

    class Meta:
        model = models.Task
        fields = ('id', 'name', 'config', 'category', 'status', 'parent', )


class TaskCallbackSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.TaskScheduleCallback
        exclude = ('update_time', )


class TaskScheduleSerializer(serializers.ModelSerializer):
    task = TaskSerializer()
    callback = TaskCallbackSerializer()

    class Meta:
        model = models.TaskSchedule
        exclude = ('update_time', )


class QueueScheduleSerializer(TaskScheduleSerializer):
    task = QueueTaskSerializer()
    callback = TaskCallbackSerializer()

    class Meta:
        model = models.TaskSchedule
        fields = ('id', 'task', 'type', 'next_schedule_time', 'update_time', 'callback', 'user')


class TaskScheduleLogSerializer(serializers.ModelSerializer):
    schedule = TaskScheduleSerializer()

    class Meta:
        model = models.TaskScheduleLog
        exclude = ('update_time', )
