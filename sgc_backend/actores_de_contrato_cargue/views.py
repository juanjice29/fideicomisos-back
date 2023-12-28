from django.shortcuts import render
from django.http import JsonResponse
from fidecomisos.models import Fideicomiso
from .forms import UploadFileForm
import pandas as pd
from rest_framework.permissions import IsAuthenticated
from .models import ActorDeContrato, TipoActorDeContrato
from rest_framework import viewsets
from django.core.exceptions import ValidationError
from .models import ActorDeContrato
from .serializers import ActorDeContratoSerializer
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
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            data = pd.read_excel(excel_file)
            for index, row in data.iterrows():
                try:
                    fideicomiso = Fideicomiso.objects.get(CodigoSFC=row['FideicomisoAsociado'])
                except ObjectDoesNotExist:
                    return JsonResponse({'status': 'error', 'message': f'Fideicomiso {row["FideicomisoAsociado"]} no existe'}, status=400)

                ActorDeContrato.objects.create(
                    TipoIdentificacion=row['TipoIdentificacion'],
                    NumeroIdentificacion=row['NumeroIdentificacion'],
                    Nombre=row['Nombre'],
                    TipoActor=row['TipoActor'],
                    FideicomisoAsociado=fideicomiso,
                    FechaActualizacion=pd.to_datetime(row['FechaActualizacion'])
                )
            return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'invalid request'}, status=400)

class TipoActorDeContratoListView(generics.ListAPIView):
    queryset = TipoActorDeContrato.objects.all().order_by('id')
    serializer_class = TipoActorDeContratoSerializer
class ActorDeContratoListView(generics.ListAPIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    serializer_class = ActorDeContratoSerializer
    pagination_class = CustomPageNumberPagination
    def get_queryset(self):
        try:
            queryset = ActorDeContrato.objects.all()
            FideicomisoAsociado = self.request.query_params.get('FideicomisoAsociado', None)
            Primer_Nombre = self.request.query_params.get('Primer_Nombre', None)
            Segundo_Nombre = self.request.query_params.get('Segundo_Nombre', None)
            Primer_Apellido = self.request.query_params.get('Primer_Apellido', None)
            Segundo_Apellido = self.request.query_params.get('Segundo_Apellido', None)
            TipoActor = self.request.query_params.get('TipoActor', None)
            FideicomisoAsociado = self.request.query_params.get('FideicomisoAsociado', None)
            FechaActualizacion = self.request.query_params.get('FechaActualizacion', None)
            Activo = self.request.query_params.get('Activo', None)
            order_direction = self.request.query_params.get('order_direction', 'asc')
            query_params = ['FideicomisoAsociado', 'Primer_Nombre', 'Segundo_Nombre', 'Primer_Apellido', 'Segundo_Apellido', 'TipoActor', 'FideicomisoAsociado', 'FechaActualizacion', 'Activo']
            for param in query_params:
                value = self.request.query_params.get(param, None)
                if value is not None:
                    model_field = param
                    queryset = queryset.filter(**{f'{model_field}__icontains': value})
            if order_by in ['FideicomisoAsociado', 'Primer_Nombre', 'Segundo_Nombre', 'Primer_Apellido', 'Segundo_Apellido', 'TipoActor', 'FideicomisoAsociado', 'FechaActualizacion', 'Activo']:
                    if order_direction == 'desc':
                        order_by = '-' + order_by
                    queryset = queryset.order_by(order_by, 'FideicomisoAsociado')
            return queryset
        except ValidationError as e:
            raise ParseError(detail=str(e))
        except Exception as e:
            raise APIException(detail=str(e))
class ActorDeContratoCreateView(APIView):
    def post(self, request):
        try:
            codigo_sfc = request.data.get('FideicomisoAsociado')
            tipo_actor_id = request.data.get('TipoActor')
            Primer_Nombre = request.data.get('Primer_Nombre')
            Segundo_Nombre = request.data.get('Segundo_Nombre')
            Primer_Apellido = request.data.get('Primer_Apellido')
            Segundo_Apellido = request.data.get('Segundo_Apellido')
            numero_identificacion = request.data.get('NumeroIdentificacion')
            try:
                tipo_documento_instance = TipoDeDocumento.objects.get(TipoDocumento=request.data['TipoIdentificacion'])
            except TipoDeDocumento.DoesNotExist:
                return Response({'status': 'invalid request', 'message': 'TipoDeDocumento no existe'}, status=status.HTTP_400_BAD_REQUEST)
            fideicomiso = Fideicomiso.objects.filter(CodigoSFC=codigo_sfc).first()
            if not fideicomiso:
                return Response({'status': 'invalid request', 'message': 'Fideicomiso no existe'}, status=status.HTTP_400_BAD_REQUEST)

            tipo_actor = TipoActorDeContrato.objects.filter(id=tipo_actor_id).first()
            if not tipo_actor:
                return Response({'status': 'invalid request', 'message': 'TipoActor no existe'}, status=status.HTTP_400_BAD_REQUEST)

            if len(numero_identificacion) > 12:
                return Response({'status': 'invalid request', 'message': 'NumeroIdentificacion debe ser de 12 caracteres o menos'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                actor = ActorDeContrato.objects.create(
                    TipoIdentificacion=tipo_documento_instance,
                    FideicomisoAsociado=fideicomiso,
                    NumeroIdentificacion=numero_identificacion,
                    TipoActor=tipo_actor,
                    Primer_Nombre=Primer_Nombre,
                    Segundo_Nombre=Segundo_Nombre,
                    Primer_Apellido=Primer_Apellido,
                    Segundo_Apellido=Segundo_Apellido,
                    Activo=True,
                    FechaActualizacion=timezone.now()
                )
            except IntegrityError:
                return Response({
                    'status': 'error',
                    'message': 'La relación de NumeroIdentificacion con Fideicomiso ya existe'
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
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
            instance.Primer_Nombre=data['Primer_Nombre']
            instance.Segundo_Nombre=data['Segundo_Nombre']
            instance.Primer_Apellido=data['Primer_Apellido']
            instance.Segundo_Apellido=data['Segundo_Apellido']
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
    
