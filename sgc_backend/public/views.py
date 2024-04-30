from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from sgc_backend.permissions import HasRolePermission
from sgc_backend.permissions import HasRolePermission, LoggingJWTAuthentication
from .models import TipoDeDocumento
from actores.models import TipoActorDeContrato
from .serializers import TipoDeDocumentoSerializer
from actores.serializers import TipoActorDeContratoSerializer
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ParseError
from rest_framework.exceptions import APIException
from rest_framework.permissions import AllowAny

class IndexView(APIView):
    authentication_classes = []  # No requiere autenticación
    permission_classes = [AllowAny]
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