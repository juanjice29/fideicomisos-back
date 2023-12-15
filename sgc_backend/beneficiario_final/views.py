
from rest_framework import generics
from .serializers import Beneficiario_ReporteSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Beneficiario_Reporte
from xml.etree import ElementTree as ET
from datetime import datetime
from rest_framework.views import APIView

class ClientCreateView(generics.CreateAPIView):
    queryset = Beneficiario_Reporte.objects.all()
    serializer_class = Beneficiario_ReporteSerializer

class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Beneficiario_Reporte.objects.all()
    serializer_class = Beneficiario_ReporteSerializer
    lookup_field = 'client_id'

class ClientsByUserTypeView(generics.ListAPIView):
    serializer_class = Beneficiario_ReporteSerializer

    def get_queryset(self):
        user_type = self.kwargs.get('user_type')
        return Beneficiario_Reporte.objects.filter(user_type=user_type)

class UpdateClientView(APIView):
    def post(self, request, format=None):
        xml_data = ET.fromstring(request.data['xml'])
        product = request.data.get('product')
        period = request.data.get('period', '2023-3')

        for item in xml_data.findall('item'):
            client_id = item.find('niben').text
            tipo_novedad = item.find('tnov').text
            date_create = datetime.strptime(item.find('date_create').text, '%Y-%m-%d')

            is_active = True if tipo_novedad in ['1', '2'] else False

            Beneficiario_Reporte.objects.update_or_create(
                client_id=client_id,
                defaults={
                    'user_type': tipo_novedad,
                    'type_product': product,
                    'date_added': datetime.now(),
                    'date_created': date_create,
                    'period': period,
                    'is_active': is_active
                }
            )
        return Response(status=status.HTTP_200_OK)