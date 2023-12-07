from django.shortcuts import render
from django.http import JsonResponse
from fidecomisos.models import Fideicomiso
from .forms import UploadFileForm
import pandas as pd
from .models import ActorDeContrato
from rest_framework import viewsets
from .models import ActorDeContrato
from .serializers import ActorDeContratoSerializer

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            data = pd.read_excel(excel_file)
            for index, row in data.iterrows():
                ActorDeContrato.objects.create(
                    TipoIdentificacion=row['TipoIdentificacion'],
                    NumeroIdentificacion=row['NumeroIdentificacion'],
                    Nombre=row['Nombre'],
                    TipoActor=row['TipoActor'],
                    FideicomisoAsociado=row['FideicomisoAsociado'],
                    FechaActualizacion=pd.to_datetime(row['FechaActualizacion'])
                )
            return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'invalid request'}, status=400)
    


class ActorDeContratoViewSet(viewsets.ModelViewSet):
    queryset = ActorDeContrato.objects.all()
    serializer_class = ActorDeContratoSerializer

    def create(self, request, *args, **kwargs):
        fideicomiso_id = request.data.get('FideicomisoAsociado')
        numero_identificacion = request.data.get('NumeroIdentificacion')

        if not Fideicomiso.objects.filter(CodigoSFC=fideicomiso_id).exists():
            return JsonResponse({'status': 'invalid request', 'message': 'Fideicomiso does not exist'}, status=400)

        if len(numero_identificacion) > 12:
            return JsonResponse({'status': 'invalid request', 'message': 'NumeroIdentificacion must be 12 characters or less'}, status=400)

        return super().create(request, *args, **kwargs)