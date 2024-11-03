from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from sgc_backend.permissions import HasRolePermission
from sgc_backend.permissions import HasRolePermission, LoggingJWTAuthentication
from .models import *
from actores.models import TipoActorDeContrato
from .serializers import *
from actores.serializers import TipoActorDeContratoSerializer
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ParseError
from rest_framework.exceptions import APIException
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import NotFound
from rest_framework import status

class IndexView(APIView):
    authentication_classes = []  # No requiere autenticación
    permission_classes = [AllowAny]
    def get(self, request, format=None):
        content = {
            'wmsg':"Sonar qube quality gate test 2"
        }
        return Response(content)

class RestrictedView(APIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]

    def get(self, request):
        return Response(data="Only for users with the authorized roles")

class TipoDeDocumentoListView(APIView):   
    permission_classes = [AllowAny]      

    def get(self,request) :        
        try:  
            queryset = TipoDeDocumento.objects.all().order_by('-idTipoPersona','tipoDocumento')
            queryset_serializer=TipoDeDocumentoSerializer(queryset,many=True)        
            return Response(queryset_serializer.data)
        except ValidationError as e:
            raise ParseError(detail=str(e))
        except Exception as e:
            raise APIException(detail=str(e))

class TipoDeActorListView(APIView):   
    permission_classes = [AllowAny]      

    def get(self,request) :        
        try:  
            queryset = TipoActorDeContrato.objects.all().order_by('tipoActor')
            queryset_serializer=TipoActorDeContratoSerializer(queryset,many=True)        
            return Response(queryset_serializer.data)
        except ValidationError as e:
            raise ParseError(detail=str(e))
        except Exception as e:
            raise APIException(detail=str(e))  
        
class TipoActorView(APIView):    
    def get_object_by_id(self,pk):
        try:
            return TipoActorDeContrato.objects.get(pk=pk)        
        except  TipoActorDeContrato.DoesNotExist:
            raise NotFound(detail='Tipo de actor de contrato no encontrado')
        except Exception as e:
            raise APIException(detail=str(e)) 
    
class PeriodoTrimestralListView(APIView):
    permission_classes = [AllowAny]   
    def get(self,request):       
        try:  
            queryset = PriodoTrimestral.objects.all().order_by('-periodo')
            queryset_serializer=PriodoTrimestralSerializer(queryset,many=True)        
            return Response(queryset_serializer.data)
        except ValidationError as e:
            raise ParseError(detail=str(e))
        except Exception as e:
            raise APIException(detail=str(e)) 
        
class GenericParamDetailView(APIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    
    def get_by_name(self,nombre):
        try:
            return ParametrosGenericos.objects.get(nombre=nombre)
        except ParametrosGenericos.DoesNotExist:
            raise NotFound(detail='Parametro no encontrado.')
        except Exception as e:
            raise APIException(detail=str(e))
        
    def get(self,request,nombre):
        try:
            param=self.get_by_name(nombre)
            serializer=ParametrosGenericosSerializer(param)
            return Response(serializer.data,status=status.HTTP_200_OK)            
        except ParametrosGenericos.DoesNotExist:
            raise NotFound('Parametro no encontrado.')
        except Exception as e:
            return Response({'error': str(e)}, status=500) 
            