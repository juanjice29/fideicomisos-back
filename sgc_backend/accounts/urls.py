from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from accounts import views
from .views import *
from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetCompleteView
schema_view = get_schema_view(
   openapi.Info(
      title="API DE AUTENTICACION",
      default_version='v1',
      description="DOCUMENTACION DE LA API DE AUTENTICACION",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
   
    path('api/login', views.LoginView.as_view(), name='login'),
    
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('account.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('account.yaml', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),
    path('api/login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/get_permisos/', PermisosView.as_view(), name='token_refresh'),
    path('password_reset/', PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
]   

urlpatterns = format_suffix_patterns(urlpatterns)

