from django.shortcuts import render
from rest_framework.views import APIView

from sgc_backend.pagination import CustomPageNumberPagination
from .tasks import task_process_example
from rest_framework.response import Response
from sgc_backend.permissions import HasRolePermission, LoggingJWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ParseError,NotFound,APIException
from accounts.models import User
from .serializers import EjecucionProcesoListSerializer,LogEjecucionProcesoListSerializer
from rest_framework import generics,filters,status
from .models import EjecucionProceso,LogEjecucionProceso
from rest_framework.pagination import PageNumberPagination
# Create your views here.

class ExampleProcessView(APIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    def get(self,request):
                  
        result=task_process_example.delay(usuario_id=request.user.id,disparador="MAN")        
        return Response({"proceso": result.id}, status=status.HTTP_202_ACCEPTED)

class ProcessDetailView(APIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    def get_object(self,pk):
        try:
            return EjecucionProceso.objects.get(pk=pk)        
        except  EjecucionProceso.DoesNotExist:
            raise NotFound(detail='Proceso no encontrado')
        except Exception as e:
            raise APIException(detail=str(e))
    def get(self,request,pk,format=None):
        proceso=self.get_object(pk)
        serializer=EjecucionProcesoListSerializer(proceso)
        return Response(serializer.data,status=status.HTTP_200_OK)
        
class ProcessListView(generics.ListAPIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    
    pagination_class = CustomPageNumberPagination 
    queryset= EjecucionProceso.objects.all()
    ordering=['-fechaInicio']
    serializer_class=EjecucionProcesoListSerializer
    filter_backends=[filters.SearchFilter,filters.OrderingFilter] 
    search_fields = ['celeryTaskId','proceso__nombre','proceso__tipoProceso__nombre']
    
    def get_queryset(self):
        try:
            return self.queryset
        except Exception as e:
            raise APIException(detail=str(e))  

class LogEjecucionListView(APIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    
    queryset= LogEjecucionProceso.objects.all()
    ordering=['-fecha']
    
    def get(self,request,pk,format=None):
        try:
            queryset=LogEjecucionProceso.objects.filter(ejecucionProceso_id=pk)
            paginator = PageNumberPagination()
            paginator.page_size = 15
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            serializer=LogEjecucionProcesoListSerializer(paginated_queryset,many=True)            
            return  paginator.get_paginated_response(serializer.data)
        except Exception as e:
            raise APIException(detail=str(e))