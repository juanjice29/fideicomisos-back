from django.shortcuts import render
from rest_framework.views import APIView
from .tasks import task_process_example
from rest_framework.response import Response
from rest_framework import status
from sgc_backend.permissions import HasRolePermission, LoggingJWTAuthentication
from rest_framework.permissions import IsAuthenticated
from accounts.models import User
# Create your views here.

class ExampleProcessView(APIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    def get(self,request):
                  
        result=task_process_example.delay(usuario_id=request.user.id,disparador="MAN")        
        return Response({"proceso": result.id}, status=status.HTTP_202_ACCEPTED)