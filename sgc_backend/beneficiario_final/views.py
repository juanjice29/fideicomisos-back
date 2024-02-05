
from rest_framework import generics
from django.db import connection
from .serializers import Beneficiario_ReporteSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Beneficiario_Reporte_Dian, File, RPBF_HISTORICO, RPBF_PERIODOS
from xml.etree import ElementTree as ET
from datetime import datetime
from rest_framework.views import APIView, View
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse
from rest_framework.parsers import MultiPartParser, FormParser
import hashlib
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import logging
from .tasks import run_tasks_in_order,test_task
from .utils import *
from .querys import semilla
import cx_Oracle
import pandas as pd


class TestTaskView(APIView):
    def get(self, request, *args, **kwargs):
        result=test_task.apply_async()
        
        current_period=get_current_period()
        last_report_period= add_period(current_period,-3)        
        last_report_regs=RPBF_HISTORICO.objects.filter(PERIODO_REPORTADO=last_report_period) 
        df=pd.DataFrame.from_records(last_report_regs.values())
        
        nov_1=df[df["TIPO_NOVEDAD"]=="1"]
        nov_2=df[df["TIPO_NOVEDAD"]=="2"]
        nov_3=df[df["TIPO_NOVEDAD"]=="3"]
            
        dsn_tns = cx_Oracle.makedsn('192.168.168.175', '1521', service_name='SIFIVAL')
        conn = cx_Oracle.connect(user='VU_SFI', password='VU_SFI', dsn=dsn_tns)
        cur = conn.cursor()     
        cur.execute(semilla.query.format("10000","2023-12-31","12"))        
        rows=cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        cur.close()
        conn.close()
        df_current = pd.DataFrame(rows, columns=columns)
        logger.info("esta es la row",df_current)       
                
        return Response({"status":"200"}) 
    
class RunTasksView(APIView):
    def get(self, request, format=None):
        run_tasks_in_order.apply_async()
        return Response({'status': 'Tasks started'})
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

logger = logging.getLogger(__name__)
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
        product = request.data.get('FONDO')
        period = request.data.get('PERIODO_REPORTADO')
        for item in xml_data.findall('bene'):
            NRO_IDENTIF = item.get('niben')
            Tipo_Novedad = item.get('tnov')
            TIPO_IDENTIF = item.get('tdocben')
            NRO_IDENTIF_set = set()
            period_instance = RPBF_PERIODOS.objects.get(PERIODO=period)
            obj, created = RPBF_HISTORICO.objects.update_or_create(
                NRO_IDENTIF=NRO_IDENTIF,
                defaults={
                    'TIPO_NOVEDAD': Tipo_Novedad,
                    'TIPO_IDENTIF': TIPO_IDENTIF,
                    'FONDO': product,
                    'PERIODO_REPORTADO': period_instance,
                
                }
            )
            if created:
                logger.info(f'Created record with NRO_IDENTIF={NRO_IDENTIF}')
            else:
                logger.info(f'Updated record with NRO_IDENTIF={NRO_IDENTIF}')    
        return Response(status=status.HTTP_200_OK)
    
class UpdateBeneficiarioReporteDianView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        current_period = request.data.get('period')  # get the period from the request data

        # calculate the last period taking into account the year change
        year, quarter = map(int, current_period.split('-'))
        last_period = f'{year - 1 if quarter == 1 else year}-{4 if quarter == 1 else quarter - 1}'

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT TIPO_IDENTIF, NRO_IDENTIF, FONDO FROM RPBF_HISTORICO WHERE PERIODO_REPORTADO = %s AND TIPO_NOVEDAD != '3'
            """, [last_period])
            rows = cursor.fetchall()

        for row in rows:
            TIPO_IDENTIF = row[0]
            NRO_IDENTIF = row[1]
            FONDO = row[2]

            # check if the record exists in the last period
            exists_in_last_period = RPBF_HISTORICO.objects.exclude(TIPO_NOVEDAD='3').filter(TIPO_IDENTIF=TIPO_IDENTIF, NRO_IDENTIF=NRO_IDENTIF, FONDO=FONDO, PERIODO_REPORTADO=last_period).exists()
            TIPO_NOVEDAD = '2' if exists_in_last_period else '1'

            RPBF_HISTORICO.objects.update_or_create(
                TIPO_IDENTIF=TIPO_IDENTIF,
                NRO_IDENTIF=NRO_IDENTIF,
                FONDO=FONDO,
                PERIODO_REPORTADO=current_period,
                defaults={
                    'TIPO_NOVEDAD': TIPO_NOVEDAD,
                }
            )

        # For each record in the last period that doesn't exist in the current period, create a new record with TIPO_NOVEDAD = '3'
        last_period_records = RPBF_HISTORICO.objects.filter(PERIODO_REPORTADO=last_period).exclude(TIPO_NOVEDAD='3')
        for record in last_period_records:
            if not RPBF_HISTORICO.objects.filter(TIPO_IDENTIF=record.TIPO_IDENTIF, NRO_IDENTIF=record.NRO_IDENTIF, FONDO=record.FONDO, PERIODO_REPORTADO=current_period).exists():
                RPBF_HISTORICO.objects.create(
                    TIPO_IDENTIF=record.TIPO_IDENTIF,
                    NRO_IDENTIF=record.NRO_IDENTIF,
                    FONDO=record.FONDO,
                    PERIODO_REPORTADO=current_period,
                    TIPO_NOVEDAD='3'
                )

        return Response(status=status.HTTP_200_OK)
class CheckIntegrityView(View):
    def get(self, request, *args, **kwargs):
        # retrieve all unique periods from the table
        periods = RPBF_HISTORICO.objects.values_list('PERIODO_REPORTADO', flat=True).distinct()

        for current_period in periods:
            # calculate the last period taking into account the year change
            year, quarter = map(int, current_period.split('-'))
            last_period = f'{year - 1 if quarter == 1 else year}-{4 if quarter == 1 else quarter - 1}'

            # retrieve all active records from the last period
            last_period_records = RPBF_HISTORICO.objects.filter(PERIODO_REPORTADO=last_period, Activo=True)

            for record in last_period_records:
                # check if the record exists in the current period
                current_period_record = RPBF_HISTORICO.objects.filter(NRO_IDENTIF=record.NRO_IDENTIF, PERIODO_REPORTADO=current_period,TIPO_IDENTIF=record.TIPO_IDENTIF ).first()

                if current_period_record:
                    # if the record exists in the current period and its type is 2, create a new record with the same data but with the current period
                    if current_period_record.TIPO_NOVEDAD == '2':
                        RPBF_HISTORICO.objects.create(
                            NRO_IDENTIF=record.NRO_IDENTIF,
                            TIPO_IDENTIF=record.TIPO_IDENTIF,
                            TIPO_NOVEDAD='2',
                            FONDO=record.FONDO,
                            PERIODO_REPORTADO=current_period,
                            
                        )
                else:
                    # if the record doesn't exist in the current period, add it to the current period with type 3
                    RPBF_HISTORICO.objects.create(
                        NRO_IDENTIF=record.NRO_IDENTIF,
                        TIPO_IDENTIF=record.TIPO_IDENTIF,
                        TIPO_NOVEDAD='2',
                        FONDO=record.FONDO,
                        PERIODO_REPORTADO=current_period,
                    )

            # for each record in the current period that doesn't exist in the last period, set its type to 1
            current_period_records = RPBF_HISTORICO.objects.filter(Periodo=current_period)
            for record in current_period_records:
                if not RPBF_HISTORICO.objects.filter(client_id=record.client_id, Periodo=last_period).exists():
                    record.Tipo_Novedad = '1'

        # save the changes to the database
        RPBF_HISTORICO.objects.bulk_update(current_period_records, ['Tipo_Novedad'])

        # return a response indicating that the integrity check is complete
        return JsonResponse({'status': 'Integrity check complete'})
    

        