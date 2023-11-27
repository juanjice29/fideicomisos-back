from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from sgc_backend.permissions import IsEmployee
class IndexView(APIView):
   
    def get(self, request, format=None):
        content = {
            'wmsg':"Welcome to SGC Api Fiduciaria"
        }
        return Response(content)
    
class RestrictedView(APIView):
    permission_classes = [IsEmployee]
    def get(self, request):
        return Response(data="Only for logged in users")