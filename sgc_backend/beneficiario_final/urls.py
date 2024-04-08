from django.urls import path
from .views import RunAllTasksView
from .views import TaskStatusView
from .views import DownloadDianReport
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    #path('clients_by_user_type/<int:user_type>/', BeneficiarioDianByUserTypeView.as_view()),
    #path('update_client/', UpdateBeneficiarioDianView.as_view(), name='update_client'),
    path('run_tasks/',RunAllTasksView.as_view()),
    path('generate_xml/',TaskStatusView.as_view()),
    path('download_report/',DownloadDianReport.as_view())

]

urlpatterns = format_suffix_patterns(urlpatterns)