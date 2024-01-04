
from rest_framework import generics
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