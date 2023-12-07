from django.urls import path
from .views import FideicomisoList
from rest_framework.urlpatterns import format_suffix_patterns
from .views import *
urlpatterns = [
    path('fideicomisos/', FideicomisoList.as_view(), name='fideicomiso-list'),
    path('encargos/', EncargoListView.as_view(), name='encargo-list'),
    path('update_fideicomiso/', UpdateFideicomisoView.as_view(), name='update-fideicomiso'),
    path('traer_fideicomiso/', FetchFideicomisoView.as_view(), name='traer-fideicomiso'),
    path('update_encargos/', UpdateEncargoView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)