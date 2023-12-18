import logging
from rest_framework.permissions import BasePermission
from django.core.exceptions import PermissionDenied
from accounts.models import Permisos
logger = logging.getLogger(__name__)
from rest_framework_simplejwt.authentication import JWTAuthentication

class LoggingJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        #logger.info('authenticate called')
        result = super().authenticate(request)
        #logger.info('authenticate result: %s', result)
        return result
class HasRolePermission(BasePermission):
    
    def has_permission(self, request, view):
        #logger.info('User: %s', request.user)
        #logger.info('Is authenticated: %s', request.user.is_authenticated)
        #logger.info('Has profile: %s', hasattr(request.user, 'profile'))
        #logger.info('Has role: %s', hasattr(request.user.profile, 'rol') if hasattr(request.user, 'profile') else False)
        if hasattr(request.user, 'profile') and hasattr(request.user.profile, 'rol'):
            role_views = Permisos.objects.filter(role=request.user.profile.rol).values_list('view__name', flat=True)
        else:
            role_views = []
        #logger.info('Current view: %s', view.__class__.__name__)
        #logger.info('Can access view: %s', view.__class__.__name__ in role_views)
        return request.user.is_authenticated and view.__class__.__name__ in role_views        
        