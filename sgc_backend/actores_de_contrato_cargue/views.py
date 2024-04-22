from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import generics
from fidecomisos.models import Fideicomiso
from .forms import UploadFileForm
from rest_framework.exceptions import NotFound
import pandas as pd
from rest_framework.permissions import IsAuthenticated
from .models import ActorDeContrato, TipoActorDeContrato
from rest_framework import viewsets
from django.core.exceptions import ValidationError
from .models import ActorDeContrato
from .serializers import ActorDeContratoSerializer
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
    
class TipoActorDeContratoListView(generics.ListAPIView):
    queryset = TipoActorDeContrato.objects.all().order_by('id')
    serializer_class = TipoActorDeContratoSerializer
    
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
            raise NotFound('No existe ese fideicomiso ')
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
class ActorDeContratoCreateViewExcel(APIView):
    def post(self, request):
        try: 
            file = request.data['file']
            data = pd.read_excel(file)
            response_data = []
            for index, row in data.iterrows():
                codigos_sfc = row['FideicomisoAsociado']
                tipo_actor_id = row['TipoActor']
                PrimerNombre = row['PrimerNombre']
                SegundoNombre = row['SegundoNombre']
                PrimerApellido = row['PrimerApellido']
                SegundoApellido =row['SegundoApellido']
                numeroidentificacion = row['NumeroIdentificacion']
                try:
                    tipo_documento_instance = TipoDeDocumento.objects.get(TipoDocumento=row['TipoIdentificacion'])
                except TipoDeDocumento.DoesNotExist:
                    response_data.append({
                        'NumeroIdentificacion': numeroidentificacion,
                        'status': 'error',
                        'message': 'TipoDeDocumento no existe'
                    })
                    continue
                fideicomisos = Fideicomiso.objects.filter(CodigoSFC__exact=codigos_sfc)
                if not fideicomisos.exists():
                    response_data.append({
                        'NumeroIdentificacion': numeroidentificacion,
                        'status': 'error',
                        'message': 'Fideicomiso no existe'
                    })
                    continue
                tipo_actor = TipoActorDeContrato.objects.filter(id=tipo_actor_id).first()
                if not tipo_actor:
                    response_data.append({
                        'NumeroIdentificacion': numeroidentificacion,
                        'status': 'error',
                        'message': 'TipoActor no existe'
                    })
                    continue
                try:
                    actor = ActorDeContrato.objects.create(
                        TipoIdentificacion=tipo_documento_instance,
                        NumeroIdentificacion=numeroidentificacion,
                        TipoActor=tipo_actor,
                        PrimerNombre=PrimerNombre,
                        SegundoNombre=SegundoNombre,
                        PrimerApellido=PrimerApellido,
                        SegundoApellido=SegundoApellido,
                        Activo=True,
                        FechaActualizacion=timezone.now(),
                        
                    )
                    actor.FideicomisoAsociado.set(fideicomisos)
                    response_data.append({
                        'NumeroIdentificacion': numeroidentificacion,
                        'status': 'success'
                    })
                except IntegrityError as e:
                    return Response({
                        'NumeroIdentificacion': numeroidentificacion,
                        'status': 'error',
                        'message': 'La relación de NumeroIdentificacion con Fideicomiso ya existe',
                        'error': str(e)
                    })
                return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class ActorDeContratoCreateView(APIView):
    def post(self, request):
        try:
            codigos_sfc = request.data.get('FideicomisoAsociado')
            tipo_actor_id = request.data.get('TipoActor')
            PrimerNombre = request.data.get('PrimerNombre')
            SegundoNombre = request.data.get('SegundoNombre')
            PrimerApellido = request.data.get('PrimerApellido')
            SegundoApellido = request.data.get('SegundoApellido')
            numeroidentificacion = request.data.get('NumeroIdentificacion')
            try:
                tipo_documento_instance = TipoDeDocumento.objects.get(TipoDocumento=request.data['TipoIdentificacion'])
            except TipoDeDocumento.DoesNotExist:
                return Response({'status': 'invalid request', 'message': 'TipoDeDocumento no existe'}, status=status.HTTP_400_BAD_REQUEST)
            fideicomisos = Fideicomiso.objects.filter(CodigoSFC__in=codigos_sfc).first()
            if not fideicomisos:
                return Response({'status': 'invalid request', 'message': 'Fideicomiso no existe'}, status=status.HTTP_400_BAD_REQUEST)

            tipo_actor = TipoActorDeContrato.objects.filter(id=tipo_actor_id).first()
            if not tipo_actor:
                return Response({'status': 'invalid request', 'message': 'TipoActor no existe'}, status=status.HTTP_400_BAD_REQUEST)

            if len(numeroidentificacion) > 12:
                return Response({'status': 'invalid request', 'message': 'NumeroIdentificacion debe ser de 12 caracteres o menos'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                actor = ActorDeContrato.objects.create(
                    TipoIdentificacion=tipo_documento_instance,
                    NumeroIdentificacion=numeroidentificacion,
                    TipoActor=tipo_actor,
                    PrimerNombre=PrimerNombre,
                    SegundoNombre=SegundoNombre,
                    PrimerApellido=PrimerApellido,
                    SegundoApellido=SegundoApellido,
                    Activo=True,
                    FechaActualizacion=timezone.now(),
                    
                )
                actor.FideicomisoAsociado.set([fideicomisos])
            except IntegrityError as e:
                return Response({
                    'status': 'error',
                    'message': 'La relación de NumeroIdentificacion con Fideicomiso ya existe',
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
        except Exception as e:
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
class ActorDeContratoUpdateView(generics.UpdateAPIView):
    queryset = ActorDeContrato.objects.all()
    serializer_class = ActorDeContratoSerializer
    lookup_field = 'id'
    def put(self, request, *args, **kwargs):
        try:
            instance = self.get_object()

            # request.data is the JSON object sent from the Angular frontend
            data = request.data

            tipo_documento_instance = TipoDeDocumento.objects.get(TipoDocumento=data['TipoIdentificacion'])
            fideicomiso = Fideicomiso.objects.get(CodigoSFC=data['FideicomisoAsociado'])
            tipo_actor = TipoActorDeContrato.objects.get(id=data['TipoActor'])
            instance.TipoIdentificacion = tipo_documento_instance
            instance.FideicomisoAsociado = fideicomiso
            instance.NumeroIdentificacion = data['NumeroIdentificacion']
            instance.TipoActor = tipo_actor
            instance.PrimerNombre=data['PrimerNombre']
            instance.SegundoNombre=data['SegundoNombre']
            instance.PrimerApellido=data['PrimerApellido']
            instance.SegundoApellido=data['SegundoApellido']
            instance.FechaActualizacion = timezone.now()
            instance.Activo=data['Activo']
            instance.save()

            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        except TipoDeDocumento.DoesNotExist:
            return Response({'status': 'invalid request', 'message': 'TipoDeDocumento no existe'}, status=status.HTTP_400_BAD_REQUEST)
        except Fideicomiso.DoesNotExist:
            return Response({'status': 'invalid request', 'message': 'Fideicomiso no existe'}, status=status.HTTP_400_BAD_REQUEST)
        except TipoActorDeContrato.DoesNotExist:
            return Response({'status': 'invalid request', 'message': 'TipoActor no existe'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class ActorDeContratoDeleteView(generics.DestroyAPIView):
    queryset = ActorDeContrato.objects.all()
    lookup_field = 'id'
    
