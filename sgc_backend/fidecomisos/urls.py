from django.urls import path
from .views import FideicomisoList
from rest_framework.urlpatterns import format_suffix_patterns
from .views import *
urlpatterns = [
    path('fideicomisos/', FideicomisoList.as_view(), name='fideicomiso-list'),
    path('tipodedocumento/', TipoDeDocumentoListView.as_view(), name='tipodedocumento-list'),
    path('update_fideicomiso/', UpdateFideicomisoView.as_view(), name='update-fideicomiso'),
    path('update_encargo/', UpdateEncargoFromTemp.as_view(), name='update-encargo'),
    path('update_encargotemp/', UpdateEncargoTemp.as_view(), name='update-encargo-temp')
]

urlpatterns = format_suffix_patterns(urlpatterns)