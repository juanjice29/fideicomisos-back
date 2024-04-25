from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import *
urlpatterns = [
    path('logs-by-key/', ChangesView.as_view(), name='logs-by-key')


]

urlpatterns = format_suffix_patterns(urlpatterns)