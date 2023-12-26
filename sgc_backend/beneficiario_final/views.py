
from rest_framework import generics
from .serializers import Beneficiario_ReporteSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Beneficiario_Reporte_Dian
from xml.etree import ElementTree as ET
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
class ClientCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Beneficiario_Reporte_Dian.objects.all()
    serializer_class = Beneficiario_ReporteSerializer

class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Beneficiario_Reporte_Dian.objects.all()
    serializer_class = Beneficiario_ReporteSerializer
    lookup_field = 'Id_Cliente'

class ClientsByUserTypeView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = Beneficiario_ReporteSerializer

    def get_queryset(self):
        user_type = self.kwargs.get('Tipo_Novedad')
        return Beneficiario_Reporte_Dian.objects.filter(user_type=user_type)

class UpdateClientView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        xml_data = ET.fromstring(request.data['xml'])
        product = request.data.get('product')
        period = request.data.get('period', '2023-3')

        for item in xml_data.findall('item'):
            Id_Cliente = item.find('niben').text
            Tipo_Novedad = item.find('tnov').text
            Fecha_creado = datetime.strptime(item.find('date_create').text, '%Y-%m-%d')

            is_active = True if Tipo_Novedad in ['1', '2'] else False

            Beneficiario_Reporte_Dian.objects.update_or_create(
                client_id=Id_Cliente,
                defaults={
                    'Tipo_Novedad': Tipo_Novedad,
                    'Tipo_Producto': product,
                    'Fecha_Añadido': datetime.now(),
                    'Fecha_Creado': Fecha_creado,
                    'Periodo': period,
                    'Activo': is_active
                }
            )
        return Response(status=status.HTTP_200_OK)