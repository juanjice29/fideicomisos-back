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
        if hasattr(request.user, 'profile') and hasattr(request.user.profile, 'rol'):
            Rol_Vista = Permisos.objects.filter(
                rol=request.user.profile.rol,
                accion__nombre=request.method
            ).values_list('vista__nombre', flat=True)
        else:
            Rol_Vista = []
        return request.user.is_authenticated and view.__class__.__name__ in Rol_Vista