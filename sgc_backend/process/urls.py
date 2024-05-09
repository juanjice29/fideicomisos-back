from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import *

urlpatterns = [
    path('example-process/', ExampleProcessView.as_view(), name='process'),
]
urlpatterns = format_suffix_patterns(urlpatterns)