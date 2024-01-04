from django.urls import path
from .views import BeneficiarioDianByUserTypeView
from .views import UpdateBeneficiarioDianView
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('clients_by_user_type/<int:user_type>/', BeneficiarioDianByUserTypeView.as_view()),
    path('update_client/', UpdateBeneficiarioDianView.as_view(), name='update_client'),
]

urlpatterns = format_suffix_patterns(urlpatterns)