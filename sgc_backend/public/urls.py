from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from public import views

urlpatterns = [
    path('',views.IndexView.as_view()),
    path('api/restricted', views.RestrictedView.as_view(), name='restricted')
]

urlpatterns = format_suffix_patterns(urlpatterns)

