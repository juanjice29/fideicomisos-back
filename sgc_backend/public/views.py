from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from sgc_backend.permissions import HasRolePermission
from rest_framework.exceptions import PermissionDenied
from accounts.models import Permisos# Import the Permission model
class IndexView(APIView):
   
    def get(self, request, format=None):
        content = {
            'wmsg':"Welcome to SGC Api Fiduciaria"
        }
        return Response(content)

class RestrictedView(APIView):
    permission_classes = [HasRolePermission]
    def check_permissions(self, request):
        self.required_roles = list(Permisos.objects.filter(view__name='RestrictedView').values_list('role__name', flat=True))
        if not request.user.profile.rol.name in self.required_roles:
            raise PermissionDenied('You do not have permission to view this.')
        return super().check_permissions(request)

    def get(self, request):
        return Response(data="Only for users with the authorized roles")