from django.urls import path
from .views import ClientsByUserTypeView
from .views import UpdateClientView
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('clients_by_user_type/<int:user_type>/', ClientsByUserTypeView.as_view()),
    path('update_client/', UpdateClientView.as_view(), name='update_client'),
]

urlpatterns = format_suffix_patterns(urlpatterns)