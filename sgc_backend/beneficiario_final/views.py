from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import update
from rest_framework.renderers import JSONRenderer
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
import subprocess




class TestTaskView(APIView):
    def get(self, request, *args, **kwargs):
        fondo="14"
        novedades=[1,2,3]  
        #result=test_task.apply_async()        
        #current_period=get_current_period()
        #last_report_period= add_period(current_period,-3)        
        last_report_regs=RPBF_HISTORICO.objects.filter(FONDO=fondo) 
        df_historico=pd.DataFrame.from_records(last_report_regs.values())        
        df_historico["PERIODO_REPORTADO_id"]=df_historico["PERIODO_REPORTADO_id"].apply(lambda x: int("".join(x.split("-"))))
        logger.info("dataframe historico %",df_historico)
        #nov_1=df[df["TIPO_NOVEDAD"]=="1"]
        #nov_2=df[df["TIPO_NOVEDAD"]=="2"]
        #nov_3=df[df["TIPO_NOVEDAD"]=="3"]
        
          
        dsn_tns = cx_Oracle.makedsn('192.168.168.175', '1521', service_name='SIFIVAL')
        conn = cx_Oracle.connect(user='FS_SGC_US', password='fs_sgc_us', dsn=dsn_tns)
        cur = conn.cursor()
        
        sql_delete_candidates="DELETE FROM TEMP_RPBF_CANDIDATES"   
        cur.execute(sql_delete_candidates)
        conn.commit()
        
        saldo= cur.execute(semilla.saldo_fondo.format("2023-12-31",fondo)).fetchone()
        saldo=str(saldo[0]).replace(",",".")             
         
        cur.execute(semilla.query.format(saldo,"2023-12-31",fondo))        
        rows=cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        
        
        df_current = pd.DataFrame(rows, columns=columns)
        result=[]
        for index,row in df_current.iterrows():
            nro_identif=row["NRO_IDENTIF"]            
            filtered_df=df_historico[df_historico["NRO_IDENTIF"]==str(nro_identif)]
            novedad_t="1"
            
            if(len(filtered_df)>0):
                max_index=filtered_df["PERIODO_REPORTADO_id"].idxmax()            
                last_state=filtered_df.loc[max_index]
                
                if(last_state["TIPO_NOVEDAD"]=="1"):
                    novedad_t="2"
                if(last_state["TIPO_NOVEDAD"]=="2"):
                    novedad_t="2"
                if(last_state["TIPO_NOVEDAD"]=="3"):
                    novedad_t="1"     
                                  
                  
                
            else:
                novedad_t="1"                
            result.append((nro_identif,novedad_t,fondo))
            
        sql_insert = "INSERT INTO TEMP_RPBF_CANDIDATES (NRO_IDENTIF, NOVEDAD,FONDO) VALUES (:1, :2, :3)"

        # Ejecutar la sentencia SQL con la lista de registros
        cur.executemany(sql_insert, result)    
        conn.commit()   
        cur.close()
        conn.close()      
        return Response({"status":"200","longitud":len(result)}) 
    
class VerifyDataIntegrityView():
    def get(self, request, *args, **kwargs):
        dsn_tns = cx_Oracle.makedsn('192.168.168.175', '1521', service_name='SIFIVAL')
        conn = cx_Oracle.connect(user='FS_SGC_US', password='fs_sgc_us', dsn=dsn_tns)
        cur = conn.cursor()
        return Response({"status":"200"})

class FillPostalCodeView(APIView):
    def get(self, request, *args, **kwargs):
        engine = create_engine('oracle+cx_oracle://FS_SGC_US:fs_sgc_us@192.168.168.175:1521/?service_name=SIFIVAL')
        sql ="""
        SELECT DIREC_DIREC ID_CLIENTE,CIUD_DEPTO||CIUD_DANE AS ID_CIUDAD_RESIDENCIA,CIUD_DEPTO AS ID_DPTO_RESIDENCIA,'COL' AS ID_PAIS_RESIDENCIA,
        DIREC_DIRECCION AS DIRECCION_RECIDENCIAL,NVL(DIREC_BARRIO,'-') BARRIO_DIR_RESIDENCIAL
        FROM TEMP_RPBF_CANDIDATES 
        INNER JOIN CL_TDIREC D1 ON D1.DIREC_NROIDENT=NRO_IDENTIF
        INNER JOIN (SELECT DIREC_NROIDENT,MAX(DIREC_DIREC) MAX_DIREC FROM CL_TDIREC 
        WHERE DIREC_POSTAL IS NULL AND DIREC_ESTADO='ACT' AND DIREC_TPDIR='RES'  AND DIREC_DIRECCION IS NOT NULL
        GROUP BY DIREC_NROIDENT) D2 ON D1.DIREC_DIREC=D2.MAX_DIREC
        INNER JOIN GE_TCIUD ON DIREC_CIUD=CIUD_CIUD
        INNER JOIN GE_TDEPTO ON DEPTO_DEPTO=CIUD_DEPTO
        INNER JOIN GE_TPAIS ON PAIS_PAIS=DEPTO_PAIS
        """
        df = pd.read_sql(sql, engine)
        df.columns = df.columns.str.upper()
        df = df.astype(str)
        df.to_excel('cod_postal.xlsx', index=False)
        return Response({"status":"200"})
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class RunJarView(APIView):
    renderer_classes = [JSONRenderer]
    def get(self, request, *args, **kwargs):
        result = subprocess.run(['java', '-Dhttp.proxyHost=10.1.5.2', '-Dhttp.proxyPort=80', '-Dhttps.proxyHost=10.1.5.2', '-Dhttps.proxyPort=80', '-jar', 'cp.jar', '-separador', ',', '-entrada', 'cod_postal.xlsx', '-salida', 'salida.csv'], check=True)
        df = pd.read_csv('salida.csv')
        engine = create_engine('oracle+cx_oracle://FS_SGC_US:fs_sgc_us@192.168.168.175:1521/?service_name=SIFIVAL') 
        metadata = MetaData()
        metadata.bind = engine
        cl_tdirec = Table('cl_tdirec', metadata, autoload_with=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        for index, row in df.iterrows():
            logger.info(f"Data Enter cl_tdirec: direc_direc={row['ID_CLIENTE']}, direc_postal={row['CP']}")
            if pd.isnull(row['CP']):
                continue
            stmt = update(cl_tdirec).where(cl_tdirec.c.direc_direc == row['ID_CLIENTE']).values(direc_postal=row['CP'])
            session.execute(stmt)
            logger.info(f"Updated cl_tdirec: direc_direc={row['ID_CLIENTE']}, direc_postal={row['CP']}")
        session.commit()
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
    

        