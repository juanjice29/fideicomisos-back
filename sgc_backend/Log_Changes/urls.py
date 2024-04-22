from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import *
urlpatterns = [
    path('cambios_actor/', ChangesView.as_view(), name='changes-actor')


]

urlpatterns = format_suffix_patterns(urlpatterns)