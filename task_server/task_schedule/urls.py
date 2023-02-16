from django.urls import path
from . import views

urlpatterns = [
    path('task/', views.TaskListView.as_view()),
    path('task/<int:pk>/', views.TaskDetailView.as_view()),
    path('schedule/', views.TaskScheduleListView.as_view()),
    path('schedule/<int:pk>/', views.TaskScheduleDetailView.as_view()),
    path('schedule/queue/', views.TaskScheduleQueueAPI.as_view()),
]
