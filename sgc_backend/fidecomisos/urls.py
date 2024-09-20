from django.urls import path
from .views import FideicomisoList
from rest_framework.urlpatterns import format_suffix_patterns
from .views import *
urlpatterns = [
    path('fideicomisos/', FideicomisoList.as_view(), name='fideicomisos-list'),    
    path('fideicomiso/<str:codigo_sfc>/', FideicomisoView.as_view(), name='fideicomiso_detail'),
    path('encargos/<str:codigo_sfc>/', EncargoListView.as_view(), name='encargos-list'), 
    path('actores/<str:codigo_sfc>/', ActoresByFideicomisoList.as_view(), name='actores-by-fidei-list'),
    path('carguegeneral/', CargueFideicomisoEncargosView.as_view(), name='fideicomisos-encargos'),
 
]

urlpatterns = format_suffix_patterns(urlpatterns)