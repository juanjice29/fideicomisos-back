from django.shortcuts import render
from django.http import JsonResponse
from fidecomisos.models import Fideicomiso
from .forms import UploadFileForm
import pandas as pd
from .models import ActorDeContrato, TipoActorDeContrato
from rest_framework import viewsets
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
                    return JsonResponse({'status': 'error', 'message': f'Fideicomiso {row["FideicomisoAsociado"]} does not exist'}, status=400)

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

class EncargoListView(generics.ListAPIView):
    serializer_class = EncargoSerializer

    def get_queryset(self):
        queryset = Encargo.objects.all().order_by('id')
        codigo_sfc = self.request.query_params.get('CodigoSFC', None)
        if codigo_sfc is not None:
            queryset = queryset.filter(Fideicomiso__CodigoSFC=codigo_sfc)
        return queryset
class TipoActorDeContratoListView(generics.ListAPIView):
    queryset = TipoActorDeContrato.objects.all().order_by('id')
    serializer_class = TipoActorDeContratoSerializer
class ActorDeContratoListView(generics.ListAPIView):
    queryset = ActorDeContrato.objects.all().order_by('id')
    serializer_class = ActorDeContratoSerializer
class ActorDeContratoCreateView(APIView):
    def post(self, request):
        try:
            codigo_sfc = request.data.get('FideicomisoAsociado')
            tipo_actor_id = request.data.get('TipoActor')
            encargo_id = request.data.get('EncargoAsociado')
            Primer_Nombre = request.data.get('Primer_Nombre')
            Segundo_Nombre = request.data.get('Segundo_Nombre')
            Primer_Apellido = request.data.get('Primer_Apellido')
            Segundo_Apellido = request.data.get('Segundo_Apellido')
            numero_identificacion = request.data.get('NumeroIdentificacion')
            try:
                tipo_documento_instance = TipoDeDocumento.objects.get(TipoDocumento=request.data['TipoIdentificacion'])
            except TipoDeDocumento.DoesNotExist:
                return Response({'status': 'invalid request', 'message': 'TipoDeDocumento does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            fideicomiso = Fideicomiso.objects.filter(CodigoSFC=codigo_sfc).first()
            if not fideicomiso:
                return Response({'status': 'invalid request', 'message': 'Fideicomiso does not exist'}, status=status.HTTP_400_BAD_REQUEST)

            tipo_actor = TipoActorDeContrato.objects.filter(id=tipo_actor_id).first()
            if not tipo_actor:
                return Response({'status': 'invalid request', 'message': 'TipoActor does not exist'}, status=status.HTTP_400_BAD_REQUEST)

            encargo = Encargo.objects.filter(id=encargo_id, Fideicomiso=fideicomiso).first()
            if not encargo:
                return Response({'status': 'invalid request', 'message': 'Encargo does not exist or is not associated with the provided Fideicomiso'}, status=status.HTTP_400_BAD_REQUEST)

            if len(numero_identificacion) > 12:
                return Response({'status': 'invalid request', 'message': 'NumeroIdentificacion must be 12 characters or less'}, status=status.HTTP_400_BAD_REQUEST)

            actor = ActorDeContrato.objects.create(
                TipoIdentificacion=tipo_documento_instance,
                FideicomisoAsociado=fideicomiso,
                NumeroIdentificacion=numero_identificacion,
                TipoActor=tipo_actor,
                Primer_Nombre=Primer_Nombre,
                Segundo_Nombre=Segundo_Nombre,
                Primer_Apellido=Primer_Apellido,
                Segundo_Apellido=Segundo_Apellido,
                EncargoAsociado=encargo,
                Activo=True,
                FechaActualizacion=timezone.now()
            )

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
            encargo = Encargo.objects.get(id=data['EncargoAsociado'], Fideicomiso=fideicomiso)

            instance.TipoIdentificacion = tipo_documento_instance
            instance.FideicomisoAsociado = fideicomiso
            instance.NumeroIdentificacion = data['NumeroIdentificacion']
            instance.TipoActor = tipo_actor
            instance.Primer_Nombre=data['Primer_Nombre']
            instance.Segundo_Nombre=data['Segundo_Nombre']
            instance.Primer_Apellido=data['Primer_Apellido']
            instance.Segundo_Apellido=data['Segundo_Apellido']
            instance.EncargoAsociado = encargo
            instance.FechaActualizacion = timezone.now()
            instance.Activo=data['Activo']
            instance.save()

            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        except TipoDeDocumento.DoesNotExist:
            return Response({'status': 'invalid request', 'message': 'TipoDeDocumento does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Fideicomiso.DoesNotExist:
            return Response({'status': 'invalid request', 'message': 'Fideicomiso does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except TipoActorDeContrato.DoesNotExist:
            return Response({'status': 'invalid request', 'message': 'TipoActor does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Encargo.DoesNotExist:
            return Response({'status': 'invalid request', 'message': 'Encargo does not exist or is not associated with the provided Fideicomiso'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class ActorDeContratoDeleteView(generics.DestroyAPIView):
    queryset = ActorDeContrato.objects.all()
    lookup_field = 'id'
    
