from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import *

urlpatterns = [
    path('example-process/', ExampleProcessView.as_view(), name='process-example'),
    path('process-list/',ProcessListView.as_view(),name='process-list'),
    path('process-detail/<str:pk>/',ProcessDetailView.as_view(),name='process-list'),
    path('process-kill/<str:celery_id>/',KillProcessView.as_view(),name="process-kill"),
    path('logs-process/<str:pk>/',LogEjecucionListView.as_view(),name='logs-process-list'),
    path('logs-process-task/<str:ejecucion>/<str:tarea>/',LogEjecucionTareaDetailView.as_view(),name="logs-process-task-detail"),
    
]
urlpatterns = format_suffix_patterns(urlpatterns)