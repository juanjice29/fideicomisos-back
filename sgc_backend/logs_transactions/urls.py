from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import *
urlpatterns = [
    path('logs-creacion/<str:model_name>/<str:object_key>/', LogCreateView.as_view(), name='losgs_create'),
    path('logs-creacion-list/', LogCreateListView.as_view(), name='losgs_create_list'),
    path('logs-actualizacion-list/<str:model_name>/<str:object_key>/', LogUpdateListView.as_view(), name='logs_update_list'),

]

urlpatterns = format_suffix_patterns(urlpatterns)