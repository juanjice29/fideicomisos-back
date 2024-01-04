
from rest_framework import generics
from django.db import connection
from .serializers import Beneficiario_ReporteSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Beneficiario_Reporte_Dian, File
from xml.etree import ElementTree as ET
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse
from rest_framework.parsers import MultiPartParser, FormParser
import hashlib
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
class BeneficiarioDianCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Beneficiario_Reporte_Dian.objects.all()
    serializer_class = Beneficiario_ReporteSerializer
class BeneficiarioDianDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Beneficiario_Reporte_Dian.objects.all()
    serializer_class = Beneficiario_ReporteSerializer
    lookup_field = 'Id_Cliente'
class BeneficiarioDianByUserTypeView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = Beneficiario_ReporteSerializer
    def get_queryset(self):
        user_type = self.kwargs.get('Tipo_Novedad')
        return Beneficiario_Reporte_Dian.objects.filter(user_type=user_type)
class UpdateBeneficiarioDianView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        xml_file = request.FILES['xml']  # get the XML file from the request files
        file_content = xml_file.read()  # read the file content
        # calculate the hash of the file content
        file_hash = hashlib.md5(file_content).hexdigest()
        # check if a file with the same hash already exists
        if File.objects.filter(file_hash=file_hash).exists():
            return Response({'error': 'File already exists'}, status=status.HTTP_400_BAD_REQUEST)
        # save the file
        file_name = default_storage.save('uploads/' + xml_file.name, ContentFile(file_content))
        # save the file hash
        File.objects.create(file_name=file_name, file_hash=file_hash)
        # parse the XML file
        xml_data = ET.fromstring(file_content)
        product = request.data.get('product')
        period = request.data.get('period')
        for item in xml_data.findall('item'):
            Id_Cliente = item.find('niben').text
            Tipo_Novedad = item.find('tnov').text
            Fecha_creado = datetime.strptime(item.find('date_create').text, '%Y-%m-%d')

            is_active = True if Tipo_Novedad in ['1', '2'] else False
            id_cliente_set = set()
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
        Beneficiario_Reporte_Dian.objects.exclude(client_id__in=id_cliente_set).delete()    
        return Response(status=status.HTTP_200_OK)
    
class UpdateBeneficiarioReporteDianView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        with connection.cursor() as cursor:
            cursor.execute("""
                sql-here
            """)
            rows = cursor.fetchall()

        for row in rows:
            Id_Cliente = row[0]  # adjust the index based on  SQL query
            Fecha_Creado = datetime.strptime(row[1], '%Y-%m-%d')  # adjust the index and date format based on  SQL query
            Fecha_Añadido = datetime.now()

            # calculate the period based on the current date
            year = Fecha_Añadido.year
            quarter = (Fecha_Añadido.month - 1) // 3 + 1
            Periodo = f'{year}-{quarter}'

            # determine the Tipo_Novedad based on whether the Id_Cliente exists in the last period
            last_period = f'{year}-{quarter - 1 if quarter > 1 else 4}'
            exists_in_last_period = Beneficiario_Reporte_Dian.objects.filter(client_id=Id_Cliente, Periodo=last_period).exists()
            Tipo_Novedad = '2' if exists_in_last_period else '1'

            # determine the Activo based on the Tipo_Novedad
            Activo = Tipo_Novedad != '3'

            Beneficiario_Reporte_Dian.objects.update_or_create(
                client_id=Id_Cliente,
                defaults={
                    'Tipo_Novedad': Tipo_Novedad,
                    'Tipo_Producto': '10',
                    'Fecha_Añadido': Fecha_Añadido,
                    'Fecha_Creado': Fecha_Creado,
                    'Periodo': Periodo,
                    'Activo': Activo
                }
            )

        return Response(status=status.HTTP_200_OK)