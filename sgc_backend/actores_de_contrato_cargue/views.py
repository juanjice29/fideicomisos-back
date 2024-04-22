from django.shortcuts import render
from django.http import JsonResponse
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
from .serializers import ActorDeContratoSerializer,ActorDeContratoCreateSerializer
from fidecomisos.serializers import FideicomisoSerializer
from fidecomisos.models import Encargo, TipoDeDocumento
from fidecomisos.serializers import EncargoSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from rest_framework import generics
from .serializers import TipoActorDeContratoSerializer
from django.db import IntegrityError
from sgc_backend.permissions import HasRolePermission, LoggingJWTAuthentication
from rest_framework.exceptions import ParseError
from rest_framework.exceptions import APIException
from sgc_backend.pagination import CustomPageNumberPagination
from fidecomisos.models import Fideicomiso
from django.db import transaction
from rest_framework.parsers import FileUploadParser

class FileUploadView(APIView):
    parser_class = (FileUploadParser,)

    def post(self, request, *args, **kwargs):
        excel_file = request.data['file']
        data = pd.read_excel(excel_file)

        actors = []

        with transaction.atomic():
            for _, row in data.iterrows():
                tipo_identificacion = TipoDeDocumento.objects.get(id=row["TipoIdentificacion"])
                tipo_actor = TipoActorDeContrato.objects.get(id=row["TipoActor"])
                fideicomiso_asociado = Fideicomiso.objects.filter(id__in=row["FideicomisoAsociado"].split(','))

                actor = ActorDeContrato(
                    TipoIdentificacion=tipo_identificacion,
                    NumeroIdentificacion=row["NumeroIdentificacion"],
                    PrimerNombre=row["PrimerNombre"],
                    SegundoNombre=row["SegundoNombre"],
                    PrimerApellido=row["PrimerApellido"],
                    SegundoApellido=row["SegundoApellido"],
                    TipoActor=tipo_actor,
                    FechaActualizacion=row["FechaActualizacion"],
                    Activo=row["Activo"]
                )
                actor.save()
                actor.FideicomisoAsociado.set(fideicomiso_asociado)
                actors.append(actor)

        return Response({"actors": [actor.id for actor in actors]}, status=status.HTTP_201_CREATED)
    
class TipoActorDeContratoListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]  
    def get(self,request):
        try:        
            queryset = TipoActorDeContrato.objects.all().order_by('id')
            queryset_serializer=TipoActorDeContratoSerializer(queryset,many=True)  
            return Response(queryset_serializer.data)
        except ValidationError as e:
            raise ParseError(detail=str(e))
        except Exception as e:
            raise APIException(detail=str(e))
    
    
class ActorDeContratoListAllView(generics.ListAPIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    pagination_class = CustomPageNumberPagination
    def get(self,request):
        try:
            Actor = ActorDeContrato.objects.order_by('NumeroIdentificacion')
            paginator = CustomPageNumberPagination()
            paginated_actor = paginator.paginate_queryset(Actor, request)
            actor_serializer = ActorDeContratoSerializer(paginated_actor, many=True)
            return paginator.get_paginated_response(actor_serializer.data)
        
        except Exception as e:
            return Response({'error':'invalid request', 'message':str(e)}, status=500)
    
class ActorDeContratoListView(generics.ListAPIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    pagination_class = CustomPageNumberPagination
    def get(self, request, codigo_sfc):
        try:
            fideicomiso = Fideicomiso.objects.get(CodigoSFC=codigo_sfc)
        except ObjectDoesNotExist:
            raise NotFound('Fideicomiso no encontrado.')
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        try:
            Actor = ActorDeContrato.objects.filter(FideicomisoAsociado__in=[fideicomiso]).order_by('NumeroIdentificacion')
            for field, value in request.query_params.items():
                if field in [f.name for f in  ActorDeContrato._meta.get_fields()]:
                    Actor = Actor.filter(**{field: value})
            paginator = CustomPageNumberPagination()
            paginated_actor = paginator.paginate_queryset(Actor, request)
            actor_serializer = ActorDeContratoSerializer(paginated_actor, many=True)
            return paginator.get_paginated_response(actor_serializer.data)
        except ObjectDoesNotExist:
            return Response({'error':'invalid request','message': 'No se encuentra el Actor de Contrato :('}, status=404)
        except Exception as e:
            return Response({'error':'invalid request', 'message':str(e)}, status=500)
        
class ActorDeContratoView(APIView):
    def post(self, request):
        try:
            actor = request.data    
            codigos_sfc = actor.get('FideicomisoAsociado')                  
            fideicomiso = Fideicomiso.objects.filter(CodigoSFC__in=codigos_sfc)            
            if len(codigos_sfc)!=len(fideicomiso):
                return Response({'status': 'invalid request', 'message': 'Fideicomiso no existe'}, status=status.HTTP_400_BAD_REQUEST)                       
            actor_serializer = ActorDeContratoCreateSerializer(data=actor)
            if actor_serializer.is_valid():    
                actor_serializer.save()
                return Response(actor_serializer.data, status=status.HTTP_201_CREATED)
            return Response(actor_serializer.errors, status=status.HTTP_400_BAD_REQUEST)            
        except Exception as e:
            print(e)
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def put(self,request):
        try:
            actor = request.data    
            codigos_sfc = actor.get('FideicomisoAsociado')       
            numero_identificacion = actor.get('NumeroIdentificacion')           
            fideicomiso = Fideicomiso.objects.filter(CodigoSFC__in=codigos_sfc)            
            if len(codigos_sfc)!=len(fideicomiso):
                return Response({'status': 'invalid request', 'message': 'Fideicomiso no existe'}, status=status.HTTP_400_BAD_REQUEST)               
            actor_object=ActorDeContrato.objects.get(NumeroIdentificacion=numero_identificacion)  
            fideicomisos_ids = list(actor_object.FideicomisoAsociado.values_list('CodigoSFC', flat=True))
            fideicomisos_ids=list(set(fideicomisos_ids+codigos_sfc))
            print(fideicomisos_ids)    
            actor["FideicomisoAsociado"]=fideicomisos_ids    
            actor_serializer = ActorDeContratoCreateSerializer(actor_object,data=actor)
            if actor_serializer.is_valid():    
                actor_serializer.save()
                return Response(actor_serializer.data, status=status.HTTP_201_CREATED)
            return Response(actor_serializer.errors, status=status.HTTP_400_BAD_REQUEST)            
        except Exception as e:
            print(e)
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        
class ListFideicomisosOfActorView(generics.ListAPIView):
    serializer_class = FideicomisoSerializer

    def get(self, request, *args, **kwargs):
        try:
            numero_identificacion = request.query_params['NumeroIdentificacion']
            actor = ActorDeContrato.objects.get(NumeroIdentificacion=numero_identificacion)
            fideicomisos = actor.FideicomisoAsociado.all()
            serializer = self.get_serializer(fideicomisos, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ActorDeContrato.DoesNotExist:
            return Response({'status': 'invalid request', 'message': 'ActorDeContrato no existe'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AddFideicomisosToActorView(generics.UpdateAPIView):
    queryset = ActorDeContrato.objects.all()

    def put(self, request, *args, **kwargs):
        try:
            numero_identificacion = request.data['NumeroIdentificacion']
            actor = ActorDeContrato.objects.get(NumeroIdentificacion=numero_identificacion)
            fideicomiso_codigos = request.data['FideicomisoAsociado']  # list of Fideicomiso CodigoSFC

            for codigo in fideicomiso_codigos:
                fideicomiso = Fideicomiso.objects.get(CodigoSFC=codigo)
                actor.FideicomisoAsociado.add(fideicomiso)

            actor.save()

            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        except ActorDeContrato.DoesNotExist:
            return Response({'status': 'invalid request', 'message': 'ActorDeContrato no existe'}, status=status.HTTP_400_BAD_REQUEST)
        except Fideicomiso.DoesNotExist:
            return Response({'status': 'invalid request', 'message': 'Fideicomiso no existe'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
