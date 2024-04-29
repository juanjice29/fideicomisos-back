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
from .serializers import ActorDeContratoSerializer,ActorDeContratoCreateSerializer,TipoActorDeContratoSerializer
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
        
    def get(sel,request,tipo_id,nro_id):
        try:            
            actor=ActorDeContrato.objects.get(TipoIdentificacion=tipo_id,NumeroIdentificacion=nro_id)
            serializer=ActorDeContratoSerializer(actor)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except ActorDeContrato.DoesNotExist:
            raise Response({'status': 'error', 'message': 'Actor de contrato no encontraro'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
         

    