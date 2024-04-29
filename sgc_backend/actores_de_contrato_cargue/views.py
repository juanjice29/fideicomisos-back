from django.shortcuts import render
from django.http import JsonResponse,Http404
from rest_framework import generics
from fidecomisos.models import Fideicomiso
from .forms import UploadFileForm
from rest_framework.exceptions import NotFound
import pandas as pd
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from .models import ActorDeContrato, TipoActorDeContrato
from rest_framework import viewsets
from django.core.exceptions import ValidationError
from .models import ActorDeContrato
from .serializers import ActorDeContratoReadSerializer,TipoActorDeContratoSerializer,ActorDeContratoCreateSerializer
from fidecomisos.serializers import FideicomisoSerializer
from fidecomisos.models import Encargo, TipoDeDocumento
from fidecomisos.serializers import EncargoSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from rest_framework import generics 
from django.db import IntegrityError
from sgc_backend.permissions import HasRolePermission, LoggingJWTAuthentication
from rest_framework.exceptions import ParseError
from rest_framework.exceptions import APIException
from sgc_backend.pagination import CustomPageNumberPagination
from fidecomisos.models import Fideicomiso
from django.db import transaction
from rest_framework.parsers import FileUploadParser
from rest_framework import filters


class ActorView(APIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    def get_object_by_id(self,pk):
        try:
            return ActorDeContrato.objects.get(ActorDeContrato.id==pk)        
        except  ActorDeContrato.DoesNotExist:
            raise Response({'status': 'error', 'message': 'Actor de contrato no encontraro'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   
    def get_object(self,tipo_id,nro_id):
        try:
            return ActorDeContrato.objects.get(TipoIdentificacion=tipo_id,NumeroIdentificacion=nro_id)        
        except  ActorDeContrato.DoesNotExist:
            raise Response({'status': 'error', 'message': 'Actor de contrato no encontraro'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   
        
    def get(self,request,tipo_id,nro_id,formate=None):               
        actor=self.get_object(tipo_id,nro_id)
        serializer=ActorDeContratoReadSerializer(actor)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def put(self,request,tipo_id,nro_id):
        actor=self.get_object(tipo_id,nro_id)
        serializer=ActorDeContratoCreateSerializer(actor,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
         

    