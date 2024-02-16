from django.urls import path
from .views import BeneficiarioDianByUserTypeView
from .views import UpdateBeneficiarioDianView
from .views import TestTaskView
from .views import RunJarView
from .views import FillPostalCodeView
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('clients_by_user_type/<int:user_type>/', BeneficiarioDianByUserTypeView.as_view()),
    path('update_client/', UpdateBeneficiarioDianView.as_view(), name='update_client'),
    path('test_task/',TestTaskView.as_view()),
    path('excel/',FillPostalCodeView.as_view()),
    path('jar/',RunJarView.as_view())
    
]

urlpatterns = format_suffix_patterns(urlpatterns)