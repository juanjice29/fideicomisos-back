from django.urls import path
from .views import GenerateRPBF,DownloadDianReport,ConfirmRPBF
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [    
    path('download_report/',DownloadDianReport.as_view()),
    path('genrep/',GenerateRPBF.as_view()),
    path('confirmrep/',ConfirmRPBF.as_view())

]

urlpatterns = format_suffix_patterns(urlpatterns)