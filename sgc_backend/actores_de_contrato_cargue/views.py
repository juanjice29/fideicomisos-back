from django.shortcuts import render
from django.http import JsonResponse
from fidecomisos.models import Fideicomiso
from .forms import UploadFileForm
import pandas as pd
from .models import ActorDeContrato, TipoActorDeContrato
from rest_framework import viewsets
from .models import ActorDeContrato
from .serializers import ActorDeContratoSerializer
from fidecomisos.models import Encargo
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
    queryset = TipoActorDeContrato.objects.all()
    serializer_class = TipoActorDeContratoSerializer

class ActorDeContratoCreateView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            fideicomiso_id = request.data.get('FideicomisoAsociado')
            tipo_actor_id = request.data.get('TipoActor')
            encargo_id = request.data.get('EncargoAsociado')
            numero_identificacion = request.data.get('NumeroIdentificacion')

            if not Fideicomiso.objects.filter(CodigoSFC=fideicomiso_id).exists():
                return Response({'status': 'invalid request', 'message': 'Fideicomiso does not exist'}, status=status.HTTP_400_BAD_REQUEST)

            if not TipoActorDeContrato.objects.filter(id=tipo_actor_id).exists():
                return Response({'status': 'invalid request', 'message': 'TipoActor does not exist'}, status=status.HTTP_400_BAD_REQUEST)

            encargo = Encargo.objects.filter(id=encargo_id, FideicomisoAsociado=fideicomiso_id).first()
            if not encargo:
                return Response({'status': 'invalid request', 'message': 'Encargo does not exist or is not associated with the provided Fideicomiso'}, status=status.HTTP_400_BAD_REQUEST)

            if len(numero_identificacion) > 12:
                return Response({'status': 'invalid request', 'message': 'NumeroIdentificacion must be 12 characters or less'}, status=status.HTTP_400_BAD_REQUEST)

            actor = ActorDeContrato.objects.create(
                FideicomisoAsociado=fideicomiso_id,
                NumeroIdentificacion=numero_identificacion,
                TipoActor=tipo_actor_id,
                Nombre=encargo.Nombre,
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
            actor = self.get_object()
            fideicomiso_id = request.data.get('FideicomisoAsociado', actor.FideicomisoAsociado)
            tipo_actor_id = request.data.get('TipoActor', actor.TipoActor)
            encargo_id = request.data.get('EncargoAsociado', actor.EncargoAsociado)
            numero_identificacion = request.data.get('NumeroIdentificacion', actor.NumeroIdentificacion)

            if not Fideicomiso.objects.filter(CodigoSFC=fideicomiso_id).exists():
                return Response({'status': 'invalid request', 'message': 'Fideicomiso does not exist'}, status=status.HTTP_400_BAD_REQUEST)

            if not TipoActorDeContrato.objects.filter(id=tipo_actor_id).exists():
                return Response({'status': 'invalid request', 'message': 'TipoActor does not exist'}, status=status.HTTP_400_BAD_REQUEST)

            encargo = Encargo.objects.filter(id=encargo_id, FideicomisoAsociado=fideicomiso_id).first()
            if not encargo:
                return Response({'status': 'invalid request', 'message': 'Encargo does not exist or is not associated with the provided Fideicomiso'}, status=status.HTTP_400_BAD_REQUEST)

            if len(numero_identificacion) > 12:
                return Response({'status': 'invalid request', 'message': 'NumeroIdentificacion must be 12 characters or less'}, status=status.HTTP_400_BAD_REQUEST)

            actor.FideicomisoAsociado = fideicomiso_id
            actor.NumeroIdentificacion = numero_identificacion
            actor.TipoActor = tipo_actor_id
            actor.Nombre = encargo.Nombre
            actor.FechaActualizacion = timezone.now()
            actor.save()

            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ActorDeContratoDeleteView(generics.DestroyAPIView):
    queryset = ActorDeContrato.objects.all()
    lookup_field = 'id'
    
