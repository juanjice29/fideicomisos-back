from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from sgc_backend.permissions import HasRolePermission
from rest_framework.exceptions import PermissionDenied
from accounts.models import Permisos # Import the Permission model
from sgc_backend.permissions import HasRolePermission, LoggingJWTAuthentication
class IndexView(APIView):
   
    def get(self, request, format=None):
        content = {
            'wmsg':"Welcome to SGC Api Fiduciaria"
        }
        return Response(content)

class RestrictedView(APIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]

    def get(self, request):
        return Response(data="Only for users with the authorized roles")