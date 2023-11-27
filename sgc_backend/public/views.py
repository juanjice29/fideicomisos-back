from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from sgc_backend.permissions import HasRolePermission

class IndexView(APIView):
   
    def get(self, request, format=None):
        content = {
            'wmsg':"Welcome to SGC Api Fiduciaria"
        }
        return Response(content)
    
class RestrictedView(APIView):
    permission_classes = [HasRolePermission]
    required_roles = [13, 12, 11]

    def get(self, request):
        return Response(data="Only for users with role 11,12,13")